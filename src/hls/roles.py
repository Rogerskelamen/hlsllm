from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message

from const import HLS_SRC_CODE_FILE, IMPLEMENT_FILE_PATH
from hls.actions import RepairHLSCode


class HLSEngineer(Role):
    name: str = "HLSEngineer"
    profile: str = "Vitis HLS engineer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([RepairHLSCode])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "nl2c.actions.RunCCode":
            self._set_state(self.find_state("RepairHLSCode"))
        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        if isinstance(todo, RepairHLSCode):
            resp = await todo.run(IMPLEMENT_FILE_PATH, HLS_SRC_CODE_FILE)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg


class HLSToolAssistant(Role):
    name: str = "HLSToolHelper"
    profile: str = "Vitis HLS tool assistant"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions()


class HLSPerfAnalyzer(Role):
    name: str = "HLSPerfAnalyzer"
    profile: str = "hls performance analyzer"
