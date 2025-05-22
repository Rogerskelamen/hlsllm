import subprocess
from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message

import config

from const import (
    HLS_OPT_CODE_FILE,
    HLS_OPT_PROJECT_NAME,
    HLS_SRC_CODE_FILE,
    HLS_TCL_FILE,
    SYNTH_TARGET_PART,
)

from hls.actions import (
    CosimHLSCode,
    FixHLSCode,
    FixHLSOpt,
    OptimizeHLSPerf,
    RepairHLSCode,
    SynthHLSCode,
    SynthHLSOpt
)
from utils import synth_tcl_gen


"""
This agent is a HLS expert,
focused on repairing HLS code to ensure synthesizability and
applying optimization techniques to improve hardware performance
"""
class HLSEngineer(Role):
    name: str = "HLSEngineer"
    profile: str = "Vitis HLS engineer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([RepairHLSCode, FixHLSCode])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "hls.actions.SynthHLSCode":
            self._set_state(self.find_state("RepairHLSCode"))

        elif msg.cause_by == "hls.actions.CosimHLSCode":
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
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(config.src_file, msg.content)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        elif isinstance(todo, FixHLSCode):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(config.src_file, msg.content)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg



"""
This agent assists in building HLS project by TCL scripts,
focusing on managing automatical steps and
ensuring the entire process runs as smoothly as possible.
"""
class HLSBuildAssistant(Role):
    name: str = "HLSBuildAssistant"
    profile: str = "Vitis HLS building assistant"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SynthHLSCode, CosimHLSCode, SynthHLSOpt])
        self._watch([RepairHLSCode, FixHLSCode, OptimizeHLSPerf, FixHLSOpt])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by in ("nl2c.actions.RunCCode", "hls.actions.RepairHLSCode"):
            self._set_state(self.find_state("SynthHLSCode"))

        elif msg.cause_by == "hls.actions.SynthHLSCode":
            self._set_state(self.find_state("CosimHLSCode"))

        elif msg.cause_by in ("hls.actions.OptimizeHLSPerf", "hls.actions.FixHLSOpt"):
            self._set_state(self.find_state("SynthHLSOpt"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        if isinstance(todo, SynthHLSCode):
            synth_tcl_gen()
            resp = await todo.run()

            # HLS代码综合成功
            if not resp:
                logger.info(f"{self._setting}: HLS C Synthesis succeed!")
                msg = Message(
                    content="HLS C Synthesis succeed!",
                    role=self.profile,
                    cause_by=type(todo),
                    send_to="HLSBuildAssistant"
                )

            # 综合失败
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

        elif isinstance(todo, CosimHLSCode):
            resp = await todo.run()

            # HLS协同仿真成功
            if not resp:
                logger.info(f"{self._setting}: HLS C/RTL Cosimulation passed!")
                msg = Message(
                    content="HLS C/RTL Cosimulation passed!",
                    role=self.profile,
                    cause_by=type(todo),
                )
                result = subprocess.run(
                    ["cp", config.src_file, "out"],
                    capture_output=True, text=True
                )

            # 协同仿真失败
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

        # 优化HLS代码综合
        elif isinstance(todo, SynthHLSOpt):
            resp = await todo.run(
                proj_name=HLS_OPT_PROJECT_NAME,
                top_func=TOP_FUNCTION_FILE,
                src_file=HLS_OPT_CODE_FILE,
                part=SYNTH_TARGET_PART,
                tcl_file=HLS_TCL_FILE
            )

            # HLS代码综合成功
            if not resp:
                logger.info(f"{self._setting}: hls source file successfully synthesised!")
                msg = Message(content="hls source file successfully synthesised!", role=self.profile, cause_by=type(todo))

            # 综合失败
            else:
                msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSPerfAnalyzer")

        return msg


class HLSPerfAnalyzer(Role):
    name: str = "HLSPerfAnalyzer"
    profile: str = "hls performance analyzer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([OptimizeHLSPerf, FixHLSOpt])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "hls.actions.SynthHLSCode":
            self._set_state(self.find_state("OptimizeHLSPerf"))

        elif msg.cause_by == "hls.actions.SynthHLSOpt":
            self._set_state(self.find_state("FixHLSOpt"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 优化HLS代码
        if isinstance(todo, OptimizeHLSPerf):
            resp = await todo.run(HLS_SRC_CODE_FILE, HLS_OPT_CODE_FILE)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        # 优化的HLS代码综合失败，进行修复步骤
        elif isinstance(todo, FixHLSOpt):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(HLS_OPT_CODE_FILE, msg)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg
