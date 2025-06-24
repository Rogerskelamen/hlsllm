import fire
import os

from metagpt.team import Team

import config

from const import BUILD_ALGO_DIR, BUILD_HLS_DIR
from hls.roles import (
    HLSEngineer,
    HLSPerfAnalyzer,
    HLSBuildAssistant
)
from nl2c.roles import (
    CodeProgrammer,
    CTestExecutor,
)

from utils import pre_handle_testbench, read_file

async def main(
    algo_path: str,
    investment: float = 3.0,
    n_round: int = 8,
):
    # preprocess
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # copy target directory to local
    algo_name = pre_handle_testbench(algo_path)

    # store algorithm name and other files
    config.algo_name = algo_name
    config.src_file  = BUILD_ALGO_DIR / f"{algo_name}.cpp"
    config.head_file = BUILD_ALGO_DIR / f"{algo_name}.h"
    config.tb_file   = BUILD_ALGO_DIR / f"{algo_name}_tb.cpp"
    config.desc_file = BUILD_ALGO_DIR / f"{algo_name}.md"
    config.hls_src   = BUILD_HLS_DIR / f"{algo_name}.cpp"

    # get algorithm description
    algo_desc = BUILD_ALGO_DIR / f"{algo_name}.md"

    team = Team()
    team.hire([
        CodeProgrammer(),
        CTestExecutor(),
        HLSEngineer(),
        HLSBuildAssistant(),
        HLSPerfAnalyzer(),
    ])

    team.invest(investment=investment)
    team.run_project(read_file(algo_desc))
    await team.run(n_round=n_round)


if __name__ == "__main__":
    fire.Fire(main)


# import asyncio
#
# from hls.rag import RAGCodeStyle, RAGOptTech
#
# async def main():
#     # answer = await RAGOptTech().aask("List some optimization technologies for Vitis HLS")
#     answer = await RAGCodeStyle().aask("What are unsupported C/C++ Constructs in Vitis HLS development?")
#     # print(answer)
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
