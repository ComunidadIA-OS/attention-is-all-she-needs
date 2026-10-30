import logging
import time
from abc import ABC, abstractmethod

from aiasn.pipelines.context import RunContext


log = logging.getLogger("aiasn")


class Pipeline(ABC):
    name: str   # section in the manifest

    def __call__(self, ctx: RunContext, force: bool = False) -> bool:
        """Runs the step and records it in the manifest. A step already done is skipped unless `force` (or the
        context's): its outputs are in the lake. Returns whether it ran."""
        if ctx.manifest.step_done(self.name) and not (force or ctx.force):
            log.info("%-6s %-10s already done", self.name, "skipped")
            return False
        ctx.manifest.start(self.name)
        start = self._clock = time.perf_counter()
        try:
            self.run(ctx)
        except Exception as e:
            ctx.manifest.fail(self.name, e)
            raise
        ctx.manifest.done(self.name)
        log.info("%-6s %-10s %6.1f s", self.name, "total", time.perf_counter() - start)
        return True

    def _log_step(self, step: str, summary: str = "", seconds: float | None = None) -> None:
        """One line per step: time since the previous one and a few numbers to check the results at a glance.

        Steps running in parallel pass their own `seconds` instead.
        """
        if seconds is None:
            now = time.perf_counter()
            seconds, self._clock = now - getattr(self, "_clock", now), now
        log.info("%-6s %-10s %6.1f s  %s", self.name, step, seconds, summary)

    @abstractmethod
    def run(self, ctx: RunContext) -> None: ...
