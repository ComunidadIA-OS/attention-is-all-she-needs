# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging

from aiasn.core.gold.fusion import FusionGold
from aiasn.core.gold.kpis import KpisGold
from aiasn.pipelines.transform_pipeline import TransformPipeline
from aiasn.settings import Settings


class GoldPipeline(TransformPipeline):
    """What the front shows, per video: the quadrants of the fusion, the verdicts and the KPIs. Runs after silver."""
    name = "gold"

    def __init__(self, settings: Settings):
        super().__init__([FusionGold(settings), KpisGold(settings)])


if __name__ == "__main__":
    # Usage: python -m aiasn.pipelines.gold VIDEO_ID   (after silver)
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
    GoldPipeline(settings)(ctx)
