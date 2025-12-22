from collections import defaultdict

class Recorder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_once()
        return cls._instance

    def _init_once(self):
        self._action_calls = defaultdict(int)

    def record(self, action_name: str):
        self._action_calls[action_name] += 1

    def get_action_calls(self) -> dict:
        return dict(self._action_calls)

    def reset(self):
        self._action_calls.clear()

