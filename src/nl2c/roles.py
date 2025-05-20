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
    TARGET_EXE_ELF_PATH,
)

from nl2c.actions import (
    FixCCode,
    WriteAlgorithmCode,
    CompileCCode,
    RunCCode,
)


class CodeProgrammer(Role):
    name: str = "CodeProgrammer"
    profile: str = "c code programmer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteAlgorithmCode, FixCCode])
        self._watch([UserRequirement])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.role == "Human":
            self._set_state(self.find_state("WriteAlgorithmCode"))

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
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 根据源代码和错误信息修正C代码
        elif isinstance(todo, FixCCode):
            error = self.get_memories(k=1)[0]
            resp = await todo.run(test_file=IMPLEMENT_TEST_FILE_PATH, error=error, fpath=IMPLEMENT_FILE_PATH)  # generate 4 reference
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg


"""
To execute generated source + header + testbench code, includes two actions:
1. compile those files
2. run the runnable ELF
"""
class CTestExecutor(Role):
    name: str = "CTestExecutor"
    profile: str = "c code case executor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([WriteAlgorithmCode, FixCCode])
        self.set_actions([CompileCCode, RunCCode])
        # self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 编译测试代码
        if isinstance(todo, CompileCCode):
            resp = await todo.run(
                [
                    config.src_file,
                    config.head_file,
                    config.tb_file
                ],
                IMPLEMENT_TEST_EXE_PATH
            )  # compile result
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 运行测试代码
        elif isinstance(todo, RunCCode):
            resp = await todo.run(IMPLEMENT_TEST_EXE_PATH)  # runtime result
            compile_error = self.get_memories(k=1)[0].content
            resp += compile_error

            # 测试程序编译和运行通过
            if not resp:
                logger.info(f"{self._setting}: algorithm code tests all passed!")
                msg = Message(content="algorithm code tests all passed!", role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

            # 测试未通过，返回给Programmer
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="CCodeProgrammer")

        self.rc.memory.add(msg)
        return msg

