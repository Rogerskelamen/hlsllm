from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent.parent
IMPLEMENT_DIR = ROOT_PATH / "impl"
IMPLEMENT_FILE_PATH = IMPLEMENT_DIR / "impl.c"
IMPLEMENT_TEST_FILE_PATH = IMPLEMENT_DIR / "impl_test.c"
IMPLEMENT_TEST_EXE_PATH = IMPLEMENT_DIR / "impl_test"

REFERENCE_DIR = ROOT_PATH / "ref"
REFERENCE_FILE_PATH = REFERENCE_DIR / "reference.txt"
