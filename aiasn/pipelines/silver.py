# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging

from aiasn.core.silver.audio import AudioSilver
from aiasn.core.silver.identity import IdentitySilver
from aiasn.core.silver.names import NamesSilver
from aiasn.core.silver.nlp import NlpSilver
from aiasn.core.silver.video import VideoSilver
from aiasn.core.silver.word_bias import WordBiasSilver
from aiasn.pipelines.transform_pipeline import TransformPipeline
from aiasn.settings import Settings


class SilverPipeline(TransformPipeline):
    """Clean, per-entity tables from bronze. Runs after the bronze pipelines (video, audio, nlp)."""
    name = "silver"

    def __init__(self, settings: Settings):
        super().__init__([VideoSilver(settings), AudioSilver(settings), IdentitySilver(settings), NamesSilver(settings),
                          NlpSilver(settings), WordBiasSilver(settings)])


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.silver VIDEO_ID   (after the bronze pipelines)
    from aiasn.pipelines.context import RunContext
    from aiasn.storage.lake import Lake
    from aiasn.storage.manifest import Manifest

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext(video_id, settings, Lake(settings.lake_dir), Manifest(settings.lake_dir, video_id),
                     settings.tmp_dir / video_id)
    SilverPipeline(settings)(ctx)
