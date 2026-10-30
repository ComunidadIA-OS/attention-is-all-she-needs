# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Runs the pipelines of one video: chains in parallel threads, then the ones that read what the chains wrote."""

import logging
from concurrent.futures import ThreadPoolExecutor

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import Settings
from aiasn.storage.manifest import ERROR, OK, RUNNING

log = logging.getLogger("aiasn")


def process_video(video_id: str, settings: Settings, chains: list[list[Pipeline]], then: list[Pipeline] = (),
                  force: bool = False) -> None:
    """Runs each chain in its own thread, its pipelines one after the other (a failure stops the rest of its chain).
    Then, if every chain succeeded, the pipelines in `then` in order.

    Steps the manifest marks as done are skipped unless `force`, so a retry resumes; but once a step runs, the rest of
    its chain and `then` run too, since they read what it wrote. Audio and NLP mostly wait for remote APIs while video
    uses the GPU.

    With `settings.privacy.delete_media_after_run`, the media of the video is deleted when the run ends (see
    `delete_media`). The tables of the lake are kept.
    """
    ctx = RunContext.for_video(settings, video_id, force)
    ctx.manifest.set_status(RUNNING)
    try:
        with ThreadPoolExecutor(len(chains)) as pool:
            runs = [pool.submit(_run_chain, chain, ctx) for chain in chains]
            ran = [run.result() for run in runs]   # re-raises the first failure, once all have finished
        _run_chain(then, ctx, force=any(ran))
    except Exception as e:
        ctx.manifest.set_status(ERROR, e)
        delete_media(ctx, landing=False)
        raise
    ctx.manifest.set_status(OK)
    delete_media(ctx, landing=True)


def delete_media(ctx: RunContext, landing: bool) -> None:
    """Data minimisation: deletes the tmp folder (frames with faces, audio) and, with `landing`, the uploaded video.

    Only with `settings.privacy.delete_media_after_run`. A failed run keeps the video in landing so that it can be
    retried (`landing=False`). Deleting never fails the run: it is logged and the media stays for a periodic purge.
    """
    if not ctx.settings.privacy.delete_media_after_run:
        return
    try:
        ctx.delete_tmp()
    except Exception:
        log.warning("could not delete the tmp folder of %s", ctx.video_id, exc_info=True)
    if landing:
        try:
            ctx.lake.delete_landing(ctx.video_id)
        except Exception:
            log.warning("could not delete the uploaded video of %s", ctx.video_id, exc_info=True)


def _run_chain(chain: list[Pipeline], ctx: RunContext, force: bool = False) -> bool:
    """Runs the pipelines in order; once one runs, the following ones run too. Returns whether any ran."""
    for pipeline in chain:
        force = pipeline(ctx, force=force) or force
    return force
