from typing import Any

from ..llm import query_engine, query_for_json
from .actor import ActorWithMemory


class OneShotLLMActor(ActorWithMemory):
    def __init__(
        self,
        name: str,
        engine: Any,
        initial_prompt: str,
        *,
        query_with_example: bool = False,
        query_with_cot: bool = False,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.engine = engine
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
            return query_engine(
                self.engine, f"{q}\n\nWrite only your reply to the prompt."
            )
        else:
            return query_for_json(
                self.engine,
                expected_type,
                q,
                with_example=self.query_with_example,
                with_cot=self.query_with_cot,
            )


class SimpleCoTLLMActor(OneShotLLMActor):
    """Extension of `OneShotLLMActor` that does one extra query to do a simple chain-of-thought reasoning."""

    REFLECT_PROMPT = """\
1. Summarize what you know at this point and reflect on your current situation.
2. State your current goals.
3. Propose actions that can be taken within the current circumstances to reach the goal."""

    def _act(self, prompt: str = None, *, expected_type=None) -> str:
        hist = self.memory.get_formatted()

        q1 = f"""\
{self.initial_prompt}\n
# Past events\n
{hist}\n
# End of Past events\n
# Instructions\n
{self.REFLECT_PROMPT}"""

        if prompt is None:
            prompt = f"As {self.name}, what is your next action?"
        thoughts = query_engine(self.engine, q1)

        q2 = f"""\
{self.initial_prompt}\n
# Past events\n
{hist}\n
# End of Past events\n
# Thoughts on the current situation\n
{thoughts}\n
# End of Thoughts on the current situation\n
# Instructions\n
{prompt}"""

        if expected_type is str or expected_type is None:
            return query_engine(
                self.engine, f"{q2}\n\nWrite only your reply to the prompt."
            )
        else:
            return query_for_json(
                self.engine,
                expected_type,
                q2,
                with_example=self.query_with_example,
                with_cot=self.query_with_cot,
            )
