from metagpt.roles import Role
from metagpt.actions import UserRequirement

from actions import WriteAlgorithm

class AlgorithmWriter(Role):
    name: str = "AlgorithmWriter"
    profile: str = "algorithm_writer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([WriteAlgorithm])
