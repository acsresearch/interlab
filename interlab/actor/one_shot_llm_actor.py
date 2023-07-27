from typing import Any

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
            prompt = f"As {self.name}, what is your next action?"
        hist = self.memory.get_formatted()
        q = f"""\
{self.initial_prompt}\n
# Past events\n
{hist}\n
# End of Past events\n
{prompt}"""

        if expected_type is str or expected_type is None:
            return query_model(
                self.model, f"{q}\n\nWrite only your reply to the prompt."
            )
        else:
            return query_for_json(
                self.model,
                expected_type,
                q,
                with_example=self.query_with_example,
                with_cot=self.query_with_cot,
            )
