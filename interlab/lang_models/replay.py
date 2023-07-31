from typing import Optional

from interlab.context import Context
from interlab.context.context import ContextState


class Replay:
    def __init__(self, context: Context):
        self.replays = {}
        for context in context.find_contexts(lambda ctx: ctx.kind == "query"):
            if context.state != ContextState.FINISHED:
                continue
            conf = context.inputs.get("conf")
            prompt = context.inputs.get("prompt")
            if conf is None or prompt is None:
                continue
            key = (frozenset(conf.items()), prompt)
            self.replays.setdefault(key, [])
            self.replays[key].append(context.result)
        for replay in self.replays.values():
            replay.reverse()

    def get_cached_response(self, conf: dict, prompt: str) -> Optional[str]:
        key = (frozenset(conf.items()), prompt)
        replay = self.replays.get(key)
        if not replay:
            return None
        return replay.pop()
