"""The worker: runs every pipeline of one video and exits.

    python -m aiasn.run_pipelines --video-id ID      the video is already in landing (what the API launches)
    python -m aiasn.run_pipelines --file video.mp4   uploads it to landing first (local use); its id is the file name
    --force                                          run again the steps already done
"""

import argparse
import logging
from pathlib import Path

from aiasn.pipelines.audio import AudioPipeline
from aiasn.pipelines.captions import CaptionsPipeline
from aiasn.pipelines.gold import GoldPipeline
from aiasn.pipelines.nlp import NlpPipeline
from aiasn.pipelines.runner import process_video
from aiasn.pipelines.silver import SilverPipeline
from aiasn.pipelines.video import VideoPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--video-id")
    source.add_argument("--file", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    settings = Settings()
    video_id = args.video_id
    if args.file:
        video_id = args.file.stem
        Lake.from_settings(settings).upload_to_landing(video_id, args.file)
    # NLP reads the transcript and captions the OCR texts, so they go after audio and video; models are loaded once
    chains = [[AudioPipeline(settings.audio), NlpPipeline(settings.nlp)],
              [VideoPipeline(settings.video), CaptionsPipeline(settings.nlp)]]
    process_video(video_id, settings, chains, then=[SilverPipeline(settings), GoldPipeline(settings)], force=args.force)


if __name__ == "__main__":
    main()
