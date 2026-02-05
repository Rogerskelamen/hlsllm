from metagpt.actions import Action

from prompt.preprocess import *
from utils import parse_code, read_file, write_file

class PreprocessHLSCode(Action):
    name: str = "PreprocessHLSCode"

    COMMON_PROMPT: str = """
    Act as a senior HLS hardware engineer and compiler-oriented code transformation expert. Your task is to preprocess input C/C++ HLS source code by applying HLS-friendly structural transformations.
    The goal is not to optimize performance with pragmas, but to rewrite the source code into a canonical, predictable, and synthesis-friendly form suitable for downstream HLS optimizations such as pipelining, dataflow, and bit-width refinement.

    Given the input HLS source code provided below, rewrite the code by applying a defined sequence of HLS-friendly structural transformations. All transformations must preserve functional correctness and synthesizability. Output ONLY the rewritten C++ code.
    {hls_code}

    Apply the following preprocessing strategies sequentially, and only within the scope defined by each strategy:
    {preprocess_strategy}

    [Requirements]
    - If none of the strategy is suitable, DON'T apply any optimization.
    - Return ```cpp your_code_here``` without any explanation.
    """

    async def run(self, src_file: str):
        code = read_file(src_file)
        strategies = STATIC_INTERN_ARRAY + \
                     HLS_INTRINSIC_FUNCTION + \
                     CONTROL_FLOW_CANONICAL + \
                     MEMORY_ACCESS_LINEAR
        prompt = self.COMMON_PROMPT.format(hls_code=code, preprocess_strategy=strategies)
        rsp = await self._aask(prompt)
        opt_code = parse_code(rsp)
        write_file(opt_code, src_file)
        return opt_code

