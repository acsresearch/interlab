from dataclasses import dataclass
from typing import Any, Optional, TypeVar, Generic, Type, Callable, Tuple

import numpy as np

from interlab.actor import ActorBase, ActorWithMemory
from ..algorithms.mcts import Situation, Mcts


@dataclass
class PlayerConfig:
    action_type: Type[Any]
    action_prompt: Optional[str]
    initial_actor: ActorBase


 class ActorSituation(Situation):

    def __init__(self, config: "ActorMcts", current_player: Optional[int], actors: list[ActorBase]):
        if current_player is not None:
            actors = [a.copy() for a in actors]
            actor = actors[current_player]
        else:
            raise NotImplementedError
        super().__init__(current_player)
        self.config = config
        self.actors = actors


    def perform_action(self, action_idx: int) -> "ActorSituation":
        player = self.config.player_configs[self.current_player]
        actor = self.actors[self.current_player]
        actions = actor.act(prompt=player.action_prompt, expected_type=list[player.action_type])

        raise Exception("TODO")


class ActorMcts:

    def __init__(self,
                 evaluate_situation: Callable[[ActorBase], Tuple[list[Any], np.ndarray, np.ndarray]]
                 perform_action: Callable[[list[ActorBase]], Tuple[int, ]]):
        self.player_configs: list[PlayerConfig] = []
        self.evaluate_situation = evaluate_situation

    def add_player(self, actor: ActorBase, action_type: Type[Any], action_prompt: Optional[str]):
        config = PlayerConfig(initial_actor=actor, action_type=action_type, action_prompt=action_prompt)
        self.player_configs.append(config)

    def search(self, n_iterations: int, initial_player: int=0):
        situation = ActorSituation(initial_player, )
        Mcts()


    def _create_nonterminal_situation(self, current_player: int, actors: list[ActorBase]):

        ActorSituation(self, current_player, actors)

    def _create_terminal_situation(self):
        ActorSituation(self, None, [], [], None)

class MctsActor(ActorWithMemory):
    def __init__(
        self,
        name: str,
        model: Any,
        initial_prompt: str,
        oponent_prompt: str,
        *,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.model = model
        self.initial_prompt = initial_prompt
        self.oponent_prompt = oponent_prompt

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

