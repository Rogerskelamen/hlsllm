import os
import subprocess
from typing import List

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
    You are an expert in C++ and High-Level Synthesis(HLS), with a strong background in hardware. You excel at translating algorithm descriptions written in natural language into synthesizable C++ code suitable for HLS tools.
    Please generate a complete and self-contained C++ function implementation based on the following information:

    [Algorithm description]
    {algorithm_desc}

    [Header file]
    {header_file}

    [Requirements]
    - Include the specified header file using `#include "{header_name}`.
    - Implement only the function described in the algorithm, without any main function, test code, or additional unrelated content.
    - ONLY include standard library headers if they are required by the implementation.
    - DO NOT add any HLS directives at this stage.
    - Add clear comments explaining key parts of the implementation.
    - Ensure the code follows C++ programming best practices, making it reusable and readable.
    - Return ```cpp your_code_here```, NO additional text.
    """

    async def run(self, algorithm_desc: str, header_file: str, fpath: str):
        header_name = os.path.basename(header_file)
        prompt = self.COMMON_PROMPT.format(algorithm_desc=algorithm_desc, header_file=read_file(header_file), header_name=header_name)

        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, fpath)
        return code_text



class CompileCCode(Action):
    name: str = "CompileCCode"
    async def run(self, src: List[str], out: str):
        compile_cmd = ["g++"] + src + ["-o", out]
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
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

