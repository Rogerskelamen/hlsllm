from metagpt.rag.engines import SimpleEngine
from metagpt.rag.engines.simple import SentenceSplitter
from metagpt.rag.schema import CohereRerankConfig, ColbertRerankConfig, FAISSIndexConfig, FAISSRetrieverConfig, BM25RetrieverConfig
from metagpt.logs import logger

from llama_index.core.schema import QueryType

from const import COHERE_API_KEY, RAG_CODE_STYLE_PATH, RAG_CODE_STYLE_PERSIST_DIR, RAG_HLS_EXAMPLE_CODE_PATH, RAG_OPT_TECH_PATH, RAG_OPT_TECH_PERSIST_DIR, RAG_PP4FPGA_PATH


class RAGCodeStyle:
    _instance = None
    _initialized = False

    engine: SimpleEngine = None

    retriever_configs = [FAISSRetrieverConfig(), BM25RetrieverConfig()]
    persist_dir = RAG_CODE_STYLE_PERSIST_DIR
    dataset_files = [RAG_CODE_STYLE_PATH]

    # 创建单例类写法
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RAGCodeStyle, cls).__new__(cls)
        return cls._instance


    def __init__(self) -> None:
        if self.__class__._initialized:
            return

        logger.info("execute RAGCodeStyle.__init__")

        if self.persist_dir.exists():
            logger.info(f"Loading Existed persistent index from {self.persist_dir}!")
            self.engine = SimpleEngine.from_index(
                index_config=FAISSIndexConfig(persist_path=self.persist_dir),
                ranker_configs=[ColbertRerankConfig()],
                retriever_configs=self.retriever_configs
            )
        else:
            logger.info("Loading index from documents!")
            self.engine = SimpleEngine.from_docs(
                input_files=self.dataset_files,
                retriever_configs=[FAISSRetrieverConfig()],
                ranker_configs=[CohereRerankConfig(api_key=COHERE_API_KEY)],
                # transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=0)],
                # 过大的chunk_size会造成计算索引时内存过大
                transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=32)],
            )
            self.engine.persist(self.persist_dir)

        self.__class__._initialized = True


    async def aask(self, str_or_query_bundle: QueryType) -> str:
        query_result = await self.engine.aquery(str_or_query_bundle)
        # retrieval_results = await self.engine.retriever.aretrieve(str_or_query_bundle)
        # print("====== Retrieved Source Nodes ======")
        # for i, node in enumerate(retrieval_results):
        #     print(f"[{i+1}] {node.text}\n")
        resp = query_result.response
        print(resp)
        return resp


class RAGOptTech:
    _instance = None
    _initialized = False

    engine: SimpleEngine = None

    retriever_configs = [FAISSRetrieverConfig(), BM25RetrieverConfig()]
    persist_dir = RAG_OPT_TECH_PERSIST_DIR
    dataset_codes = list(RAG_HLS_EXAMPLE_CODE_PATH.glob("**/*"))
    # dataset_files = [RAG_OPT_TECH_PATH, RAG_PP4FPGA_PATH] + [f for f in dataset_codes if f.is_file()]
    dataset_files = [RAG_OPT_TECH_PATH, RAG_PP4FPGA_PATH]

    # 创建单例类写法
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RAGOptTech, cls).__new__(cls)
        return cls._instance


    def __init__(self) -> None:
        if self.__class__._initialized:
            return

        logger.info("execute RAGPerfOpt.__init__")

        if self.persist_dir.exists():
            logger.info(f"Loading Existed persistent index from {self.persist_dir}!")
            self.engine = SimpleEngine.from_index(
                index_config=FAISSIndexConfig(persist_path=self.persist_dir),
                ranker_configs=[ColbertRerankConfig()],
                retriever_configs=self.retriever_configs
            )
        else:
            logger.info("Loading index from documents!")
            self.engine = SimpleEngine.from_docs(
                input_files=self.dataset_files,
                retriever_configs=[FAISSRetrieverConfig()],
                ranker_configs=[CohereRerankConfig(api_key=COHERE_API_KEY)],
                # transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=0)],
                # 过大的chunk_size会造成计算索引时内存过大
                transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=32)],
            )
            self.engine.persist(self.persist_dir)

        self.__class__._initialized = True


    async def aask(self, str_or_query_bundle: QueryType) -> str:
        query_result = await self.engine.aquery(str_or_query_bundle)
        resp = query_result.response
        print(resp)
        return resp
