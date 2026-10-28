from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



### SETTINGS FOR VIDEO PIPELINE COMPONENTS

class ShotDetectorSettings(BaseModel):
    threshold: float = Field(0.5, gt=0, lt=1)


class PersonTrackerSettings(BaseModel):
    model: str = "yolo11m-pose.pt"
    keypoint_conf: float = Field(0.5, ge=0, le=1)   # min confidence to count a head/shoulder keypoint as visible


class FaceDetectorSettings(BaseModel):
    model_pack: str = "buffalo_l"
    root: Path = Path("~/.insightface")            # where InsightFace keeps its model packs
    det_size: int = Field(640, gt=0)


class ReidentificatorSettings(BaseModel):
    model_pack: str = "buffalo_l"
    root: Path = Path("~/.insightface")
    max_distance: float = Field(0.6, gt=0)   # cosine distance between tracks of the same person


class ActiveSpeakerDetectorSettings(BaseModel):
    repo_dir: Path = Path("models/TalkNet-ASD")   # cloned with its weights if missing


class GenderEstimatorSettings(BaseModel):
    model: str = "iitolstykh/mivolo_v2"
    revision: str = "53393526c220e34cdd7b722b36d22b6f9e5f4241"   # pinned: the model runs code from its Hub repo


class OcrSettings(BaseModel):
    languages: list[str] = ["es", "en"]
    model_dir: Path = Path("~/.EasyOCR/model")
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


class ToneSettings(BaseModel):
    method: Literal["llm", "zero_shot"] = "llm"
    zero_shot_model: str = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"   # multilingual NLI
    min_score: float = Field(0.9, ge=0, le=1)      # zero-shot: below it in every class, no tone
    with_previous_turn: bool = True                # zero-shot: collaborating or disagreeing depends on what came before


### SETTINGS FOR NLP PIPELINE

class NlpSettings(BaseModel):
    llm: LlmSettings = Field(default_factory=LlmSettings)
    tone: ToneSettings = Field(default_factory=ToneSettings)
    device: Literal["auto", "cuda", "cpu"] = "auto"   # local models (zero-shot tone)
    max_parallel: int = Field(6, gt=0)             # tasks (LLM calls) at the same time
    caption_blocks_per_call: int = Field(4, gt=0)  # OCR blocks per captions call; the calls go in parallel
    # Guide for the model, which may add new topics
    # English (key, word2vec) → Spanish (UI). One word per topic, so that word2vec has it; more only when needed
    topics_guide: dict[str, str] = {
        # stereotyped as "feminine" or centred on the person
        "care": "cuidados", "family": "familia", "motherhood": "maternidad",
        "work-life balance": "conciliación",   # no single word for it: no word2vec bias
        "relationships": "relaciones y vida sentimental", "appearance": "aspecto físico", "womanhood": "ser mujer",
        "diversity": "diversidad", "equality": "igualdad",
        # professional or stereotyped as "masculine"
        "technology": "tecnología", "science": "ciencia", "economy": "economía", "leadership": "liderazgo",
        "expertise": "su especialidad", "politics": "política", "sports": "deporte",
        # others
        "education": "educación", "health": "salud", "history": "historia",
    }
    # Guide for the model, which may add new roles; English → Spanish
    roles_guide: dict[str, str] = {
        "host": "presentador/a", "interviewer": "entrevistador/a", "expert": "experto/a",
        "voice-over narrator": "narrador/a en off", "testimony": "testimonio", "character": "personaje",
        "audience": "público"}
    max_ideas: int = Field(10, gt=0)               # key ideas of the piece


### SETTINGS FOR SILVER LAYER

class BiasSettings(BaseModel):
    """w2vNEWS (Google News word2vec), for the gender bias of topics and titles (Bolukbasi et al. 2016)."""
    model_path: Path = Path("~/gensim-data/word2vec-google-news-300/word2vec-google-news-300.gz")
    url: str | None = ("https://github.com/RaRe-Technologies/gensim-data/releases/download/"
                       "word2vec-google-news-300/word2vec-google-news-300.gz")   # downloaded from here if missing
    vocab_limit: int = Field(500_000, gt=0)        # most frequent words loaded; terms outside them get no score


