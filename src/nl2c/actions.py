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


class FixCompileErr(Action):
    name: str = "FixCompileErr"

    COMMON_PROMPT: str = """
    You are an expert in C++ and High-Level Synthesis(HLS), with a strong background in hardware. You are highly skilled at diagnosing compilation errors and correcting source code to make it compile successfully.
    Please follow the instructions to fix the issue:

    [Instructions]
    Let's think step by step.
    Firstly, carefully analyze the compilation message to determine the type and cause of the error.
    Then, locate the exact line(s) of code responsible for the issue.
    Finally, modify only what is necessary to resolve the compilation error, while preserving the original functionality and logic of the code.

    [Source Code]
    {code}

    [Compilation Message]
    {msg}

    [Requirements]
    - Provide only the corrected version of the algorithm function.
    - DO NOT add, remove, or modify functionality—just fix the compilation issue.
    - DO NOT include a main function, test code, or additional explanation.
    """

    async def run(self, error: str, src_file: str):
        code = read_file(src_file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=error)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)

        write_file(code_text, src_file)
        return code_text



class FixCCode(Action):
    name: str = "FixCCode"

    COMMON_PROMPT: str = """
    You are an expert in C++ and High-Level Synthesis(HLS), with a strong background in hardware design. You are highly skilled at analyzing execution results and correcting source code to ensure it behaves correctly and passes all tests.
    Please follow the instructions to fix the issue:

    [Instructions]
    Let's think step by step.
    Firstly, carefully analyze the error message or test output to determine whether the code caused the error or the function can't pass tests.
    Then, locate the exact line(s) of code responsible for the issue.
    Finally, modify only what is necessary to resolve the error, while make sure the code could follow the exact algorithm description.

    [Algorithm Description]
    {algo_desc}

    [Source Code]
    {code}

    [Error Message]
    {error}

    [Requirements]
    - Provide only the corrected version of the algorithm function, NO need to be runnable
    - DO NOT add, remove, or modify functionality—just fix the compilation issue.
    """

    async def run(self, error: str, desc_file: str, src_file: str):
        algo_desc = read_file(desc_file)
        code = read_file(src_file)
        prompt = self.COMMON_PROMPT.format(algo_desc=algo_desc, code=code, error=error)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)

        write_file(code_text, src_file)
        return code_text



class CompileCCode(Action):
    name: str = "CompileCCode"
    async def run(self, src: List[str], out: str):
        compile_cmd = ["g++"] + src + ["-o", out]
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
        error_result = compile_result.stderr
        status_code = compile_result.returncode
        logger.info(f"error_result:\n{error_result}")
        logger.info(f"status_code: {status_code}")
        return [status_code, error_result]


class RunCCode(Action):
    name: str = "RunCCode"
    async def run(self, elf_file: str, cwd: str):
        runtime_result = subprocess.run(
            [elf_file],
            cwd=cwd,
            capture_output=True, text=True
        )
        """
        Actually, there is two kinds of error in runtime
        1. caused by failing the testbench (given by stdout)
        2. caused by kernel print error (given by stderr)
        But it can only get errors from stderr or stdout
        """
        error_result = runtime_result.stderr + runtime_result.stdout
        status_code = runtime_result.returncode
        logger.info(f"error_result:\n{error_result}")
        logger.info(f"status_code:\n{status_code}")
        return [status_code, error_result]

