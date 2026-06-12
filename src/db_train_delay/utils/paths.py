from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
LOCAL_DATA_DIR = DATA_DIR / "local"
SAMPLE_DATA_DIR = DATA_DIR / "samples"
CONFIG_DIR = PROJECT_ROOT / "config"

