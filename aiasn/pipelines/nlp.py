import argparse
import logging

from aiasn.model_adapters.llm_client import LLMClient, make_llm_client
from aiasn.model_adapters.nlp.mentions import MentionExtractor
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import NlpSettings


class NlpPipeline(Pipeline):
    """Reads the transcript of the audio pipeline (bronze audio_turns), so it runs after it."""
    name = "nlp"

    def __init__(self, cfg: NlpSettings, llm: LLMClient | None = None):
        self.cfg = cfg
        llm = llm or make_llm_client(cfg.llm)
        self.tasks = [MentionExtractor(llm, cfg)]

    def run(self, ctx: RunContext) -> None:
        turns = ctx.lake.read("bronze", "audio_turns", ctx.video_id)
        self._log_step("load", f"{len(turns)} turns, {turns.speaker.nunique()} speakers")
        for task in self.tasks:
            table = task.extract(turns)
            ctx.lake.write("bronze", task.table, ctx.video_id, table)
            unchecked = f", {(~table.found).sum()} not found in the transcript" if "found" in table else ""
            self._log_step(task.table.removeprefix("nlp_"), f"{len(table)} rows{unchecked}")


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.nlp VIDEO_ID   (after the audio pipeline)
    from aiasn.settings import Settings
    from aiasn.storage.lake import Lake
    from aiasn.storage.manifest import Manifest

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext(video_id, settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, video_id),
                     settings.tmp_dir / video_id)
    NlpPipeline(settings.nlp)(ctx)
