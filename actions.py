from metagpt.actions import Action
from metagpt.logs import logger

from utils import parse_code

class WriteAlgorithm(Action):
    COMMON_TEMPLATE: str = """
    Based on the following natural language description of an algorithm, write a complete C language implementation.
    The code should include only the function implementation without a main function or test code.
    Algorithm description: {algorithm_desc}
    """

    FULL_PROMPT: str = COMMON_TEMPLATE + """
    Output format requirements:
    1. Implement only the function corresponding to the given algorithm, without a main function or test code.
    2. Include neccessary `#include` directives **only if the implementation uses standard library functions**. DO NOT include unnecessary headers.
    3. Add clear comments explaining key parts of the implementation.
    4. Ensure the code follows C programming best practices, making it reusable and readable
    5. Only code is allowd in output
    """

    async def run(self, algorithm_desc: str):
        prompt = self.FULL_PROMPT.format(algorithm_desc=algorithm_desc)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)

        return code_text

