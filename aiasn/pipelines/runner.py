# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Runs the pipelines of one video: chains in parallel threads, then the ones that read what the chains wrote."""

from concurrent.futures import ThreadPoolExecutor

from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext
from aiasn.settings import Settings
from aiasn.storage.manifest import ERROR, OK, RUNNING


def process_video(video_id: str, settings: Settings, chains: list[list[Pipeline]], then: list[Pipeline] = (),
                  force: bool = False) -> None:
    """Runs each chain in its own thread, its pipelines one after the other (a failure stops the rest of its chain).
    Then, if every chain succeeded, the pipelines in `then` in order.

    Steps the manifest marks as done are skipped unless `force`, so a retry resumes; but once a step runs, the rest of
    its chain and `then` run too, since they read what it wrote. Audio and NLP mostly wait for remote APIs while video
    uses the GPU.
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
        raise
    ctx.manifest.set_status(OK)


def _run_chain(chain: list[Pipeline], ctx: RunContext, force: bool = False) -> bool:
    """Runs the pipelines in order; once one runs, the following ones run too. Returns whether any ran."""
    for pipeline in chain:
        force = pipeline(ctx, force=force) or force
    return force
