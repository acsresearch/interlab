"""
InterLab core
-------------

Core functionality of InterLab:
* `context` with rich structured logging of nested `Context`s, storage for contexts, and custom-visualized
  content (Images, generic HTML, and f-strings visualizing the field substitutions)
* `actor` for `ActorBase` and few basic agents (including a generic LLM agent and a web console for playing
  as an actor yourself), and actor memory system.
* `lang_models` with several LLM APIs, web-console "LLM" for debugging, and generic wrapper `query_model`
  unifying API of our models, LangChain models (both chat and non-chat models) and general callable functions,
  while doing context logging.
* `queries` holds powerful helpers for advanced queries to the models: querying the model for structured
  data for any dataclass or Pydantic model, including generating schemas, optionally generating examples, and
  robust and powerful response parsing for JSON (with repeats and validation).
* `ui` contains the server for context browser and the web consoles (actor and model), along with compiled web apps.
* `utils` with several text utilities, color handling and other helpers.

And finally, `ext` contains extensions and integrations with other systems (currently Matplotlib and Google Colab).

Note that this package does not contain more complex and concrete implementations of actors, scenarios, and other
LLM-based algorithms. You can find a growing collection of these in `interlab_zoo`.
"""

from . import actor, context, lang_models, queries, utils  # noqa: F401
