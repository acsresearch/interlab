"""
InterLab core
-------------

Core functionality of InterLab:
* `actor` for `ActorBase` and few basic agents (including a generic LLM agent and a web console for playing
  as an actor yourself), and actor memory system.
* `queries` holds powerful helpers for advanced queries to the models: querying the model for structured
  data for any dataclass or Pydantic model, including generating schemas, optionally generating examples, and
  robust and powerful response parsing for JSON (with repeats and validation).
* `environment` for imlementation of Environments.

Note that this package does not contain more complex and concrete implementations of actors, scenarios, and other
LLM-based algorithms. You can find a growing collection of these in `interlab_zoo`.
"""

from . import actor, environment, queries, utils
from .__version__ import __version__

__all__ = ["actor", "environment", "queries", "utils", "__version__"]
