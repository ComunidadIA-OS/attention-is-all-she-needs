from abc import ABC, abstractmethod

from aiasn.pipelines.context import RunContext


class Pipeline(ABC):
    name: str   # section in the manifest

    def __call__(self, ctx: RunContext) -> None:
        ctx.manifest.start(self.name)
        try:
            self.run(ctx)
        except Exception as e:
            ctx.manifest.fail(self.name, e)
            raise
        ctx.manifest.done(self.name)

    @abstractmethod
    def run(self, ctx: RunContext) -> None: ...
