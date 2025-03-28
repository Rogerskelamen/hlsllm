from metagpt.roles import Role
from metagpt.actions import UserRequirement
from metagpt.logs import logger
from metagpt.roles.role import RoleReactMode
from metagpt.schema import Message

from const import (
    IMPLEMENT_FILE_PATH,
    IMPLEMENT_TEST_FILE_PATH,
    IMPLEMENT_TEST_EXE_PATH,
    REFERENCE_FILE_PATH,
)

from nl2c.actions import (
    FixCCode,
    WriteAlgorithmCode,
    DesignIORef,
    WriteTestCase,
    WriteTestCode,
    CompileCCode,
    RunCCode,
)


class CCodeProgrammer(Role):
    name: str = "CCodeProgrammer"
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
            resp = await todo.run(msg.content, fpath=IMPLEMENT_FILE_PATH)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 根据源代码和错误信息修正C代码
        elif isinstance(todo, FixCCode):
            error = self.get_memories(k=1)[0]
            resp = await todo.run(test_file=IMPLEMENT_TEST_FILE_PATH, error=error, fpath=IMPLEMENT_FILE_PATH)  # generate 4 reference
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg


class CTestDesigner(Role):
    name: str = "CTestDesigner"
    profile: str = "c code test designer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([DesignIORef, WriteTestCase])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)
        self._watch([UserRequirement])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 获取自然语言，生成用来测试的输入输出数据参考
        if isinstance(todo, DesignIORef):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(msg.content, REFERENCE_FILE_PATH, k=4)  # generate 4 reference by default
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 根据自然语言描述和测试数据参考，生成测试用例
        elif isinstance(todo, WriteTestCase):
            algo = self.get_memories(k=2)[0]
            ref = self.get_memories(k=1)[0]
            resp = await todo.run(algorithm_desc=algo, reference=ref)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        self.rc.memory.add(msg)
        return msg


class CTestExecutor(Role):
    name: str = "CTestExecutor"
    profile: str = "c code case executor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([WriteTestCase, FixCCode])
        self.set_actions([WriteTestCode, CompileCCode, RunCCode])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 整合assertion测试用例代码和算法实现代码
        if isinstance(todo, WriteTestCode):
            for memory in self.get_memories():
                if memory.cause_by == "nl2c.actions.WriteTestCase":
                    test = memory.content
            resp = await todo.run(file=IMPLEMENT_FILE_PATH, test=test, fpath=IMPLEMENT_TEST_FILE_PATH)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 编译测试代码
        elif isinstance(todo, CompileCCode):
            resp = await todo.run(IMPLEMENT_TEST_FILE_PATH, IMPLEMENT_TEST_EXE_PATH)  # compile result
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 运行测试代码
        elif isinstance(todo, RunCCode):
            resp = await todo.run(IMPLEMENT_TEST_EXE_PATH)  # runtime result
            compile_error = self.get_memories(k=1)[0].content
            resp += compile_error

            if not resp:
                logger.info(f"{self._setting}: algorithm code test passed!")
                msg = Message(content="algorithm code test passed!", role=self.profile, cause_by=type(todo))
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="CCodeProgrammer")

        self.rc.memory.add(msg)
        return msg

