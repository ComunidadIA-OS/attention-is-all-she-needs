from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VideoSettings(BaseModel):
    fps: int = Field(25, gt=0)                     # required by TalkNet
    audio_sample_rate: int = Field(16_000, gt=0)   # required by TalkNet
    stride: int = Field(4, gt=0)
    min_track_seconds: float = Field(1.0, ge=0)
    min_head: float = Field(0.5, ge=0, le=1)       # fraction of detections with head or shoulders visible
    reid_max_distance: float = Field(0.6, gt=0)    # cosine distance
    device: Literal["auto", "cuda", "cpu"] = "auto"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")

    lake_dir: Path = Path("data")
    tmp_dir: Path = Path("tmp")
    video: VideoSettings = Field(default_factory=VideoSettings)
