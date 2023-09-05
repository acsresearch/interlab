import abc
import math
from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Callable, Sequence, Tuple
import numpy as np

from interlab.context import Context
from interlab_zoo.algorithms.situation import Situation


@dataclass
class Node:
    situation: Situation
    policy: Optional[Sequence[float]]
    value_sum: Sequence[float]
    visit_count: int
    children: list[Optional["Node"]]

    @property
    def value(self):
        return [v / self.visit_count for v in self.value_sum]


def _dump_node_as_context_tree(node: Node, parent: Optional[Node], action_idx):
    desc, style = node.situation.description()
    a = action_idx if action_idx is not None else "root"
    visit_count = node.visit_count
    value = np.around(node.value, 2)
    policy = np.around(parent.policy[action_idx], 2) if parent else "N/A"
    situation = node.situation
    name = f"[{a}] {desc} visits: {visit_count}, value: {value}, policy: {policy}"
    if action_idx is None:
        inputs = None
    else:
        inputs = {"action": parent.situation.actions[action_idx]}
    with Context(name, inputs=inputs, meta=style) as ctx:
        if node:
            for idx, child in enumerate(node.children):
                if child is None:
                    ctx.add_event(
                        f"[{idx}] non-explored",
                        inputs={"action": situation.actions[idx]},
                    )
                else:
                    _dump_node_as_context_tree(child, node, idx)


class Mcts:
    def __init__(
        self,
        situation: Situation,
        pv_estimator: Callable[
            [Situation], tuple[Optional[Sequence[float]], Sequence[float]]
        ],
        c_puct=1.0,
    ):
        self.pv_estimator = pv_estimator
        self.n_iterations: int = 0
        self.root = self._create_node(situation)
        self.c_puct = c_puct

    def search(self, n_iterations: int):
        for _ in range(n_iterations):
            self._run_search()
        self.n_iterations += n_iterations

    def _run_search(self):
        node = self.root
        search_path = [node]
        action_idx = self._choose_action_index(node)
        while action_idx is not None:
            child = node.children[action_idx]
            if child is None:
                break
            search_path.append(child)
            node = child
            action_idx = self._choose_action_index(node)

        if action_idx is not None:
            situation = node.situation.perform_action(action_idx)
            new_node = self._create_node(situation)
            node.children[action_idx] = new_node
        else:
            new_node = None
        self._update_path(search_path, new_node)

    def create_dot(self):
        def helper(node):
            scores = self._compute_scores(node)
            if scores:
                scores = np.around(scores, 2)
            label = "score: {}\nval: {}\nvis: {}".format(
                scores, np.around(node.value, 2), node.visit_count
            )
            lines.append('n{} [label="{}"]'.format(id(node), label))
            for action, child in zip(node.situation.actions, node.children):
                if child is None:
                    continue
                helper(child)
                label = node.situation.action_to_description(action)
                lines.append(
                    'n{} -> n{} [label="{}"]'.format(id(node), id(child), label)
                )

        lines = ["digraph Search {"]
        helper(self.root)
        lines.append("}")
        return "\n".join(lines)

    def dump_as_context_tree(self):
        _dump_node_as_context_tree(self.root, None, None)

    def _compute_scores(self, node: Node) -> Optional[list[float]]:
        policy = node.policy
        if policy is None:
            return None
        spc = math.sqrt(node.visit_count - 1)
        player = node.situation.current_player
        scores = []
        for i, child in enumerate(node.children):
            if child:
                visit_count = child.visit_count
                q = child.value_sum[player] / visit_count
                score = q + policy[i] * spc / (visit_count + 1)
            else:
                score = policy[i] * spc
            scores.append(score)
        return scores

    def _choose_action_index(self, node: Node) -> Optional[int]:
        scores = self._compute_scores(node)
        if scores is None:
            return None
        return int(np.argmax(scores))

    def _update_path(
        self,
        search_path: list[Node],
        new_node: Optional[Node],
    ):
        value = (new_node or search_path[-1]).value
        for node in search_path:
            node.visit_count += 1
            node.value_sum += value

    def _create_node(self, situation: Situation) -> Node:
        policy, value = self.pv_estimator(situation)
        if policy is not None:
            children = [None] * len(policy)
        else:
            children = []
        return Node(
            situation=situation,
            policy=policy,
            value_sum=value,
            visit_count=1,
            children=children,
        )
