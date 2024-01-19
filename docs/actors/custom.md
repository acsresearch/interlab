# `BaseActor` subclassing

To create a subclass of `BaseActor`, the following methods should be overridden:

### `_observe(self, observation: Any)`
This method handles the observation process. It should take an observation and handle it as necessary for the actor's functionality.

```python
from interlab import BaseActor, Event

class MyActor(BaseActor):
    def _observe(self, event: Event):
        # Process the event
        pass
```

### `_query(self, prompt: Any = None, **kwargs) -> Any`
This method processes a query and returns the result. The prompt and any keyword arguments can be used to tailor the query/response logic of the actor.

```python
class MyActor(BaseActor):
    # ... (other methods)

    def _query(self, prompt: Any = None, **kwargs) -> Any:
        # Process the query and return the result
        return some_result
```

### `copy(self)`

This method has to create a copy of the actor.


## `ActorWithMemory` Subclassing

When subclassing `ActorWithMemory`, only the `_query` method is compulsory to override as it already provides implementations for `_observe` and `copy`.

### `_query(self, prompt: Any = None, **kwargs) -> Any`
Just like with the `BaseActor`, you need to implement query processing logic that suits your actor's role.

```python
from interlab import ActorWithMemory

class MyMemoryActor(ActorWithMemory):
    # ... (other methods, if any)

    def _query(self, prompt: Any = None, **kwargs) -> Any:
        # Access the memory and process the query
        return some_result
```