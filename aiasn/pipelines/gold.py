# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging

from aiasn.core.gold.fusion import FusionGold
from aiasn.core.gold.graph import GraphGold
from aiasn.core.gold.index import IndexGold
from aiasn.core.gold.kpis import KpisGold
from aiasn.pipelines.transform_pipeline import TransformPipeline
from aiasn.settings import Settings


class GoldPipeline(TransformPipeline):
    """What the front shows, per video: the quadrants of the fusion, the verdicts and the KPIs. Runs after silver."""
    name = "gold"

    def __init__(self, settings: Settings):
        super().__init__([FusionGold(settings), KpisGold(settings), IndexGold(settings), GraphGold(settings)])


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.gold VIDEO_ID   (after silver)
    from aiasn.pipelines.context import RunContext

    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    video_id = parser.parse_args().video_id
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    ctx = RunContext.for_video(settings, video_id, force=True)   # run by hand: redo it
    GoldPipeline(settings)(ctx)
