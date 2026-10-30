"""The data lake: a local folder or an object store (S3, MinIO...), the same for every layer, through fsspec."""

import shutil
from pathlib import Path
from typing import BinaryIO

import fsspec
import pandas as pd

LAYERS = ("bronze", "silver", "gold")


class Lake:
    def __init__(self, uri: str | Path, storage_options: dict | None = None):
        """`uri`: a folder (`data`), `s3://bucket` or any fsspec URL; `storage_options` go to its filesystem
        (endpoint and keys of an S3 store)."""
        self.fs, self.root = fsspec.core.url_to_fs(str(uri), **(storage_options or {}))
        self.root = self.root.rstrip("/")
        self.local = "file" in self.fs.protocol

    @classmethod
    def from_settings(cls, settings) -> "Lake":
        return cls(settings.lake_uri, settings.storage.options(settings.lake_uri))

    def _path(self, *parts: str) -> str:
        return "/".join([self.root, *parts])

    def landing_dir(self, video_id: str) -> str:
        return self._path("landing", f"video_id={video_id}")

    def landing_file(self, video_id: str) -> str:
        """The video uploaded for `video_id`: the one file in its landing folder."""
        folder = self.landing_dir(video_id)
        files = [f for f in self.fs.ls(folder, detail=False) if self.fs.isfile(f)] if self.fs.exists(folder) else []
        if len(files) != 1:
            raise FileNotFoundError(f"Expected one file in landing for {video_id}, found {len(files)}")
        return files[0]

    def upload_to_landing(self, video_id: str, source: Path) -> str:
        """Copies a local video into the landing folder of `video_id`."""
        target = f"{self.landing_dir(video_id)}/{Path(source).name}"
        self.fs.makedirs(self.landing_dir(video_id), exist_ok=True)
        self.fs.put_file(str(source), target)
        return target

    def write_landing(self, video_id: str, name: str, data: BinaryIO) -> str:
        """Writes a video coming as a stream (an upload) into the landing folder of `video_id`."""
        target = f"{self.landing_dir(video_id)}/{name}"
        self.fs.makedirs(self.landing_dir(video_id), exist_ok=True)
        with self.fs.open(target, "wb") as f:
            shutil.copyfileobj(data, f)
        return target

    def delete_landing(self, video_id: str) -> None:
        """Deletes the uploaded video of `video_id` (its landing folder); nothing happens if it is not there."""
        folder = self.landing_dir(video_id)
        if self.fs.exists(folder):
            self.fs.rm(folder, recursive=True)

    def fetch_landing(self, video_id: str, folder: Path) -> Path:
        """The video of `video_id` as a local file: itself in a local lake, else downloaded into `folder`."""
        remote = self.landing_file(video_id)
        if self.local:
            return Path(remote)
        folder.mkdir(parents=True, exist_ok=True)
        local = folder / Path(remote).name
        self.fs.get_file(remote, str(local))
        return local

    def table_dir(self, layer: str, table: str, video_id: str) -> str:
        if layer not in LAYERS:
            raise ValueError(f"Unknown layer: {layer}")
        return self._path(layer, table, f"video_id={video_id}")

    def exists(self, layer: str, table: str, video_id: str) -> bool:
        return self.fs.exists(f"{self.table_dir(layer, table, video_id)}/part-0.parquet")

    def write(self, layer: str, table: str, video_id: str, df: pd.DataFrame) -> str:
        path = f"{self.table_dir(layer, table, video_id)}/part-0.parquet"
        self.fs.makedirs(self.table_dir(layer, table, video_id), exist_ok=True)
        with self.fs.open(path, "wb") as f:
            df.to_parquet(f, index=False)
        return path

    def read(self, layer: str, table: str, video_id: str) -> pd.DataFrame:
        with self.fs.open(f"{self.table_dir(layer, table, video_id)}/part-0.parquet", "rb") as f:
            return pd.read_parquet(f)
