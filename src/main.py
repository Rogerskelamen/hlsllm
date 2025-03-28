import fire

from metagpt.logs import logger
from metagpt.team import Team

from nl2c.roles import (
    CCodeProgrammer,
    CTestDesigner,
    CTestExecutor,
)

from utils import read_file

async def main(
    algo_file: str = "./input/buble_sort.txt",
    investment: float = 3.0,
    n_round: int = 5,
):
    algorithm = read_file(algo_file)
    logger.info(f"the certain algorithm: {algorithm}")

    team = Team()
    team.hire([
        CCodeProgrammer(),
        CTestDesigner(),
        CTestExecutor(),
    ])

    team.invest(investment=investment)
    team.run_project(algorithm)
    await team.run(n_round=n_round)


if __name__ == "__main__":
    fire.Fire(main)
