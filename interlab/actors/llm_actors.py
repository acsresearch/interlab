from textwrap import dedent

from .actor import Actor


class OneShotLLMActor(Actor):
    def __init__(
        self,
        engine: callable,
        initial_prompt: str,
        action_type=str,
        *,
        name: str | None = None,
        color: str | None = None,
    ):
        super().__init__(name=name, color=color)
        self.engine = engine
        self.initial_prompt = initial_prompt
        self.action_type = action_type

        # TODO(gavento): Support action types other than str via JSON Pydantic parsing
        assert action_type is str, "No other action supported for now"

    def _act(self, prompt: any = None) -> str:
        if prompt is None:
            prompt = "What is your next action?"
        hist = self.formatted_memories()
        q = dedent(f"""\
            {self.initial_prompt}\n
            # Past events\n
            {hist}\n
            # End of Past events\n
            {prompt}""")
        return self.engine(q)


class SimpleReflectLLMActor(OneShotLLMActor):
    REFLECT_PROMPT = dedent(
        """\
        1. Summarize what you know at this point and reflect on your current situation.
        2. State your current goal relative to the prompt: {prompt!r}
        3. Propose actions to reach the goal within the setting."""
    )

    def _act(self, prompt: any = None) -> str:
        if prompt is None:
            prompt = "What is your next action?"
        hist = self.formatted_memories()
        q1 = dedent(f"""\
            {self.initial_prompt}\n
            # Past events\n
            {hist}\n
            # End of past events\n
            {self.REFLECT_PROMPT.format(prompt=prompt)}""")
        thoughts = self.engine(q1)
        q2 = dedent(f"""\
            {self.initial_prompt}\n
            # Past events\n
            {hist}\n
            # End of Past events\n
            # Thoughts on the current situation\n
            {thoughts}\n
            # End of Thoughts on the current situation\n
            {prompt}""")
        return self.engine(q2)
