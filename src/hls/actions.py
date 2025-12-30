import subprocess

from metagpt.actions import Action
from hls.rag import RAGCodeStyle, RAGOptTech

from record import Recorder
from utils import parse_code, read_file, write_file

from const import BUILD_DIR, BUILD_SYNTH_TCL_FILE, BUILD_TCL_FILE

from prompt.pragma import *
from prompt.loop import *

class SynthHLSCode(Action):
    name: str = "SynthHLSCode"

    async def run(self):
        cmd = ["vitis_hls", "-f", BUILD_SYNTH_TCL_FILE]
        process = subprocess.Popen(
            cmd,
            cwd=BUILD_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        output_lines = []

        # 实时读取输出并打印，同时保存
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            output_lines.append(line)

        process.stdout.close()
        return_code = process.wait()
        if return_code == 0:
            print("\n✅ Synthesis Completed Successfully!")
            return None
        else:
            print("\n❌ Synthesis Failed.")
            last_lines = output_lines[-20:]
            return ''.join(last_lines)


class CosimHLSCode(Action):
    name: str = "CosimHLSCode"

    async def run(self):
        cmd = ["vitis_hls", "-f", BUILD_TCL_FILE]
        process = subprocess.Popen(
            cmd,
            cwd=BUILD_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        output_lines = []

        # 实时读取输出并打印，同时保存
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            output_lines.append(line)

        process.stdout.close()
        return_code = process.wait()
        if return_code == 0:
            print("\n✅ C/RTL Cosimulation Completed Successfully!")
            return None
        else:
            print("\n❌ C/RTL Cosimulation Failed to pass.")
            last_lines = output_lines[-20:]
            return ''.join(last_lines)


class RepairHLSCode(Action):
    name: str = "RepairHLSCode"

    COMMON_PROMPT: str = """
    You are a hardware expert specializing in Xilinx Vitis HLS, with deep knowledge of C/C++ for High-Level Synthesis. You are highly skilled at analyzing HLS synthesis reports and modifying C/C++ code to make it fully synthesizable.
    Given the following C/C++ algorithm code and sythesis report, modify the code as needed to ensure it is fully synthesizable using Vitis HLS, in strict compliance with HLS synthesis standards.

    [Instructions]
    Let's think step by step.
    Firstly, carefully examine the sythesis report to identify any non-synthesizable constructs or unsupported operations.
    Then, locate the specific line(s) in the code responsible for the synthesis failure.
    Finally, modify only what is necessary to ensure code synthesizable, while preserving the original functionality and logic of the code.

    [C/C++ Algorithm Code]
    {code}

    [Synthesis Report]
    {msg}

    [Requirements]
    - DO NOT add any HLS optimization directives.
    - Fix any constructs that are not supported by Vitis HLS.
    - Replace or refactor unsupported operations, dynamic behaviors.
    - Preserve the original functionality as much as possible.
    - Return the corrected version, formatted as ```cpp your_code_here```
    """

    async def run(self, file: str, msg: str):
        Recorder().record(self.name)
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGCodeStyle().aask(prompt)
        code_repaired = parse_code(rsp)
        write_file(code_repaired, file)
        return code_repaired


class FixHLSCode(Action):
    name: str = "FixHLSCode"

    COMMON_PROMPT: str = """
    You are a hardware expert specializing in Xilinx Vitis HLS, with deep knowledge of C/C++ for High-Level Synthesis. You are highly skilled at analyzing C/RTL cosimulation reports and modifying HLS code to ensure it passes the testbench, while strictly conforming to HLS synthesis standards.
    Given the following C/C++ algorithm code and error of execute report, Please analyze the following code and execution report, and revise the code accordingly.

    [Instructions]
    Let's think step by step.
    Firstly, carefully analyze the cosimulation error message and determine whether the code caused the error or the function can't pass tests.
    Then, locate the exact line(s) of code responsible for the issue.
    Finally, modify only what is necessary to resolve the cosimulation error, while follow the rule of HLS code style.

    [C/C++ HLS code]
    {code}

    [Vitis HLS Report]
    {msg}

    [Requirements]
    - Carefully analyze the Vitis HLS report, focusing on the C/RTL Co-simulation phase.
    - The revised function must be fully synthesizable in Vitis HLS.
    - The function must pass C/RTL Co-simulation without functional mismatches.
    - Return corrected code, formatted as ```cpp your_code_here```
    """

    async def run(self, file: str, msg: str):
        Recorder().record(self.name)
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, file)
        return code_text


class FixHLSOpt(Action):
    name: str = "FixHLSOpt"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS and hardware acceleration, with the skill in analyzing HLS synthesis logs and C/C++ source code to identify the causes of synthesis failures and fix the original C/C++ code.

    [Task]
    Given the following optimized C/C++ source code and the synthesis failure log from Vitis HLS, analyze the cause of the failure and generate a corrected version of the code that can successfully be synthesized.

    [C++ optimized HLS Code]
    {code}

    [Synthesis Message]
    {msg}

    [Requirements]
    - Analyze the synthesis log and identify the exact cause of synthesis failure
    - Modify the original C/C++ code to resolve the synthesis issues, ensuring that the modified code is synthesizable by Vitis HLS
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, file: str, msg: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGOptTech().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, file)
        return code_text

