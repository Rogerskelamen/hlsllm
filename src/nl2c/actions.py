import subprocess

from metagpt.actions import Action
from metagpt.logs import logger

from utils import (
    parse_code,
    read_file,
    write_file
)

class WriteAlgorithmCode(Action):
    name: str = "WriteAlgorithmCode"

    COMMON_PROMPT: str = """
    You are an expert in C++ programming and algorithms, with a strong background in hardware, and are skilled at translating algorithm descriptions in natural language into corresponding C++ code.
    Based on the following natural language description of an algorithm, write a complete C++ function implementation.

    [Algorithm description]
    {algorithm_desc}

    [Requirements]
    - Implement only the function corresponding to the given algorithm, without a main function or any test code.
    - Include neccessary `#include` directives **only if the implementation uses standard library functions**. DO NOT include unnecessary headers.
    - Add clear comments explaining key parts of the implementation.
    - Ensure the code follows C++ programming best practices, making it reusable and readable.
    - Return ```cpp your_code_here```, NO additional text.
    """

    async def run(self, algorithm_desc: str, fpath: str):
        prompt = self.COMMON_PROMPT.format(algorithm_desc=algorithm_desc)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, fpath)
        return code_text



class DesignIORef(Action):
    name: str = "DesignIORef"

    COMMON_PROMPT: str = """
    You are a C++ programming expert, please generate {k} sets of structured input-output reference data from the following algorithm description.

    [Algorithm description]
    {algorithm_desc}

    Each input-output reference should be presented in the following structure:
    arg1: [<value1>, <value2>, ...], [arg2: [<value1>, <value2>, ...], ...,] reference_out: [<expected output values>]
    """

    FULL_PROMPT: str = COMMON_PROMPT + """
    [Requirements]
    - The input values should encompass Basic, Edge, and Large Scale scenarios as possible.
    - The format strictly follows the given structure.
    - Pay special attention to edge cases as they often reveal hidden bugs.
    - For large-scale tests, focus on the function's efficiency and performance under heavy loads.
    """

    async def run(self, algorithm_desc: str, fpath: str, k: int = 3):
        prompt = self.FULL_PROMPT.format(algorithm_desc=algorithm_desc, k=k)
        rsp = await self._aask(prompt)
        write_file(rsp, fpath)
        return rsp



class WriteTestCase(Action):
    name: str = "WriteTestCase"

    COMMON_PROMPT: str = """
    You are a C++ programming expert. Based on the given algorithm description and its expected input-output reference data, write test cases using the `assert` function to verify its correctness.

    [Algorithm description]
    {algorithm_desc}

    [Input-output reference]
    {reference}

    [Requirements]
    - Ensure all test cases match the provided input-output reference data.
    - NO need to make the program runnable, focus on the `assert` statement.
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, algorithm_desc: str, reference: str):
        prompt = self.COMMON_PROMPT.format(algorithm_desc=algorithm_desc, reference=reference)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        return code_text



class WriteTestCode(Action):
    name: str = "WriteTestCode"

    COMMON_PROMPT: str = """
    You are a C++ programming expert. Given an algorithm implementation and its corresponding test case code, combine them into a complete, standalone C++ program that can be compiled and executed.

    [Algorithm implementation]
    {code}

    [Test case code]
    {test}

    [Requirements]
    - Add necessary headers, main function, and any missing declarations to make the program fully functional.
    - Preserve the original logic of both the algorithm and the test cases.
    - Use only assert statements for testing —- do not print any messages, output should remain empty if all tests pass.
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, file: str, test: str, fpath: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, test=test)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, fpath)
        return code_text


class CompileCCode(Action):
    name: str = "CompileCCode"
    async def run(self, src: str, out: str):
        compile_result = subprocess.run(["g++", src, "-o", out], capture_output=True, text=True)
        error_result = compile_result.stderr
        logger.info(f"error_result:\n{error_result}")
        return error_result


class RunCCode(Action):
    name: str = "RunCCode"
    async def run(self, file: str):
        runtime_result = subprocess.run([file], capture_output=True, text=True)
        """
        Actually, there is two kinds of error in runtime
        1. cause by assertion failed(given by stderr)
        2. cause by kernel print error[such as segmentation fault]
        But it can only get errors from stderr or stdout
        """
        error_result = runtime_result.stderr
        logger.info(f"error_result:\n{error_result}")
        return error_result



class FixCCode(Action):
    name: str = "FixCCode"

    COMMON_PROMPT: str = """
    You are a C++ programming expert. Analyze the following C++ code and its runtime error message, then modify the algorithm function to fix the error while preserving the original logic.

    [Original algorithm function]
    {algo}

    [C++ source code]
    {code}

    [Error message]
    {error}

    [Requirements]
    - Provide only the corrected version of the algorithm function, NO need to be runnable
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, test_file: str, error: str, fpath: str):
        algo = read_file(fpath)
        code = read_file(test_file)
        prompt = self.COMMON_PROMPT.format(algo=algo, code=code, error=error)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)

        write_file(code_text, fpath)
        return code_text



class VerifyIORef(Action):
    name: str = "VerifyIORef"

    COMMON_PROMPT: str = """
    You are a C++ programming expert, please carefully analyze the following input-output reference data.
    1. make sure the number of args is correct
    C++ code: {code}
    """

    async def run(self, code: str):
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await self._aask(prompt)
        return rsp


