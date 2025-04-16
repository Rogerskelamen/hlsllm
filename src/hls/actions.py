import subprocess

from metagpt.actions import Action

from hls.rag import RAGCodeStyle
from utils import parse_code, read_file, write_file


class CheckHLSSpec(Action):
    name: str = "CheckHLSSpec"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given the following C/C++ algorithm code intended for HLS synthesis, analyze its structure and syntax specifically for synthesizability.
    - Identify any parts of the code that are not synthesizable by Vitis HLS (e.g., unsupported constructs, improper use of pointers, dynamic memory allocation, recursion, or unsupported library functions).
    - Explain clearly why each issue would cause synthesis to fail.
    - Suggest precise modifications or alternatives to make the code synthesizable while preserving its intended functionality.
    C/C++ algorithm code: {code}
    """

    async def run(self, file: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        return rsp


class RepairHLSCode(Action):
    name: str = "RepairHLSCode"

    COMMON_PROMPT: str = """
    You are an expert in Vitis HLS. Given the following C/C++ algorithm code, modify it as needed to ensure it is fully synthesizable using Vitis HLS, in strict compliance with HLS synthesis standards.
    - Fix any non-synthesizable constructs.
    - Replace unsupported operations or patterns.
    - Preserve the original functionality as much as possible.
    Output only the corrected C/C++ code. Do not include any explanation.
    C/C++ algorithm code: {code}
    """

    async def run(self, file: str, out: str):
        code = read_file(file)
        prompt = self.COMMON_PROMPT.format(code=code)
        rsp = await RAGCodeStyle().aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, out)
        return code_text


class SynthHLSCode(Action):
    name: str = "SynthHLSCode"

    SET_PROJ_TCL: str = """
    open_project {proj_name}
    set_top {top_func}
    add_files {src_file}
    open_solution solution1
    set_part {part}
    create_clock -period 10 -name default
    csynth_design
    exit
    """

    async def run(self, proj_name: str, top_func: str, src_file: str, part: str, tcl_file: str):
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
