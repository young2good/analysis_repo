import pandas as pd
from pathlib import Path


def load_data() -> pd.DataFrame:
    path = Path(__file__).parent / "data" / "posts_processed.parquet"
    return pd.read_parquet(path)
