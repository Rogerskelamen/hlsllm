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
    You are an expert in C++ and High-Level Synthesis(HLS), with a strong background in hardware design. You excel at translating algorithm descriptions written in natural language into synthesizable C++ implementation suitable for HLS tools.

    [Tasks]
    Given a natural language description of an HLS design, a pre-written C++ design header, and a pre-written C++ testbench, generate the C++ implementation of the HLS design that aligns with the natural language description.

    [Instructions]
    Let's think step by step:
    - Understand the Algorithm. Read the provided natural language description carefully. Identify the key computational steps, data flow, loop structures, and any decision-making logic involved.
    - Find top function
    Recognize top function and its sub-components in the algorithm description, split out logic of top function.
    - Implement the Logic
    Translate the algorithm into clean, synthesizable C++ code.
    - Implement the sub-components
    Translate the description of sub-components into sub-functions.

    [Algorithm description]
    {algorithm_desc}

    [Header file]
    {header_file}

    [Requirements]
    - Include the specified header file using `#include "{header_name}"`.
    - Implement the top function described in the algorithm description, along with any sub-component functions that are directly called by it.
    - DO NOT write a main function, any test code, or additional unrelated content.
    - Do not include any standard library headers unless they are strictly required by the code implementation. If the function does not use any standard library features, no headers should be included.
    - DO NOT add any HLS pragmas or directives, DO NOT include HLS-specific headers provided by Vitis HLS.
    - Add clear and concise comments to explain key parts of the implementation.
    - Follows modern C++ best practices to ensure reusable and readable.
    - Return ```cpp your_code_here```, NO additional text.
    """

    async def run(self, algorithm_desc: str, header_file: str, fpath: str):
        header_name = os.path.basename(header_file)
        prompt = self.COMMON_PROMPT.format(
            algorithm_desc=algorithm_desc,
            header_file=read_file(header_file),
            header_name=header_name
        )

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
    - Return ```cpp your_fix_code_here```, NO additional text
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

    [Tasks]
    Given the source code, error message or test output, and the testbench, identify and fix any issues in the source code so that it passes all tests and behaves as intended.

    [Instructions]
    Let's think step by step.
    Firstly, carefully analyze the error message or test output to determine whether the code caused the error or the function can't pass tests.
    Then, locate the exact line(s) of code responsible for the issue.
    Finally, modify only what is necessary to resolve the error, while make sure the code could follow the exact algorithm description.

    [Source Code]
    {code}

    [Error Message/Test Output]
    {error}

    [TestBench Code]
    {testbench}

    [Requirements]
    - Provide only the corrected version of the algorithm function, NO need to be runnable
    - Fix only what is required to pass all tests based on the testbench.
    - Return ```cpp your_fix_code_here```, NO additional text
    """

    async def run(self, error: str, src_file: str, tb_file: str):
        code = read_file(src_file)
        testbench = read_file(tb_file)
        prompt = self.COMMON_PROMPT.format(code=code, error=error, testbench=testbench)
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
        if status_code == 0:
            print("✅ Compilation Completed Successfully!")
        else:
            print("❌ Compilation Failed.")
        return [status_code, error_result]


class RunCCode(Action):
    name: str = "RunCCode"
    async def run(self, elf_file: str, cwd: str):
        try:
            runtime_result = subprocess.run(
                [elf_file],
                cwd=cwd,
                timeout=10,  # 10s limit
                capture_output=True, text=True
            )
            """
            Actually, there are three kinds of error message form in runtime
            1. caused by failing the testbench (given by stdout)
            2. caused by running print error (given by stderr)
            3. caused by kernel print error (given by dmesg)
            But for now it can only get errors from stderr or stdout(1&2)
            """
            error_result = runtime_result.stderr + runtime_result.stdout
            status_code = runtime_result.returncode
            logger.info(f"runtime result:\n{error_result}")
            if status_code == 0:
                print("✅ Running Code Successfully!")
            else:
                print("❌ Running Failed.")
        except subprocess.TimeoutExpired as e:
            print("❌ Timeout: Program running took too long and was killed.")
            os._exit(1)  # exit immediately
        return [status_code, error_result]

