from typing import Any

from treetrace import FormatStr

from ..queries import query_for_json, query_model
from .base import ActorWithMemory


class LLMActor(ActorWithMemory):
    """
    A common class for actors based on a language model with a memory system.
    """

    def __init__(self, name: str, model: Any, system_prompt: str = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.model = model
        self.system_prompt = system_prompt

    def query_model(self, prompt: str, *, expected_type=None, with_cot=False):
        """
        A helper function to query actor's language model with system prompt and memory context.
        """
        q = FormatStr("{system_prompt}\n\n{memory#5274d026}\n\n{prompt}").format(
            system_prompt=self.system_prompt,
            memory=self.memory.get_formatted(query=prompt),
            prompt=prompt,
        )
        if expected_type is str or expected_type is None:
            return query_model(self.model, q)
        else:
            return query_for_json(self.model, expected_type, q, with_cot=with_cot)


class OneShotLLMActor(LLMActor):
    """
    A simple yet quite general LLM actor that directly asks the model for an answer to any query.

    By default, the agent is given its system prompt and memory, and directly asked to answer the prompt.
    Optionally, the agent is also instructed to think out loud about the answer with `with_cot` in query().
    """

    def __init__(
        self,
        name: str,
        model: Any,
        system_prompt: str,
        **kwargs,
    ):
        super().__init__(name=name, model=model, system_prompt=system_prompt, **kwargs)

    def _query(self, prompt: str = None, *, expected_type=None, with_cot=False) -> str:
        if prompt is None:
            prompt = FormatStr("As {name}, what is your next action?").format(
                name=self.name
            )
        return self.query_model(prompt, expected_type=expected_type, with_cot=with_cot)
