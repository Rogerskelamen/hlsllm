from metagpt.roles import Role
from metagpt.actions import UserRequirement
from metagpt.logs import logger
from metagpt.roles.role import RoleReactMode
from metagpt.schema import Message

import config
from const import (
    IMPLEMENT_FILE_PATH,
    IMPLEMENT_TEST_FILE_PATH,
    IMPLEMENT_TEST_EXE_PATH,
    BUILD_ALGO_DIR,
    BUILD_EXE_ELF_PATH,
)

from nl2c.actions import (
    FixCCode,
    FixCompileErr,
    WriteAlgorithmCode,
    CompileCCode,
    RunCCode,
)


class CodeProgrammer(Role):
    name: str = "CodeProgrammer"
    profile: str = "c code programmer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteAlgorithmCode, FixCompileErr, FixCCode])
        self._watch([UserRequirement])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.role == "Human":
            self._set_state(self.find_state("WriteAlgorithmCode"))

        elif msg.cause_by == "nl2c.actions.CompileCCode":
            self._set_state(self.find_state("FixCompileErr"))

        elif msg.cause_by == "nl2c.actions.RunCCode":
            self._set_state(self.find_state("FixCCode"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 获取自然语言表示，生成C代码
        if isinstance(todo, WriteAlgorithmCode):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(msg.content, config.head_file, fpath=config.src_file)

        # 根据源码和编译错误信息修正代码
        elif isinstance(todo, FixCompileErr):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(msg.content, config.src_file)

        # 根据源代码和运行错误信息修正代码
        elif isinstance(todo, FixCCode):
            error = self.get_memories(k=1)[0]
            resp = await todo.run(error=error, desc_file=config.desc_file, src_file=config.src_file)

        msg = Message(content=resp, role=self.profile, cause_by=type(todo))
        return msg



class CTestExecutor(Role):
    """
    To execute generated source + header + testbench code, includes two actions:
    1. compile those files
    2. run the runnable ELF
    """

    name: str = "CTestExecutor"
    profile: str = "c test code executor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([WriteAlgorithmCode, FixCompileErr, FixCCode])
        self.set_actions([CompileCCode, RunCCode])


    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by in {"nl2c.actions.WriteAlgorithmCode", "nl2c.actions.FixCompileErr"}:
            self._set_state(self.find_state("CompileCCode"))

        elif msg.cause_by in {"nl2c.actions.CompileCCode", "nl2c.actions.FixCCode"}:
            self._set_state(self.find_state("RunCCode"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")
        return True


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 编译测试代码
        if isinstance(todo, CompileCCode):
            [retcode, resp] = await todo.run(
                [
                    config.src_file,
                    config.tb_file
                ],
                BUILD_EXE_ELF_PATH
            )  # compile result

            # 程序通过编译
            if retcode == 0:
                logger.info(f"{self._setting}: code compilation succeed!")
                msg = Message(content="code compilation succeed!", role=self.profile, cause_by=type(todo), send_to="CTestExecutor")

            # 编译不通过，返回给Programmer
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="CCodeProgrammer")


        # 运行测试代码
        elif isinstance(todo, RunCCode):
            [retcode, resp] = await todo.run(BUILD_EXE_ELF_PATH, BUILD_ALGO_DIR)  # runtime result

            # 程序运行通过
            if retcode == 0:
                logger.info(f"{self._setting}: algorithm code passed!")
                msg = Message(content="algorithm code passed!", role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

            # 测试未通过，返回给Programmer
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="CCodeProgrammer")

        # self.rc.memory.add(msg)
        return msg

