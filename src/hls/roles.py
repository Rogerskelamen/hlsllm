from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message

from const import (
    HLS_PROJECT_NAME,
    HLS_SRC_CODE_FILE,
    HLS_TCL_FILE,
    IMPLEMENT_FILE_PATH,
    SYNTH_TARGET_PART,
    TOP_FUNCTION_FILE,
)

from hls.actions import FixHLSCode, OptimizeHLSPerf, RepairHLSCode, SynthHLSCode
from utils import read_file


class HLSEngineer(Role):
    name: str = "HLSEngineer"
    profile: str = "Vitis HLS engineer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([RepairHLSCode, FixHLSCode])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "nl2c.actions.RunCCode":
            self._set_state(self.find_state("RepairHLSCode"))

        elif msg.cause_by == "hls.actions.SynthHLSCode":
            self._set_state(self.find_state("FixHLSCode"))

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

        elif isinstance(todo, FixHLSCode):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(HLS_SRC_CODE_FILE, msg)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg


class HLSToolAssistant(Role):
    name: str = "HLSToolHelper"
    profile: str = "Vitis HLS tool assistant"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SynthHLSCode])
        self._watch([RepairHLSCode, FixHLSCode])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "hls.actions.RepairHLSCode" or "hls.actions.FixHLSCode":
            self._set_state(self.find_state("SynthHLSCode"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        if isinstance(todo, SynthHLSCode):
            top_func = read_file(TOP_FUNCTION_FILE)
            resp = await todo.run(
                proj_name=HLS_PROJECT_NAME,
                top_func=top_func,
                src_file=HLS_SRC_CODE_FILE,
                part=SYNTH_TARGET_PART,
                tcl_file=HLS_TCL_FILE
            )

            # HLS代码综合成功
            if not resp:
                logger.info(f"{self._setting}: hls source file successfully synthesised!")
                msg = Message(content="hls source file successfully synthesised!", role=self.profile, cause_by=type(todo), send_to="")

            # 综合失败
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

        return msg


class HLSPerfAnalyzer(Role):
    name: str = "HLSPerfAnalyzer"
    profile: str = "hls performance analyzer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_action([OptimizeHLSPerf])
        self._watch([])
