from metagpt.actions import Action

from const import OPT_OPTIONS
from utils import parse_code, read_file, write_file

class ChooseOpt(Action):
    name: str = "ChooseOpt"

    COMMON_PROMPT: str = """
    You are a hardware expert specializing in Xilinx Vitis HLS, with deep knowledge about HLS code optimization.

    In HLS, performance can be improved using various compiler directives (pragmas). Different pragmas are suitable for different scenarios and cannot be applied arbitrarily. Below is a list of pragma descriptions and their applicable usage scenarios:
    {pragma_desc}

    Now, here is a code block representing an HLS algorithm:
    {code_content}

    [Task]
    Your task is to analyze this code block and determine which optimization pragmas are appropriate for this specific stage. Choose only the pragmas that are most suitable and likely to improve the performance or area efficiency of this code stage.

    [Note]
    - Do not apply all available optimizations — only select the ones that are clearly applicable.
    - You do not need to rewrite or modify the code.
    - Please return your answer strictly in this format (no explanation): [option_1, option_2, ..., option_n]
    - If you believe the code does not require any optimization, return `null`.
    """

    async def run(self, code_file: str):
        code = read_file(code_file)
        pragma_desc = ""
        for opt in OPT_OPTIONS:
            prompt_name = f"{opt}_PROMPT"
            prompt_content = globals()[prompt_name]
            pragma_desc += prompt_content
        prompt = self.COMMON_PROMPT.format(
            pragma_desc=pragma_desc,
            code_content=code
        )
        rsp = await self._aask(prompt)
        return rsp


class ApplyOpt(Action):
    name: str = "ApplyOpt"

    COMMON_PROMPT: str = """
    You are a hardware expert specializing in Xilinx Vitis HLS, with deep knowledge about HLS code optimization.

    [Input]
    The following is the complete source code of the algorithm:
    {code_content}

    The following is the header file (for reference only, e.g., macros or constants):
    {head_file}

    [Task]
    In HLS, code optimization can be achieved by adding various types of compilation directive (pragmas). Your task is to insert the following HLS optimization pragmas into the code to improve hardware performance.

    Please apply the following optimization pragma to the above code:
    {opt_pragmas}

    Each pragma is accompanied by a description and usage examples to guide proper insertion:
    {pragma_demo}

    [Guidance]
    When applying `#pragma HLS array_partition` to arrays such as `int A[SIZE][SIZE]`, please reason carefully before choosing the partition type.

    Step-by-step guidance:
    1. Refer to the header file to determine the actual value of `SIZE`.
    2. If the dimension size is **less than or equal to 20**, then it is acceptable to use `complete` partitioning.
       - Example: For `int A[10][10]`, use `#pragma HLS array_partition variable=A complete dim=2`
    3. If the dimension size is **greater than 20**, you must NOT use `complete`. Use `block` or `cyclic` instead, and choose an appropriate `factor` based on memory access pattern and loop structure.
       - Example: For `float B[64][64]`, use `#pragma HLS array_partition variable=B block factor=8 dim=2`


    [Requirements]
    - Use `complete` array partitioning ONLY when the array dimension is small (typically ≤ 20). For larger arrays, consider using `block` or `cyclic` partitioning to balance parallelism and resource utilization.
    - Ensure the array_partition pragma is inserted right after the array is declared, not before or elsewhere.
    - Prefer inserting `#pragma HLS pipeline` in the innermost loop to maximize pipelining efficiency, unless the loop has very few iterations, in which case pipelining may not be beneficial.
    - Analyze the algorithm and insert pragmas only where appropriate, based on the purpose and scope described in the usage examples.
    - DO NOT delete or modify existing code, ONLY insert necessary pragma directives to achieve optimal performance
    - DO NOT return any content in header file.
    - Return ONLY ```cpp your_optimized_code_here``` without any explanation.
    """

    async def run(self, code_file: str, head_file: str, opt_list: list[str], hls_src: str):
        code = read_file(code_file)
        head = read_file(head_file)
        opt_pragmas = ""
        pragma_demo_full = ""
        for i, opt_option in enumerate(opt_list):
            opt_pragmas += str(i) + ". " + opt_option + "\n"
            pragma_name = opt_option.split(" ")[-1].upper() + "_DEMO"
            pragma_demo = globals()[pragma_name]
            pragma_demo_full += str(i) + ". " + opt_option + ":\n" + pragma_demo + "\n"

        prompt = self.COMMON_PROMPT.format(
            code_content=code,
            head_file=head,
            opt_pragmas=opt_pragmas,
            pragma_demo=pragma_demo_full
        )
        print(pragma_demo_full)
        # rsp = await RAGOptTech().aask(prompt)
        rsp = await self._aask(prompt)
        code_text = parse_code(rsp)
        write_file(code_text, hls_src)
        return code_text

