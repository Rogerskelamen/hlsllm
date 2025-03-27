import sys
import subprocess

from metagpt.actions import Action
from metagpt.logs import logger

from utils import (
    parse_code,
    read_file,
    write_file
)

class WriteAlgorithm(Action):
    name: str = "WriteAlgorithm"

    COMMON_PROMPT: str = """
    Based on the following natural language description of an algorithm, write a complete C language implementation.
    The code should include only the function implementation without a main function or test code.
    Algorithm description: {algorithm_desc}
    """

    FULL_PROMPT: str = COMMON_PROMPT + """
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



class GenerateIORef(Action):
    name: str = "GenerateIORef"

    COMMON_PROMPT: str = """
    You are a C programming expert, please generate {k} sets of structured input-output reference data from the following C algorithm implementation.
    Each input-output reference should be presented in the following structure:
    arg1: [<value1>, <value2>, ...], arg2: [<value1>, <value2>, ...], ..., reference_out: [<expected output values>]
    """

    FULL_PROMPT: str = COMMON_PROMPT + """
    Make sure:
    - The input values should be representative edge cases and typical cases.
    - The output should be consistent with the function’s expected behavior.
    - The format strictly follows the given structure.
    C algorithm implementation: {algorithm_code}
    """

    async def run(self, algorithm_code: str, k: int = 3):
        prompt = self.FULL_PROMPT.format(algorithm_code=algorithm_code, k=k)
        rsp = await self._aask(prompt)
        return rsp



class WriteTestCase(Action):
    name: str = "WriteTestCase"

    COMMON_PROMPT: str = """
    You are a C programming expert, please according to the following C algorithm implementation and input-output reference data, write test cases using `assert` function to verify its correctness.

    Requirements:
    - Return ```c your_code_here```, NO other text
    - Include the given C algorithm implementation so the test cases are runnable.
    - Ensure all test cases match the provided input-output reference data.
    algorithem code: {code}
    input-output reference: {reference}
    """

    async def run(self, code: str, reference: str, fpath: str):
        prompt = self.COMMON_PROMPT.format(code=code, reference=reference)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, fpath)
        return code_text


class CompileCCode(Action):
    name: str = "CompileCCode"
    async def run(self, src: str, out: str):
        compile_result = subprocess.run(["gcc", src, "-o", out], capture_output=True, text=True)
        error_result = compile_result.stderr
        logger.info(f"error_result:\n{error_result}")
        return error_result


class RunCCode(Action):
    name: str = "RunCCode"
    async def run(self, file: str):
        result = subprocess.run([file], capture_output=True, text=True)
        error_result = result.stderr
        logger.info(f"error_result:\n{error_result}")
        return error_result


class FixCCode(Action):
    name: str = "FixCCode"

    COMMON_PROMPT: str = """
    You are a C programming expert, fix the following C code according to it's runtime error message while preserving the original logic. Provide only the corrected version of the code without additional explanations.
    C source code: {code}
    Error message: {error}
    """

    async def run(self, file: str, error: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, error=error)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)

        write_file(code_text, file)
        return code_text


class VerifyCCode(Action):
    name: str = "VerifyCCode"

    COMMON_PROMPT: str = """
    You are a C programming expert, please carefully analyze the following C cdoe.
    1. Check for syntax errors and undefined behavior.
    2. Identify common mistakes such as missing semicolons, incorrect data types, and improper memory management.
    3. Ensure compliance with C standards (C99/C11, specify if needed).
    4. If errors are found, provide detailed explanations and suggest corrected versions of the problematic parts.
    C code: {code}
    """

    async def run(self, code: str):
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await self._aask(prompt)
        return rsp

