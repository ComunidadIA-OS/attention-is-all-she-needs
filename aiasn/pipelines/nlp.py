import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from aiasn.model_adapters.llm_client import LLMClient, make_llm_client
from aiasn.model_adapters.nlp.base import NlpTask
from aiasn.model_adapters.nlp.ideas import IdeaExtractor
from aiasn.model_adapters.nlp.mentions import MentionExtractor
from aiasn.model_adapters.nlp.references import ReferenceExtractor
from aiasn.model_adapters.nlp.roles import RoleExtractor
from aiasn.model_adapters.nlp.tone import make_tone_classifier
from aiasn.model_adapters.nlp.topics import TopicExtractor
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import NlpSettings


class NlpPipeline(Pipeline):
    """Reads the transcript of the audio pipeline (bronze audio_turns), so it runs after it."""
    name = "nlp"

    def __init__(self, cfg: NlpSettings, llm: LLMClient | None = None):
        self.cfg = cfg
        llm = llm or make_llm_client(cfg.llm)
        self.tasks = [MentionExtractor(llm, cfg), TopicExtractor(llm, cfg), ReferenceExtractor(llm, cfg),
                      RoleExtractor(llm, cfg), IdeaExtractor(llm, cfg), make_tone_classifier(llm, cfg)]

    def run(self, ctx: RunContext) -> None:
        turns = ctx.lake.read("bronze", "audio_turns", ctx.video_id)
        self._log_step("load", f"{len(turns)} turns, {turns.speaker.nunique()} speakers")
        # The tasks are independent and mostly wait for the model: all at once, up to `max_parallel` calls
        with ThreadPoolExecutor(self.cfg.max_parallel) as pool:
            runs = [pool.submit(self._run_task, task, turns, ctx) for task in self.tasks]
        for run in runs:
            run.result()   # re-raises the first failure, once every task has finished

    def _run_task(self, task: NlpTask, turns: pd.DataFrame, ctx: RunContext) -> None:
        start = time.perf_counter()
        table = task.extract(turns)
        ctx.lake.write("bronze", task.table, ctx.video_id, table)
        unchecked = f", {(~table.found).sum()} not found in the transcript" if "found" in table else ""
        self._log_step(task.table.removeprefix("nlp_"), f"{len(table)} rows{unchecked}", time.perf_counter() - start)


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.nlp VIDEO_ID   (after the audio pipeline)
    from aiasn.settings import Settings

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext.for_video(settings, video_id)
    NlpPipeline(settings.nlp)(ctx)
