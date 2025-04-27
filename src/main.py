import fire
import os

from metagpt.logs import logger
from metagpt.team import Team

from hls.roles import HLSEngineer, HLSPerfAnalyzer, HLSToolAssistant
from nl2c.roles import (
    CCodeProgrammer,
    CTestDesigner,
    CTestExecutor,
)

from utils import read_file

async def main(
    algo_file: str = "../input/buble_sort.txt",
    investment: float = 3.0,
    n_round: int = 12,
):
    # preprocess
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    algorithm = read_file(algo_file)
    logger.info(f"the certain algorithm: {algorithm}")

    team = Team()
    team.hire([
        CCodeProgrammer(),
        CTestDesigner(),
        CTestExecutor(),
        HLSEngineer(),
        HLSToolAssistant(),
        HLSPerfAnalyzer(),
    ])

    team.invest(investment=investment)
    team.run_project(algorithm)
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
