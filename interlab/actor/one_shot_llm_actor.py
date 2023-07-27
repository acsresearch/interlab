from typing import Any

from ..context.data import FormatStr
from ..lang_models import query_model
from ..queries import query_for_json
from .base import ActorWithMemory


class OneShotLLMActor(ActorWithMemory):
    def __init__(
        self,
        name: str,
        model: Any,
        initial_prompt: str,
        *,
        query_with_example: bool = False,
        query_with_cot: bool = False,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.model = model
        self.initial_prompt = initial_prompt
        self.query_with_example = query_with_example
        self.query_with_cot = query_with_cot

    def _act(self, prompt: str = None, *, expected_type=None) -> str:
        if prompt is None:
            prompt = FormatStr("As {name}, what is your next action?").format(
                name=self.name
            )
        hist = self.memory.get_formatted()
        if hist.strip():
            hist_fmt = FormatStr(
                "# Past events\n\n{hist#5274d026}\n\n# End of Past events"
            ).format(hist=hist)
        else:
            hist_fmt = "[No past events]"
        # This preserves FormatStrs if passed in as either initial or current prompt
        # Note that neither initial_prompt nor prompt will be further highlighted here
        q = FormatStr("") + self.initial_prompt + "\n\n" + hist_fmt + "\n\n" + prompt

        if expected_type is str or expected_type is None:
            return query_model(self.model, q)
        else:
            return query_for_json(
                self.model,
                expected_type,
                q,
                with_example=self.query_with_example,
                with_cot=self.query_with_cot,
            )
