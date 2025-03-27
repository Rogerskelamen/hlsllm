import sys

from metagpt.roles import Role
from metagpt.actions import UserRequirement
from metagpt.logs import logger
from metagpt.roles.role import RoleReactMode
from metagpt.schema import Message

from actions import (
    FixCCode,
    WriteAlgorithm,
    WriteTestCase,
    GenerateIORef,
    CompileCCode,
    RunCCode,
)


class AlgorithmWriter(Role):
    name: str = "AlgorithmWriter"
    profile: str = "algorithm writer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteAlgorithm, FixCCode])
        self._watch([UserRequirement])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]
        logger.info(f"msg.cause_by: {msg.cause_by}, msg.send_to: {msg.send_to}")

        if msg.role == "Human":
            self._set_state(self.find_state("WriteAlgorithm"))

        elif msg.cause_by == "actions.RunCCode":
            self._set_state(self.find_state("FixCCode"))

        else:
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            self._set_state(-1)
            raise ValueError(f"Unexpected message: {msg}")

        return True


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        # 获取自然语言表示，生成C代码
        if isinstance(todo, WriteAlgorithm):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(msg.content)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 根据源代码和错误信息修正C代码
        elif isinstance(todo, FixCCode):
            error = self.get_memories(k=1)[0]
            resp = await todo.run(file=sys.path[0] + "/impl/impl.c", error=error)  # generate 4 reference
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg


class IORefGenerator(Role):
    name: str = "IORefGenerator"
    profile: str = "io reference generator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateIORef])
        self._watch([WriteAlgorithm])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")

        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        resp = await todo.run(msg.content, k=4)  # generate 4 reference
        msg = Message(content=resp, role=self.profile, cause_by=type(todo))
        return msg


class TestCaseWriter(Role):
    name: str = "TestCaseWriter"
    profile: str = "test case writer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([GenerateIORef])
        self.set_actions([WriteTestCase, CompileCCode, RunCCode])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")

        todo = self.rc.todo
        if isinstance(todo, WriteTestCase):
            code = self.get_memories(k=2)[0].content  # last 2 message
            ref = self.get_memories(k=1)[0].content  # last 1 message
            resp = await todo.run(code=code, reference=ref, fpath=sys.path[0] + "/impl/impl.c")
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        elif isinstance(todo, CompileCCode):
            resp = await todo.run(sys.path[0] + "/impl/impl.c", sys.path[0] + "/impl/impl")
            if not resp:
                msg = Message(content="algorithm code test passed!", role=self.profile, cause_by=type(todo))
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        elif isinstance(todo, RunCCode):
            resp = await todo.run(sys.path[0] + "/impl/impl")
            if not resp:
                msg = Message(content="algorithm code test passed!", role=self.profile, cause_by=type(todo))
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="AlgorithmWriter")

        # logger.info(type(todo))

        return msg

