from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, SecretStr
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


class GenderEstimatorSettings(BaseModel):
    model: str = "iitolstykh/mivolo_v2"
    revision: str = "53393526c220e34cdd7b722b36d22b6f9e5f4241"   # pinned: the model runs code from its Hub repo


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
    gender_estimator: GenderEstimatorSettings = Field(default_factory=GenderEstimatorSettings)
    ocr: OcrSettings = Field(default_factory=OcrSettings)


### SETTINGS FOR AUDIO PIPELINE COMPONENTS

class TranscriberSettings(BaseSettings):
    """Whisper with diarization on OVHcloud AI Endpoints. The token comes from the environment or .env."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: str = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
    model: str = "whisper-large-v3"
    token: SecretStr = Field(SecretStr(""), validation_alias=AliasChoices("token", "OVH_AI_ENDPOINTS_ACCESS_TOKEN"))
    language: str | None = None                    # ca, es, en...; None lets Whisper detect it
    timeout: float = Field(600, gt=0)              # seconds


class VoiceGenderClassifierSettings(BaseModel):
    model: str = "prithivMLmods/Common-Voice-Gender-Detection"
    min_seconds: float = Field(0.5, ge=0)          # shorter turns have too little voice to decide
    max_seconds: float = Field(15.0, gt=0)         # only the start of longer turns is used: enough, and faster


### SETTINGS FOR AUDIO PIPELINE

class AudioSettings(BaseModel):
    sample_rate: int = Field(16_000, gt=0)         # what Whisper and the voice classifier expect
    device: Literal["auto", "cuda", "cpu"] = "auto"
    transcriber: TranscriberSettings = Field(default_factory=TranscriberSettings)
    voice_gender_classifier: VoiceGenderClassifierSettings = Field(default_factory=VoiceGenderClassifierSettings)


### SETTINGS FOR NLP PIPELINE COMPONENTS

class LlmSettings(BaseSettings):
    """Model behind an OpenAI-compatible API (OVHcloud AI Endpoints by default). The token comes from the environment or .env."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    provider: Literal["litellm", "ollama"] = "litellm"
    model: str = "openai/Meta-Llama-3_3-70B-Instruct"   # "openai/": OpenAI-compatible endpoint for litellm
    base_url: str = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
    token: SecretStr = Field(SecretStr(""), validation_alias=AliasChoices("token", "OVH_AI_ENDPOINTS_ACCESS_TOKEN"))
    temperature: float = Field(0.0, ge=0)
    timeout: float = Field(300, gt=0)              # seconds
    retries: int = Field(2, ge=0)


### SETTINGS FOR NLP PIPELINE

class NlpSettings(BaseModel):
    llm: LlmSettings = Field(default_factory=LlmSettings)
    max_parallel: int = Field(6, gt=0)             # tasks (LLM calls) at the same time
    # Guide for the model, which may add new topics
    topics_guide: list[str] = [
        # stereotyped as "feminine" or centred on the person
        "care", "family and motherhood", "work-life balance", "love life and relationships", "physical appearance",
        "being a woman / gender experience", "diversity and equality",
        # professional or stereotyped as "masculine"
        "technology", "science and research", "finance and economy", "leadership and management",
        "their work or field", "politics", "sports",
        # others
        "education", "health", "history",
    ]
    # Guide for the model, which may add new roles
    roles_guide: list[str] = ["host", "interviewer", "expert", "voice-over narrator", "testimony", "character", "audience"]
    max_ideas: int = Field(10, gt=0)               # key ideas of the piece


### GENERAL SETTINGS

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")

    lake_dir: Path = Path("data")
    tmp_dir: Path = Path("tmp")
    video: VideoSettings = Field(default_factory=VideoSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    nlp: NlpSettings = Field(default_factory=NlpSettings)
