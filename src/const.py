from pathlib import Path

COHERE_API_KEY = "mjdRsGDNbmRkn6kD3b1oxyvjlmSLpypc5mnOwZtl"

# HLS Project constant
SYNTH_TARGET_PART = "xc7z010clg400-1"

# HLS Xilinx Optimization
OPT_OPTIONS = ["ALLOCATION", "RESOURCE", "INLINE", "DATAFLOW",
               "FUNCTION_INSTANTIATE", "STREAM", "PIPELINE",
               "OCCURRENCE", "UNROLL", "DEPENDENCE", "DATA_PACK",
               "LOOP_FLATTEN", "LOOP_MERGE", "LOOP_TRIPCOUNT",
               "ARRAY_MAP", "ARRAY_PARTITION", "ARRAY_RESHAPE"]

LOOP_STRATS = ["LOOP_MERGING", "LOOP_INTERCHANGE", "LOOP_TILING"]

# Constant Path
ROOT_PATH = Path(__file__).resolve().parent.parent

BUILD_DIR              = ROOT_PATH / "build"
BUILD_TCL_FILE         = BUILD_DIR / "build.tcl"
BUILD_FUNC_NAME_FILE   = BUILD_DIR / "top.txt"
BUILD_EXE_ELF_PATH     = BUILD_DIR / "main"
BUILD_SYNTH_TCL_FILE   = BUILD_DIR / "synth.tcl"

BUILD_REPORT_DIR       = BUILD_DIR / "report"
BUILD_REPORT_DIFF_FILE = BUILD_REPORT_DIR / "perf.rpt"

# Project related
ORIGIN_SOLUTION_NAME = "solution1"
LOOP_SOLUTION_NAME   = "solution2"
PRAGMA_SOLUTION_NAME = "solution3"

# Batch result file
RESULT_TXT = ROOT_PATH / "result.txt"

# RAG related
RAG_PATH = ROOT_PATH / "rag"
RAG_CODE_STYLE_PATH = RAG_PATH / "ug1399-code-style.pdf"
RAG_CODE_STYLE_PERSIST_DIR = RAG_PATH / "code_style_persist"

RAG_OPT_TECH_PERSIST_DIR = RAG_PATH / "opt_tech_persist"
RAG_OPT_TECH_PATH = RAG_PATH / "ug1399-opt-tech.pdf"
RAG_OPT_METHOD_PATH = RAG_PATH / "ug1270-opt-method.pdf"
RAG_PP4FPGA_PATH = RAG_PATH / "pp4fpga.pdf"
RAG_HLS_EXAMPLE_CODE_PATH = RAG_PATH / "vitis-hls-example-codes"
