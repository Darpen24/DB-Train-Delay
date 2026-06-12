import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db_train_delay.pipelines.local_pipeline import run_local_pipeline

if __name__ == "__main__":
    outputs = run_local_pipeline()
    for layer, path in outputs.items():
        print(f"{layer}: {path}")
