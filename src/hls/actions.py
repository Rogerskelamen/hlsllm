from metagpt.actions import Action
from metagpt.logs import logger

from hls.rag import RAGCodeStyle
from utils import parse_code, read_file, write_file


class CheckHLSSpec(Action):
    name: str = "CheckHLSSpec"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given the following C/C++ algorithm code intended for HLS synthesis, analyze its structure and syntax specifically for synthesizability.
    - Identify any parts of the code that are not synthesizable by Vitis HLS (e.g., unsupported constructs, improper use of pointers, dynamic memory allocation, recursion, or unsupported library functions).
    - Explain clearly why each issue would cause synthesis to fail.
    - Suggest precise modifications or alternatives to make the code synthesizable while preserving its intended functionality.
    C/C++ algorithm code: {code}
    """

    async def run(self, file: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        return rsp


class RepairHLSCode(Action):
    name: str = "RepairHLSCode"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given the following C/C++ algorithm code, modify it as needed to ensure it is fully synthesizable using Vitis HLS, in strict compliance with HLS synthesis standards.
    - Fix any non-synthesizable constructs.
    - Replace unsupported operations or patterns.
    - Preserve the original functionality as much as possible.
    Output only the corrected C/C++ code. Do not include any explanation.
    C/C++ algorithm code: {code}
    """

    async def run(self, file: str, out: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, out)
        return code_text


class SynthHLSCode(Action):
    name: str = "SynthHLSCode"


