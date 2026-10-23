from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestSettings(BaseModel):
    fps: int = Field(25, gt=0)                     # TalkNet necesita 25 fps
    audio_sample_rate: int = Field(16_000, gt=0)


class VideoSettings(BaseModel):
    stride: int = Field(4, gt=0)
    min_track_seconds: float = Field(1.0, ge=0)
    min_head: float = Field(0.5, ge=0, le=1)       # fracción de detecciones con cabeza u hombros
    reid_max_distance: float = Field(0.6, gt=0)    # distancia del coseno
    device: Literal["auto", "cuda", "cpu"] = "auto"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIASN_", env_nested_delimiter="__",
                                      env_file=".env", extra="ignore")

    lake_dir: Path = Path("data")
    tmp_dir: Path | None = None                    # None: carpeta temporal del sistema
    ingest: IngestSettings = Field(default_factory=IngestSettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
