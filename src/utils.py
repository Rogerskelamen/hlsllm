import re

def parse_code(rsp: str):
    pattern = r"```cpp(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text.strip()


def read_file(path: str) -> str:
    """读取文件内容并返回字符串类型"""
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


def extract_func_name(input: str) -> str:
    """get function name from input string"""
    code = parse_code(input)
    match = re.match(r"\w+\s+(\w+)\s*\(.*\)", code)
    if match:
        func_name = match.group(1)
        return func_name
    else:
        raise ValueError("Can't find function name")
