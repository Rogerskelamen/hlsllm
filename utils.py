import re

def parse_code(rsp):
    pattern = r"```c(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text

def read_file(path):
    """读取文件内容并返回字符串类型"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""
