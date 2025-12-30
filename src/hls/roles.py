import subprocess
from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message

from config import DataConfig
from hls.actions import (
    SynthHLSCode,
    CosimHLSCode,
    RepairHLSCode,
    FixHLSCode,
    FixHLSOpt,
)
from opt.actions.loop import ApplyLoopStrategy
from opt.actions.pragma import ApplyOpt
from opt.actions.preprocess import PreprocessHLSCode
from utils import report_output, synth_tcl_gen


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
            resp = await todo.run(DataConfig().src_file, msg.content)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        elif isinstance(todo, FixHLSCode):
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(DataConfig().src_file, msg.content)
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
        self.set_actions([SynthHLSCode, CosimHLSCode])
        self._watch([
            RepairHLSCode,
            FixHLSCode,
            PreprocessHLSCode,
            ApplyLoopStrategy,
            ApplyOpt,
            FixHLSOpt,
        ])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by in ("nl2c.actions.RunCCode", "hls.actions.RepairHLSCode"):
            self._set_state(self.find_state("SynthHLSCode"))

        elif msg.cause_by in (
                "hls.actions.SynthHLSCode",
                "hls.actions.FixHLSCode",
                "opt.actions.preprocess.PreprocessHLSCode",
                "opt.actions.loop.ApplyLoopStrategy",
                "opt.actions.pragma.ApplyOpt",
            ):
            self._set_state(self.find_state("CosimHLSCode"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]

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
            # 第一次协同仿真测试
            if msg.cause_by == "hls.actions.SynthHLSCode":
                resp = await todo.run()
                # HLS协同仿真成功
                if not resp:
                    logger.info(f"{self._setting}: HLS C/RTL Cosimulation passed!")
                    msg = Message(
                        content="HLS C/RTL Cosimulation passed!",
                        role=self.profile,
                        cause_by=type(todo),
                        # send_to="HLSPerfAnalyzer",
                        # send_to="HLSCodeReviewer",
                    )
                    ###
                    #### 保存协同仿真成功的数据集
                    ###
                    result = subprocess.run(
                        ["cp", DataConfig().src_file, "out"],
                        capture_output=True, text=True
                    )

                # 协同仿真失败
                else:
                    msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSEngineer")

            # 预处理优化完成后的第二次协同仿真
            elif msg.cause_by == "opt.actions.preprocess.PreprocessHLSCode":
                resp = await todo.run()
                # HLS协同仿真成功
                if not resp:
                    logger.info(f"{self._setting}: HLS C/RTL Cosimulation passed!")
                    msg = Message(
                        content="HLS C/RTL Cosimulation passed!",
                        role=self.profile,
                        cause_by=type(todo),
                    )

            # Loop优化完成后第三次协同仿真
            elif msg.cause_by == "opt.actions.loop.ApplyLoopStrategy":
                resp = await todo.run()
                # HLS协同仿真成功
                if not resp:
                    logger.info(f"{self._setting}: HLS C/RTL Cosimulation passed!")
                    msg = Message(
                        content="HLS C/RTL Cosimulation passed!",
                        role=self.profile,
                        cause_by=type(todo),
                    )
                    report_output()  # output Synthesis report to a certain file to compare

            else:
                raise ValueError(f"Unexpected message sender {msg.cause_by}")

        return msg

