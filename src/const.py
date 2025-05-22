from pathlib import Path

COHERE_API_KEY = "mjdRsGDNbmRkn6kD3b1oxyvjlmSLpypc5mnOwZtl"

# HLS Project constant
HLS_PROJECT_NAME = "hlsProj"
HLS_OPT_PROJECT_NAME = "hlsOptProj"
SYNTH_TARGET_PART = "xc7z010clg400-1"

ROOT_PATH = Path(__file__).resolve().parent.parent

BUILD_ALGO_DIR       = ROOT_PATH / "build"
BUILD_HLS_TCL_FILE   = BUILD_ALGO_DIR / "build.tcl"
BUILD_FUNC_NAME_FILE = BUILD_ALGO_DIR / "top.txt"
BUILD_EXE_ELF_PATH   = BUILD_ALGO_DIR / "main"
BUILD_SYNTH_TCL_FILE = BUILD_ALGO_DIR / "synth.tcl"

IMPLEMENT_DIR = ROOT_PATH / "impl"
IMPLEMENT_FILE_PATH = IMPLEMENT_DIR / "impl.cpp"
IMPLEMENT_TEST_FILE_PATH = IMPLEMENT_DIR / "impl_test.cpp"
IMPLEMENT_TEST_EXE_PATH = IMPLEMENT_DIR / "impl_test"
TOP_FUNCTION_FILE = IMPLEMENT_DIR / "top_function"

REFERENCE_DIR = ROOT_PATH / "ref"
REFERENCE_FILE_PATH = REFERENCE_DIR / "reference.json"
TESTBENCH_FILE_PATH = REFERENCE_DIR / "testbench.cpp"

HLS_PATH = ROOT_PATH / "hls"
HLS_SRC_CODE_FILE = HLS_PATH / "hlscode.cpp"
HLS_TCL_FILE = HLS_PATH / "script.tcl"
HLS_OPT_CODE_FILE = HLS_PATH / "hlsopt.cpp"

# RAG related
RAG_PATH = ROOT_PATH / "rag"
RAG_CODE_STYLE_PATH = RAG_PATH / "ug1399-code-style.pdf"
RAG_CODE_STYLE_PERSIST_DIR = RAG_PATH / "code_style_persist"

RAG_OPT_TECH_PERSIST_DIR = RAG_PATH / "opt_tech_persist"
RAG_OPT_TECH_PATH = RAG_PATH / "ug1399-opt-tech.pdf"
RAG_PP4FPGA_PATH = RAG_PATH / "pp4fpga.pdf"
RAG_HLS_EXAMPLE_CODE_PATH = RAG_PATH / "vitis-hls-example-codes"
