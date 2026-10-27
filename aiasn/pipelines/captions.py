# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging

from aiasn.model_adapters.llm_client import LLMClient, make_llm_client
from aiasn.model_adapters.nlp.captions import CaptionExtractor
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import NlpSettings


class CaptionsPipeline(Pipeline):
    """Reads the OCR texts of the video pipeline (bronze video_texts), so it runs after it."""
    name = "captions"

    def __init__(self, cfg: NlpSettings, llm: LLMClient | None = None):
        self.extractor = CaptionExtractor(llm or make_llm_client(cfg.llm), cfg.caption_blocks_per_call,
                                          cfg.max_parallel)

    def run(self, ctx: RunContext) -> None:
        captions = self.extractor.extract(ctx.lake.read("bronze", "video_texts", ctx.video_id))
        ctx.lake.write("bronze", "video_captions", ctx.video_id, captions)
        self._log_step("captions", f"{captions.name.nunique()} people captioned in {len(captions)} frames, "
                                   f"{(~captions.found).sum()} names not found in the text")


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.captions VIDEO_ID   (after the video pipeline)
    from aiasn.settings import Settings

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext.for_video(settings, video_id, force=True)   # run by hand: redo it
    CaptionsPipeline(settings.nlp)(ctx)
