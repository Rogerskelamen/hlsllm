import subprocess
from metagpt.actions import UserRequirement
from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message

from config import DataConfig
from const import LOOP_SOLUTION_NAME
from hls.actions import FixHLSOpt
from opt.actions.loop import ApplyLoopStrategy
from opt.actions.pragma import ApplyOpt, ChooseOpt
from opt.actions.preprocess import PreprocessHLSCode
from utils import build_with_other_solution, parse_opt_list, write_file


class HLSHardNormalizer(Role):
    name: str = "HLSHardNormalizer"
    profile: str = "normalize HLS code in hardware thinking"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([PreprocessHLSCode])
        self._watch([UserRequirement])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo
        await todo.run(DataConfig().src_file)

        msg = Message(content="Preprocess work done", role=self.profile, cause_by=type(todo), send_to="HLSBuildAssistant")
        return msg


class HLSPerfAnalyzer(Role):
    name: str = "HLSPerfAnalyzer"
    profile: str = "hls performance analyzer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ChooseOpt, ApplyOpt, FixHLSOpt])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "hls.actions.CosimHLSCode":
            self._set_state(self.find_state("ChooseOpt"))

        elif msg.cause_by == "hls.actions.ChooseOpt":
            self._set_state(self.find_state("ApplyOpt"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 选择优化策略
        if isinstance(todo, ChooseOpt):
            resp = await todo.run(DataConfig().src_file)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo), send_to="HLSPerfAnalyzer")

        # 应用优化策略
        elif isinstance(todo, ApplyOpt):
            context = self.get_memories(k=1)[0]
            opt_list = parse_opt_list(context.content)
            resp = await todo.run(
                DataConfig().src_file,
                DataConfig().head_file,
                opt_list,
                DataConfig().hls_src
            )
            logger.info(f"{self._setting}: Apply all suitable optimizations")
            msg = Message(content="Apply all suitable optimizations", role=self.profile, cause_by=type(todo), send_to="HLSBuildAssistant")

        return msg


class HLSCodeReviewer(Role):
    name: str = "HLSCodeReviewer"
    profile: str = "review hls code then change code structure to improve performance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ApplyLoopStrategy])
        self._watch([])

    async def _think(self) -> bool:
        msg = self.get_memories(k=1)[0]

        if msg.cause_by == "hls.actions.CosimHLSCode":
            self._set_state(self.find_state("ApplyLoopStrategy"))

        else:
            self._set_state(-1)
            logger.info(f"{self._setting}: can't find an action to handle message [{msg.content}]")
            raise ValueError(f"Unexpected message: {msg}")

        return True


    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.todo}({self.todo.name})")
        todo = self.rc.todo

        # 应用内部循环的结构性优化
        if isinstance(todo, ApplyLoopStrategy):
            resp = await todo.run(DataConfig().src_file, DataConfig().desc_file)
            cmd = [
                "mv",
                DataConfig().src_file,
                DataConfig().get_origin_src_file()
            ]
            subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            # save loop optimization code
            write_file(resp, DataConfig().src_file)
            # change build.tcl(mainly solution name)
            build_with_other_solution(LOOP_SOLUTION_NAME)
            msg = Message(content=resp, role=self.profile, cause_by=type(todo))

        return msg

