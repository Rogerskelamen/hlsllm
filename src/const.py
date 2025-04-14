from pathlib import Path

COHERE_API_KEY = "mjdRsGDNbmRkn6kD3b1oxyvjlmSLpypc5mnOwZtl"

ROOT_PATH = Path(__file__).resolve().parent.parent

IMPLEMENT_DIR = ROOT_PATH / "impl"
IMPLEMENT_FILE_PATH = IMPLEMENT_DIR / "impl.c"
IMPLEMENT_TEST_FILE_PATH = IMPLEMENT_DIR / "impl_test.c"
IMPLEMENT_TEST_EXE_PATH = IMPLEMENT_DIR / "impl_test"

REFERENCE_DIR = ROOT_PATH / "ref"
REFERENCE_FILE_PATH = REFERENCE_DIR / "reference.txt"

RAG_PATH = ROOT_PATH / "rag"
RAG_CODE_STYLE_PATH = RAG_PATH / "ug1399-code-style.pdf"
RAG_CODE_STYLE_PERSIST_DIR = RAG_PATH / "code_style_persist"

