import subprocess
import textwrap

from metagpt.actions import Action

from const import BUILD_ALGO_DIR, BUILD_HLS_TCL_FILE, BUILD_SYNTH_TCL_FILE
from hls.rag import RAGCodeStyle, RAGOptTech
from utils import parse_code, read_file, write_file


class SynthHLSCode(Action):
    name: str = "SynthHLSCode"

    async def run(self):
        cmd = ["vitis_hls", "-f", BUILD_SYNTH_TCL_FILE]
        try:
            subprocess.run(
                cmd,
                cwd=BUILD_ALGO_DIR,
                capture_output=True, text=True, check=True
            )
            print("✅ Synthesis Completed Successfully!")
            return None
        except subprocess.CalledProcessError as e:
            print("❌ Synthesis Failed.")
            # 综合失败，处理输出结果
            return e.stdout


class CosimHLSCode(Action):
    name: str = "CosimHLSCode"

    async def run(self):
        cmd = ["vitis_hls", "-f", BUILD_HLS_TCL_FILE]
        try:
            subprocess.run(
                cmd,
                cwd=BUILD_ALGO_DIR,
                capture_output=True, text=True, check=True
            )
            print("✅ Synthesis Completed Successfully!")
            return None
        except subprocess.CalledProcessError as e:
            print("❌ Synthesis Failed.")
            # 综合失败，处理输出结果
            return e.stdout


class RepairHLSCode(Action):
    name: str = "RepairHLSCode"

    COMMON_PROMPT: str = """
    You are an hardware expert specializing in Xilinx Vitis HLS, with deep knowledge of C/C++ for High-Level Synthesis. You are highly skilled at analyzing HLS synthesis reports and modifying C/C++ code to make it fully synthesizable.
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
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGCodeStyle().aask(prompt)
        code_repaired = parse_code(rsp)
        write_file(code_repaired, file)
        return code_repaired


class FixHLSCode(Action):
    name: str = "FixHLSCode"

    COMMON_PROMPT: str = """
    You are an hardware expert specializing in Xilinx Vitis HLS, with deep knowledge of C/C++ for High-Level Synthesis. You are highly skilled at analyzing C/RTL cosimulation reports and modifying HLS code to ensure it passes the testbench, while strictly conforming to HLS synthesis standards.
    Please analyze the following code and execution report, and revise the code accordingly.

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
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, file)
        return code_text




class SynthHLSOpt(Action):
    name: str = "SynthHLSOpt"

    SET_PROJ_TCL: str = textwrap.dedent("""
    open_project {proj_name}
    set_top {top_func}
    add_files {src_file}
    open_solution solution1
    set_part {part}
    create_clock -period 10 -name default
    csynth_design
    exit
    """)

    async def run(self, proj_name: str, top_func: str, src_file: str, part: str, tcl_file: str):
        top_func = read_file(top_func)
        tcl = self.SET_PROJ_TCL.format(
            proj_name=proj_name,
            top_func=top_func,
            src_file=src_file,
            part=part
        ).strip()
        write_file(tcl, tcl_file)

        cmd = ["vitis_hls", "-f", tcl_file]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Synthesis Completed Successfully!\n")
            return None
        except subprocess.CalledProcessError as e:
            print("❌ Synthesis Failed.")
            # 综合失败，处理输出结果
            return e.stdout



"""
这个动作待优化，在该动作之前可以进行一些预处理或者分析操作，比如：
1. 对复杂算法进行拆分，单函数 -> 多个子函数
2. 分析C++代码中计算量大的部分(分析工具)，针对性优化
3. 使用更高抽象的角度分析函数的调用来对硬件实现进行优化

同样的，在优化动作之后，也可以采用一些措施提高优化程度，比如：
1. 使用DSE(设计空间探索)工具来分析可用优化
"""
class OptimizeHLSPerf(Action):
    name: str = "OptimizeHLSPerf"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS and hardware acceleration, with the skill to analyze HLS code and improve hardware performance.

    [Task]
    Analyze the following C++ HLS code and optimize it for better performance using appropriate HLS pragmas (such as #pragma HLS PIPELINE, UNROLL, ARRAY_PARTITION, etc.) without changing its functionality.

    [C++ HLS Code]
    {code}

    [Requirements]
    - Identify and explain potential performance bottlenecks
    - Apply optimization techniques and relevant HLS pragmas
    - DO preserve original functionality
    - Ouput the optimized code only, NO other explanation text
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, file: str, out: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGOptTech().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, out)
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
