import logging
import time
from abc import ABC, abstractmethod

from aiasn.pipelines.context import RunContext


log = logging.getLogger("aiasn")


class Pipeline(ABC):
    name: str   # section in the manifest

    def __call__(self, ctx: RunContext) -> None:
        ctx.manifest.start(self.name)
        start = self._clock = time.perf_counter()
        try:
            self.run(ctx)
        except Exception as e:
            ctx.manifest.fail(self.name, e)
            raise
        ctx.manifest.done(self.name)
        log.info("%-6s %-8s %6.1f s", self.name, "total", time.perf_counter() - start)

    def _log_step(self, step: str, summary: str = "") -> None:
        """One line per step: time since the previous one and a few numbers to check the results at a glance."""
        now = time.perf_counter()
        log.info("%-6s %-8s %6.1f s  %s", self.name, step, now - getattr(self, "_clock", now), summary)
        self._clock = now

    @abstractmethod
    def run(self, ctx: RunContext) -> None: ...
