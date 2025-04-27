import subprocess
import textwrap

from metagpt.actions import Action

from hls.rag import RAGCodeStyle, RAGOptTech
from utils import parse_code, read_file, write_file


class CheckHLSSpec(Action):
    name: str = "CheckHLSSpec"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given the following C/C++ algorithm code intended for HLS synthesis, analyze its structure and syntax specifically for synthesizability.

    [C/C++ algorithm code]
    {code}

    [Requirements]
    - Identify any parts of the code that are not synthesizable by Vitis HLS (e.g., unsupported constructs, improper use of pointers, dynamic memory allocation, recursion, or unsupported library functions).
    - Explain clearly why each issue would cause synthesis to fail.
    - Suggest precise modifications or alternatives to make the code synthesizable while preserving its intended functionality.
    """

    async def run(self, file: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        return rsp


class RepairHLSCode(Action):
    name: str = "RepairHLSCode"

    COMMON_PROMPT: str = """
    You are an hardware expert in Vitis HLS. Given the following C/C++ algorithm code, modify it as needed to ensure it is fully synthesizable using Vitis HLS, in strict compliance with HLS synthesis standards.

    [C/C++ algorithm code]
    {code}

    [Requirements]
    - Fix any non-synthesizable constructs.
    - Replace unsupported operations or patterns.
    - Preserve the original functionality as much as possible.
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, file: str, out: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, out)
        return code_text


class FixHLSCode(Action):
    name: str = "FixHLSCode"

    COMMON_PROMPT: str = """
    You are an hardware expert in Vitis HLS, and skilled in analyzing HLS synthesis logs and C/C++ source code to identify the causes of synthesis failures and fix the original C/C++ code.

    [Task]
    Given the following C/C++ source code and the synthesis failure log from Vitis HLS, analyze the cause of the failure and generate a corrected version of the code that can successfully be synthesized.

    [C/C++ HLS code]
    {code}

    [Synthesis Message]
    {msg}

    [Requirements]
    - The generated code must be synthesizable with Vitis HLS without errors.
    - Preserve the original algorithm functionality.
    - Return ```cpp your_code_here```, NO additional text
    """

    async def run(self, file: str, msg: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code, msg=msg)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, file)
        return code_text



class SynthHLSCode(Action):
    name: str = "SynthHLSCode"

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
