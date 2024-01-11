import re
from dataclasses import dataclass
from typing import Type, Any, Sequence
from treetrace import TracingNode

from ..lang_models import query_model
from ..queries import query_for_json


@dataclass
class Affordance:
    name: str
    description: str | None = None
    args_type: Type | None = None
    environment: Any = None


@dataclass
class Action:
    affordance: Affordance
    origin: Any
    args: Any


ACTION_REGEXP = re.compile(r".*<action>(.*)</action>.*")


def query_for_action(
    model: Any,
    prompt: str,
    affordances: Sequence[Affordance],
    max_repeats: int = 5,
    extract_model: Any | None = None,
    origin: Any = None,
) -> Action:
    if extract_model is None:
        extract_model = model

    action_names = ",".join(aff.name for aff in affordances)
    action_descs = "\n\n".join(
        f"# {aff.name}\n{aff.description}" for aff in affordances
    )
    first_prompt = (
        f"{prompt}\n\n"
        f"You have to choose one of the following options: {action_names}\n\n"
        f"Detailed descriptions of each action:\n\n{action_descs}"
    )

    with TracingNode("query_for_affordances") as node:
        for _ in range(max_repeats):
            reply = query_model(model, first_prompt)
            second_prompt = (
                f"Extract what action was chosen from the following answer:\n\n{reply}\n\n"
                f"Write the answer in the format <action>ACTION</action> where ACTION is one of the following strings: {action_names}"
            )
            action = query_model(extract_model, second_prompt)
            match = ACTION_REGEXP.match(action)
            if match is None:
                continue
            chosen_action = match[1].strip()
            for aff in affordances:
                if aff.name == chosen_action:
                    break
            else:
                continue
            if aff.args_type is not None:
                args = query_for_json(
                    model,
                    aff.args_type,
                    (
                        f"Extract what action was chosen from the following answer:\n\n{reply}\n\n"
                        f"Action description:\n{aff.description}"
                    ),
                )
            else:
                args = None
            action = Action(aff, origin, args)
            node.set_result(action)
            return action
        else:
            raise Exception("Too much tries")
