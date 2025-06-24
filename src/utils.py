import re
import os
import shutil
import subprocess
import config

from const import BUILD_ALGO_DIR, BUILD_HLS_DIR, BUILD_ALGO_TCL_FILE, BUILD_REPORT_DIFF_FILE, BUILD_SYNTH_TCL_FILE

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


def pre_handle_testbench(path: str) -> str:
    # 1. copy testbench
    subprocess.run(["cp", path, "-r", BUILD_ALGO_DIR])
    # 2. remove algorithm source file
    algo_name = os.path.basename(path.rstrip('/'))
    subprocess.run(["rm", BUILD_ALGO_DIR / (algo_name + ".cpp")])
    return algo_name


def synth_tcl_gen():
    # check if synth.tcl exists
    if not os.path.exists(BUILD_SYNTH_TCL_FILE):
        # copy build.tcl to get a new tcl
        copy_tcl_cmd = ["cp", BUILD_ALGO_TCL_FILE, BUILD_SYNTH_TCL_FILE]
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


def cptb2hlsopt():
    """copy files in build/algo to build/hls"""
    # create directory if not exist
    os.makedirs(BUILD_HLS_DIR, exist_ok=True)

    for item in os.listdir(BUILD_ALGO_DIR):
        src_path = os.path.join(BUILD_ALGO_DIR, item)
        dst_path = os.path.join(BUILD_HLS_DIR, item)

        # copy only if it's file type
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

def report_output():
    origin_report = BUILD_ALGO_DIR / config.algo_name / "solution1" / "syn" / "report" / "csynth.rpt"
    hlsopt_report = BUILD_HLS_DIR / config.algo_name / "solution1" / "syn" / "report" / "csynth.rpt"
    origin_perf = extract_perf_table_text(read_file(origin_report))
    hlsopt_perf = extract_perf_table_text(read_file(hlsopt_report))
    perf_diff = f"""
    ===== Performance & Resource Estimates (Origin) ====

    {origin_perf}

    ===== Performance & Resource Estimates (After Optimized) ====

    {hlsopt_perf}
    """
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

