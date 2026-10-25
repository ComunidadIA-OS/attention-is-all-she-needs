from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict



### SETTINGS FOR VIDEO PIPELINE COMPONENTS

class ShotDetectorSettings(BaseModel):
    threshold: float = Field(0.5, gt=0, lt=1)


class PersonTrackerSettings(BaseModel):
    model: str = "yolo11m-pose.pt"
    keypoint_conf: float = Field(0.5, ge=0, le=1)   # min confidence to count a head/shoulder keypoint as visible


class FaceDetectorSettings(BaseModel):
    model_pack: str = "buffalo_l"
    det_size: int = Field(640, gt=0)


class ReidentificatorSettings(BaseModel):
    model_pack: str = "buffalo_l"
    max_distance: float = Field(0.6, gt=0)   # cosine distance between tracks of the same person


class ActiveSpeakerDetectorSettings(BaseModel):
    repo_dir: Path = Path("models/TalkNet-ASD")   # cloned with its weights if missing


class OcrSettings(BaseModel):
    languages: list[str] = ["es", "en"]
    min_conf: float = Field(0.4, ge=0, le=1)


### SETTINGS FOR VIDEO PIPELINE

class VideoSettings(BaseModel):
    fps: int = Field(25, gt=0)                     # required by TalkNet
    audio_sample_rate: int = Field(16_000, gt=0)   # required by TalkNet
    stride: int = Field(4, gt=0)
    min_track_seconds: float = Field(1.0, ge=0)
    min_head: float = Field(0.5, ge=0, le=1)       # fraction of detections with head or shoulders visible
    ocr_fps: float = Field(1.0, gt=0)              # frames per second read by the OCR: captions last seconds
    ocr_corner: float = Field(0.2, ge=0, le=0.5)   # texts centred this close to a corner (logos) are dropped
    device: Literal["auto", "cuda", "cpu"] = "auto"
    shot_detector: ShotDetectorSettings = Field(default_factory=ShotDetectorSettings)
    person_tracker: PersonTrackerSettings = Field(default_factory=PersonTrackerSettings)
    face_detector: FaceDetectorSettings = Field(default_factory=FaceDetectorSettings)
    reidentificator: ReidentificatorSettings = Field(default_factory=ReidentificatorSettings)
    active_speaker_detector: ActiveSpeakerDetectorSettings = Field(default_factory=ActiveSpeakerDetectorSettings)
    ocr: OcrSettings = Field(default_factory=OcrSettings)

### GENERAL SETTINGS

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")

    lake_dir: Path = Path("data")
    tmp_dir: Path = Path("tmp")
    video: VideoSettings = Field(default_factory=VideoSettings)
