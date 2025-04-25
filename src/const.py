from pathlib import Path

COHERE_API_KEY = "mjdRsGDNbmRkn6kD3b1oxyvjlmSLpypc5mnOwZtl"

# HLS Project constant
HLS_PROJECT_NAME = "hlsProj"
HLS_OPT_PROJECT_NAME = "hlsOptProj"
SYNTH_TARGET_PART = "{xc7z010clg400-1}"

ROOT_PATH = Path(__file__).resolve().parent.parent

IMPLEMENT_DIR = ROOT_PATH / "impl"
IMPLEMENT_FILE_PATH = IMPLEMENT_DIR / "impl.cpp"
IMPLEMENT_TEST_FILE_PATH = IMPLEMENT_DIR / "impl_test.cpp"
IMPLEMENT_TEST_EXE_PATH = IMPLEMENT_DIR / "impl_test"
TOP_FUNCTION_FILE = IMPLEMENT_DIR / "top_function"

REFERENCE_DIR = ROOT_PATH / "ref"
REFERENCE_FILE_PATH = REFERENCE_DIR / "reference.txt"
TESTBENCH_FILE_PATH = REFERENCE_DIR / "testbench.cpp"

RAG_PATH = ROOT_PATH / "rag"
RAG_CODE_STYLE_PATH = RAG_PATH / "ug1399-code-style.pdf"
RAG_CODE_STYLE_PERSIST_DIR = RAG_PATH / "code_style_persist"

HLS_PATH = ROOT_PATH / "hls"
HLS_SRC_CODE_FILE = HLS_PATH / "hlscode.cpp"
HLS_TCL_FILE = HLS_PATH / "script.tcl"
HLS_OPT_CODE_FILE = HLS_PATH / "hlsopt.cpp"

