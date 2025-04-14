from metagpt.actions import Action
from metagpt.logs import logger

from utils import read_file

class CheckHLSSpec(Action):
    name: str = "CheckHLSSpec"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given a C code snippet, analyze it for compliance with Vitis HLS synthesis standards and provide constructive feedback on any non-compliant syntax or potential issues.
    - Identify parts of the code that may cause synthesis issues or inefficiencies.
    - Suggest necessary modifications to ensure compatibility with Vitis HLS.
    C algorithm code: {code}
    """

    async def run(self, file: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await self._aask(prompt)
        return rsp
