# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

from aiasn.core.transform import Transform
from aiasn.pipelines.base_pipeline import Pipeline
from aiasn.pipelines.context import RunContext


class TransformPipeline(Pipeline):
    """Runs its transforms in order: each one reads its inputs from the lake and writes its outputs back."""

    def __init__(self, transforms: list[Transform]):
        self.transforms = transforms

    def run(self, ctx: RunContext) -> None:
        for transform in self.transforms:
            tables = {ref: ctx.lake.read(*ref.split("/"), ctx.video_id) for ref in transform.inputs}
            outputs = transform.run(tables)
            for table in transform.outputs:
                ctx.lake.write(transform.layer, table, ctx.video_id, outputs[table])
            self._log_step(transform.name, ", ".join(f"{len(outputs[t])} {t}" for t in transform.outputs))
