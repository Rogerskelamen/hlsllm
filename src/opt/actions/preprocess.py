from metagpt.actions import Action

from utils import parse_code, read_file, write_file
from prompt.preprocess import *

class PreprocessHLSCode(Action):
    name: str = "PreprocessHLSCode"

    COMMON_PROMPT: str = """
    Act as a senior HLS hardware engineer and compiler-oriented code transformation expert. Your task is to preprocess input C/C++ HLS source code by applying HLS-friendly structural transformations.
    The goal is not to optimize performance with pragmas, but to rewrite the source code into a canonical, predictable, and synthesis-friendly form suitable for downstream HLS optimizations such as pipelining, dataflow, and bit-width refinement.

    Given the input HLS source code provided below, rewrite the code by applying a defined sequence of HLS-friendly structural transformations. All transformations must preserve functional correctness and synthesizability. Output ONLY the rewritten C/C++ code.
    {hls_code}

    Apply the following preprocessing strategies sequentially, and only within the scope defined by each strategy:
    """

    async def run(self, src_file: str):
        code = read_file(src_file)
        prompt = self.COMMON_PROMPT.format(hls_code=code)
        prompt += STATIC_INTERN_ARRAY + \
                  HLS_INTRINSIC_FUNCTION + \
                  CONTROL_FLOW_CANONICAL + \
                  MEMORY_ACCESS_LINEAR
        rsp = await self._aask(prompt)
        opt_code = parse_code(rsp)
        write_file(opt_code, src_file)
        return opt_code

