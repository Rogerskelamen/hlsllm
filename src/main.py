import fire
import os

from metagpt.team import Team

from config import DataConfig
from const import BUILD_DIR, RESULT_TXT

from hls.roles import (
    HLSEngineer,
    HLSBuildAssistant
)
from nl2c.roles import (
    CodeProgrammer,
    CTestExecutor,
)
from opt.roles import (
    HLSFuncOptimizer,
    HLSHardNormalizer,
    HLSPerfAnalyzer
)

from record import Recorder
from utils import pre_handle_testbench, read_file

async def main(
    algo_path: str,
    type: str = "gen",
    investment: float = 3.0,
    n_round: int = 8,
):
    # preprocess
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    Recorder().reset()

    # copy target directory to local
    algo_name = pre_handle_testbench(algo_path, type == "gen")

    # store algorithm name and other files
    DataConfig(
        algo_name = algo_name,
        src_file  = BUILD_DIR / f"{algo_name}.cpp",
        head_file = BUILD_DIR / f"{algo_name}.h",
        tb_file   = BUILD_DIR / f"{algo_name}_tb.cpp",
        desc_file = BUILD_DIR / f"{algo_name}.md",
    )

    # get algorithm description
    algo_desc = BUILD_DIR / f"{algo_name}.md"

    team = Team()

    if type == "gen":
        team.hire([
            CodeProgrammer(),
            CTestExecutor(),
            HLSEngineer(),
            HLSBuildAssistant(),
        ])

        team.invest(investment=investment)
        team.run_project(read_file(algo_desc))
        await team.run(n_round=n_round)

        action_calls = Recorder().get_action_calls()
        with open(RESULT_TXT, 'a', encoding='utf-8') as file:
            file.write(str(action_calls) + '\n')

    elif type == "opt":
        team.hire([
            HLSEngineer(),
            HLSBuildAssistant(),
            HLSHardNormalizer(),
            HLSFuncOptimizer(),
            HLSPerfAnalyzer(),
        ])

        team.invest(investment=investment)
        team.run_project("")
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
