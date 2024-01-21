## Subclassing BaseEnvironment

To create custom environments, you shold inherit from `BaseEnvironment` and implement the `_step()` method,
which is called by the `step()` method wrapper:

```python
class MyEnv(BaseEnvironment):
    def _step(self, any_env_sepcific_arguments) -> Any:
        # Implement the logic for a single update of the environment.
```

Note that the semantics of the step depend on the environment and is up to you in your implementation.
A step could be one step in an Markov Decisioen Process, one turn or round in a game, one second of simulated time,
as well as simulating the environemnt for the given duration. The main consideration here is composing
or checpointing environments, or allowing any other external interaction with the environment.

Note that `_step` may also return any value that may repersent the result of the step. You can also define
any attributes to expose the state of the environment to the outside (the agents inside observe the environment only
via `actor.observe(...)`), e.g. a `result` attribute, a `scores` array, etc.
