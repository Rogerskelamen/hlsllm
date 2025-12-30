from metagpt.actions import Action

from const import LOOP_STRATS
from utils import parse_code, read_file

class ApplyLoopStrategy(Action):
    name: str = "ApplyLoopStrategy"

    COMMON_PROMPT: str = """
    You are a hardware expert specializing in Xilinx Vitis HLS, with deep knowledge about HLS code optimization.

    [Task]
    Given the HLS source code with a suboptimal loop structure, along with its algorithm description and a list of potential loop optimization strategies, identify which strategies are applicable to the code. Then apply the selected strategies to the HLS source code to improve its performance.

    [HLS Code]
    {code_content}

    [Algorithm Description]
    {algorithm_desc}

    [Loop Optimization Strategy]
    {loop_strategy}

    [Instructions]
    Let's think step by step.
    Firstly, carefully read and understand all the loop optimization strategies provided in the list.
    Then, analyze the given HLS code to determine which strategies are applicable, while ensuring that the optimized code remains functionally equivalent to the original algorithm description.
    Finally, apply the selected optimization strategies to the code by restructuring loops.

    [Requirements]
    - If none of the strategy is suitable, DON'T apply any optimization.
    - ONLY modify the structure of loops where appropriate.
    - Do NOT alter the core functionality or logic of the source code.
    - Return ```cpp your_code_here``` without any explanation.
    """

    async def run(self, code_file: str, algo_desc: str):
        code = read_file(code_file)
        desc = read_file(algo_desc)
        loop_strategy = ""
        for strat in LOOP_STRATS:
            strat_name = f"{strat}_DESC"
            strat_intro = globals()[strat_name]
            loop_strategy += strat_intro
        prompt = self.COMMON_PROMPT.format(
            code_content=code,
            algorithm_desc=desc,
            loop_strategy=loop_strategy
        )
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        return code_text

