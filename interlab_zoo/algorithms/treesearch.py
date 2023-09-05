# from dataclasses import dataclass, field
# from typing import Dict, TypeVar, Generic, Any, Optional, Callable, List
#
# import numpy as np
#
# from interlab_zoo.algorithms.distribution import Distribution
# from abc import ABC, abstractmethod
#
# # ActionT = TypeVar("Action")
#
# NodeDataT = TypeVar("NodeDataT")
#
#
# @abc.ABC
# class Situation:
#     def __init__(self, player: Optional[int]):
#         self.player = player
#
#     @abc.abstractmethod
#     def perform_action(self, action_id):
#         raise NotImplementedError
#
#
# @dataclass
# class Node(Generic[NodeDataT]):
#     situation: Situation
#     data: NodeDataT
#     children: list[Optional["Node[NodeDataT]"]] = field(default_factory=list)
#
#
# class TreeSearch(Generic[NodeDataT], ABC):
#     def __init__(self, situation: Situation):
#         self.n_iterations: int = 0
#         self.root = Node(situation=situation, data=self.estimator(situation))
#
#     def search(self, n_iterations: int):
#         for _ in range(n_iterations):
#             self._run_search()
#         self.n_iterations += n_iterations
#
#     def _run_search(self):
#         node = self.root
#         action_idx = self.choose_action_index(node)
#         search_path = [node]
#         while action_idx:
#             child = node.children[action_idx]
#             if child is None:
#                 break
#             search_path.append(child)
#             node = child
#             action_idx = self.choose_action_index(node)
#
#         if action_idx is not None:
#             situation = self.perform_action(node, action_idx)
#             new_node = Node(situation=situation, data=self.estimator(situation))
#         else:
#             new_node = None
#         self.update_path(search_path, new_node)
#
#     @abstractmethod
#     def estimator(self, situation: Situation) -> NodeDataT:
#         raise NotImplementedError
#
#     @abstractmethod
#     def update_path(
#         self, search_path: list[Node[NodeDataT]], new_node: Optional[Node[NodeDataT]]
#     ):
#         raise NotImplementedError
#
#     @abstractmethod
#     def choose_action_index(self, node: Node) -> Optional[int]:
#         raise NotImplementedError
#
#     @abstractmethod
#     def perform_action(self, node: Node, action_idx: int) -> Situation:
#         raise NotImplementedError
