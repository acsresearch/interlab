from dataclasses import dataclass

from interlab.environment.base import BaseEnvironment
from nicetrace import trace


@dataclass(frozen=True)
class EnvNode:
    env: BaseEnvironment
    children: list["EnvNode"]


def expand_tree(
    environment: BaseEnvironment,
    max_depth: int,
    n_children: int,
) -> EnvNode:
    def helper(env, depth):
        children = []
        if depth < max_depth and not env.is_finished:
            for i in range(n_children):
                with trace(f"{i + 1}. child") as ctx:
                    e = env.copy()
                    e.step()
                    ctx.add_input("environment", e)
                    child = helper(e, depth + 1)
                    children.append(child)
        return EnvNode(env, children)

    with trace("root") as ctx:
        ctx.add_input("environment", environment)
        return helper(environment, 0)
