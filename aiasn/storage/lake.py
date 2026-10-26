from pathlib import Path

import pandas as pd

LAYERS = ("bronze", "silver", "gold")


class Lake:
    def __init__(self, root: Path):
        self.root = Path(root)

    def landing_dir(self, video_id: str) -> Path:
        return self.root / "landing" / f"video_id={video_id}"

    def landing_file(self, video_id: str) -> Path:
        files = [p for p in self.landing_dir(video_id).iterdir() if p.is_file()]
        if len(files) != 1:
            raise FileNotFoundError(f"Expected one file in landing for {video_id}, found {len(files)}")
        return files[0]

    def table_dir(self, layer: str, table: str, video_id: str) -> Path:
        if layer not in LAYERS:
            raise ValueError(f"Unknown layer: {layer}")
        return self.root / layer / table / f"video_id={video_id}"

    def write(self, layer: str, table: str, video_id: str, df: pd.DataFrame) -> Path:
        path = self.table_dir(layer, table, video_id) / "part-0.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return path

    def read(self, layer: str, table: str, video_id: str) -> pd.DataFrame:
        return pd.read_parquet(self.table_dir(layer, table, video_id) / "part-0.parquet")
