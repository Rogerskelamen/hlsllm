import re
import os
import subprocess

from const import TARGET_ALGO_DIR

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
        path (str): The file path to read from.
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
        path (str): The file path to write to.
        content (str): The content to write into the file.
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {path}: {e}")


def pre_handle_testbench(path: str) -> str:
    # 1. copy testbench
    subprocess.run(["cp", path, "-r", TARGET_ALGO_DIR])
    # 2. remove algorithm source file
    algo_name = os.path.basename(path.rstrip('/'))
    subprocess.run(["rm", TARGET_ALGO_DIR / (algo_name + ".cpp")])
    return algo_name


def extract_func_name(input: str) -> str:
    """get function name from input string"""
    code = parse_code(input)
    match = re.match(r"\w+\s+(\w+)\s*\(.*\)", code)
    if match:
        func_name = match.group(1)
        return func_name
    else:
        raise ValueError("Can't find function name")