class SilverSettings(BaseModel):
    gender_threshold: float = Field(0.80, ge=0.5, le=1)   # below it, no_determinado (ADR-0005); also used by the fusion
    # A person whose face shows in fewer of their detections (back turned, only hands) gets no gender from the video:
    # from the body alone it is unreliable, and without a face they cannot be told apart from others either
    min_face_share: float = Field(0.5, ge=0, le=1)
    max_gap_s: float = Field(1.0, ge=0)                    # shorter absences do not split a person's presence
    speaking_threshold: float = 0.0                        # speaking_score (TalkNet) above it: speaking
    speaking_window_s: float = Field(1.0, ge=0)            # rolling majority of the speaking state; 0: no smoothing
    # A speaker is a person on screen if both talk at the same time for at least this long and this share of their speech
    min_link_s: float = Field(1.0, ge=0)
    min_link_share: float = Field(0.3, ge=0, le=1)
    # A voice still unlinked (the lip model missed it: profile, a microphone in front) is the one person alone on
    # screen for at least this share of its speech, if their genders do not contradict each other
    min_copresence_share: float = Field(0.6, ge=0, le=1)
    name_similarity: float = Field(0.8, ge=0, le=1)        # two spellings of a word count as the same name from here
    authority_roles: list[str] = ["host", "expert", "voice-over narrator"]   # roles that speak from authority
    caption_grants_authority: bool = True                  # a caption title showing authority does too, whatever the role


### GENERAL SETTINGS

class StorageSettings(BaseModel):
    """Access to an S3-compatible store (MinIO, AWS, OVH Object Storage) when the lake is an `s3://` URI."""
    endpoint_url: str | None = None                # MinIO: http://minio:9000; None: AWS
    access_key: SecretStr | None = None
    secret_key: SecretStr | None = None

    def options(self, uri: str) -> dict:
        """fsspec storage options for `uri`; none for a local folder."""
        if not uri.startswith("s3://"):
            return {}
        options = {"key": self.access_key, "secret": self.secret_key}
        options = {k: v.get_secret_value() for k, v in options.items() if v is not None}
        # No cached listings: the API and the workers write the same lake, and a stale listing makes s3fs read a
        # rewritten manifest with its old ETag (FileExpired)
        options["use_listings_cache"] = False
        return options | ({"client_kwargs": {"endpoint_url": self.endpoint_url}} if self.endpoint_url else {})


class WorkerContainerSettings(BaseModel):
    """The worker container the API starts for each video (docker launcher)."""
    image: str = "aiasn-worker"
    network: str | None = "aiasn"                  # where the store is reachable
    volumes: dict[str, str] = {"aiasn-models": "/models"}   # volume (or host folder) -> path in the container
    gpu: bool = True                               # when Docker has it (NVIDIA Container Toolkit); else the CPU
    # Variables of the API's environment passed on, by name or prefix: the worker reads the same settings
    env: list[str] = ["LAKE_URI", "STORAGE__", "MODELS_DIR", "HF_HOME", "OVH_", "TMP_DIR",
                      "VIDEO__", "AUDIO__", "NLP__", "SILVER__", "BIAS__", "PRIVACY__"]


class PrivacySettings(BaseModel):
    """Data minimisation (GDPR, EU AI Act): what is kept of a video once it is processed."""
    # Delete its tmp folder (frames with faces, audio) and, if every step succeeded, the uploaded video in landing.
    # The tables of the lake stay. Off by default: debugging and the annotated video need those files.
    delete_media_after_run: bool = False


class ApiSettings(BaseModel):
    cors_origins: list[str] = ["*"]
    upload_formats: list[str] = [".mp4", ".mov", ".webm", ".mkv", ".avi"]
    # docker: a worker container per video; process: a child process (no Docker); auto: docker if it is reachable
    launcher: Literal["auto", "docker", "process"] = "auto"
    worker: WorkerContainerSettings = Field(default_factory=WorkerContainerSettings)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")

    lake_uri: str = "data"                         # a local folder, or s3://bucket (see storage)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    tmp_dir: Path = Path("tmp")
    # One folder for every local model (Docker: a volume); None keeps each library's own default place.
    # Hugging Face models go where HF_HOME says.
    models_dir: Path | None = None
    video: VideoSettings = Field(default_factory=VideoSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    nlp: NlpSettings = Field(default_factory=NlpSettings)
    silver: SilverSettings = Field(default_factory=SilverSettings)
    bias: BiasSettings = Field(default_factory=BiasSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)

    @model_validator(mode="after")
    def _paths_in_models_dir(self) -> "Settings":
        if self.models_dir:
            root, video = self.models_dir, self.video
            video.person_tracker.model = str(root / Path(video.person_tracker.model).name)
            video.face_detector.root = video.reidentificator.root = root / "insightface"
            video.active_speaker_detector.repo_dir = root / "TalkNet-ASD"
            video.ocr.model_dir = root / "easyocr"
            self.bias.model_path = root / Path(self.bias.model_path).name
        return self
