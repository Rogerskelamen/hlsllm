import re
import os
import subprocess

from config import DataConfig
from const import BUILD_DIR, BUILD_REPORT_DIR, BUILD_TCL_FILE, BUILD_REPORT_DIFF_FILE, BUILD_SYNTH_TCL_FILE, LOOP_SOLUTION_NAME, ORIGIN_SOLUTION_NAME

def parse_code(rsp: str):
    pattern = r"```cpp(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text.strip()

def parse_json(rsp: str):
    pattern = r"```json(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text.strip()


def read_file(path: str) -> str:
    """读取文件内容并返回内容的字符串形式

    Args:
    - path (str): The file path to read from.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Reading file {path} failed: {e}")
        return ""


def write_file(content: str, path: str) -> None:
    """write the given content to a file, overwriting if it already exists.

    Args:
    - path (str): The file path to write to.
    - content (str): The content to write into the file.
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {path}: {e}")


def pre_handle_testbench(path: str, isRM: bool) -> str:
    # 1. copy testbench
    subprocess.run(["cp", "-r", path, BUILD_DIR])
    # 2. remove algorithm source file
    algo_name = os.path.basename(path.rstrip('/'))
    if isRM:
        subprocess.run(["rm", BUILD_DIR / (algo_name + ".cpp")])
    return algo_name


def synth_tcl_gen():
    # check if synth.tcl exists
    if not os.path.exists(BUILD_SYNTH_TCL_FILE):
        # copy build.tcl to get a new tcl
        copy_tcl_cmd = ["cp", BUILD_TCL_FILE, BUILD_SYNTH_TCL_FILE]
        subprocess.run(copy_tcl_cmd, capture_output=True, text=True)

        # delete line 10 (cosim)
        rm_cosim_cmd = ["sed", "-i", "10d", BUILD_SYNTH_TCL_FILE]
        subprocess.run(rm_cosim_cmd, capture_output=True, text=True)


def parse_opt_list(input: str) -> list[str]:
    match = re.search(r"\[(.*?)\]", input)
    if match:
        raw_list_str = match.group()
        try:
            # 加引号包裹每个元素
            items = re.findall(r'[^\[\],]+', raw_list_str)
            items = [item.strip() for item in items if item.strip()]
            return items
        except Exception as e:
            print("Error parsing list:", e)
    return None


def report_output():
    project_path = BUILD_DIR / DataConfig().algo_name
    origin_report = project_path / ORIGIN_SOLUTION_NAME / "syn" / "report" / "csynth.rpt"
    loop_opt_report = project_path / LOOP_SOLUTION_NAME / "syn" / "report" / "csynth.rpt"
    origin_perf = extract_perf_table_text(read_file(origin_report))
    loop_opt_perf = extract_perf_table_text(read_file(loop_opt_report))
    perf_diff = f"""
    ===== Performance & Resource Estimates (Origin) ====

    {origin_perf}

    ===== Performance & Resource Estimates (After Optimized) ====

    {loop_opt_perf}
    """
    if not os.path.exists(BUILD_REPORT_DIR):
        os.makedirs(BUILD_REPORT_DIR)
    write_file(perf_diff, BUILD_REPORT_DIFF_FILE)



def extract_perf_table_text(report_text):
    lines = report_text.splitlines()
    start_flag = "+ Performance & Resource Estimates:"
    table_start = False
    table_lines = []

    for line in lines:
        if start_flag in line:
            table_start = True
            continue
        if table_start:
            if re.match(r"^=+", line):  # 表格结束标志（遇到下一个 section）
                break
            if line.strip():  # 跳过空行
                table_lines.append(line)

    return "\n".join(table_lines)


def build_with_other_solution(solution_name):
    with open(BUILD_TCL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 替换第3行和第5行（注意索引从0开始）
    lines[4] = f"open_solution {solution_name}\n"  # hardcode for now

    with open(BUILD_TCL_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
