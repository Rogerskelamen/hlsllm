from const import BUILD_DIR

class DataConfig:
    _instance = None
    _initialized = False

    # real attr
    algo_name: str = None
    src_file: str = None
    head_file: str = None
    tb_file: str = None
    desc_file: str = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 algo_name: str = None,
                 src_file: str = None,
                 head_file: str = None,
                 tb_file: str = None,
                 desc_file: str = None) -> None:
        if self.__class__._initialized:
            return

        # initialize config instance
        self.algo_name = algo_name
        self.src_file = src_file
        self.head_file = head_file
        self.tb_file = tb_file
        self.desc_file = desc_file
        self.__class__._initialized = True


    @classmethod
    def get_instance(cls):
        if not cls._instance:
            raise Exception("DataSetConfig has not been initialized yet.")
        return cls._instance


    def get_origin_src_file(self):
        return BUILD_DIR / f"{self.algo_name}_origin.cpp"

    def get_loop_opt_file(self):
        return BUILD_DIR / f"{self.algo_name}_loop.cpp"
