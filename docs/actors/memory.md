# Memory systems

Most actors need to store their observations and make use of them when
queried. InterLab offers a common `BaseMemory` interface along with several
implementations:

* `interlab.actor.memory.ListMemory` simply keeps all observations in a list, and 
  every query has all of them available. Of course, this may run out of LLM context space
  in longer scenarios. Also works for non-textual observations (e.g. in GT contexts).
* `interlab.actor.memory.experimental.SummarizingMemory` summarizes earlier and less terse
  textual observations to keep all observations fit a given overall token capacity. Marked
  as experimental for now as it has not been thoroughly battle-tested.
* `interlab.actor.memory.experimental.SimpleEmbeddingMemory` embeds every observation using
  an embedding language model. Given a query, it embeds the query and returns up to the
  given number or length of relevant memories (ordered temporally). Similarly not as well
  tested in our experiments yet.

See the source or the API docs for details of each of the memories.

## Memory and actors

`ActorWithMemory` is intended for agents that directly pass their observations to their
memory. `ActorWithMemory.__init__` takes a `memory` argument, which defauls
to a new `ListMemory`. This is not meant to be a strict hierarchy - you can add
memory to any of your own actor implementations, and actors may even perform more than
mere recording to memory upon getting an observation.
