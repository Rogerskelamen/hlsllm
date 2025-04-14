from metagpt.rag.engines import SimpleEngine
from metagpt.rag.engines.simple import SentenceSplitter
from metagpt.rag.schema import CohereRerankConfig, ColbertRerankConfig, FAISSIndexConfig, FAISSRetrieverConfig, BM25RetrieverConfig
from metagpt.logs import logger

from llama_index.core.base.response.schema import RESPONSE_TYPE
from llama_index.core.schema import QueryType

from const import COHERE_API_KEY, RAG_CODE_STYLE_PATH, RAG_CODE_STYLE_PERSIST_DIR


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
            logger.info("Loading Existed index!")
            logger.info(f"Index Path:{self.persist_dir}")
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
                transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=0)],
            )
            self.engine.persist(self.persist_dir)

        self.__class__._initialized = True


    async def aquery(self, str_or_query_bundle: QueryType) -> RESPONSE_TYPE:
        return await self.engine.aquery(str_or_query_bundle)

