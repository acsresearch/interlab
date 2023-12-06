# Environments

Environments in Interlab are scenarios that consist of communicating actors and follow certain rules or dynamics. An environment can simulate various situations such as pricing negotiations, turn-based games, or any other process that involves a series of interactions.

## The BaseEnvironment Class

Every environment in Interlab must inherit from the `BaseEnvironment` abstract base class, which provides the necessary interface for managing the progression and state of the scenario. The environment can exist in one of two states: "running" or "finished". The "running" state indicates that the environment can proceed to the next state, whereas the "finished" state indicates the environment has reached its conclusion.

## Example Usage of Environments

A specific environment called `PriceNegotiation` is provided by Interlab as a sample implementation of environment. It simulates the scenario of two parties negotiating a price. Here's an example of how to use it:

```python
import interlab
from interlab import actor

# Initialize the language model for the actors.
e35 = interlab.chat_models.ChatOpenAI(model_name='gpt-3.5-turbo')

# Create actors with their initial statements.
pa = actor.OneShotLLMActor("Alice", e35, "I want to buy ...")
pb = actor.OneShotLLMActor("Bob", e35, "I want to sell ...")

# Setup the PriceNegotiation environment.
env = PriceNegotiation(minimizer=pa, maximizer=pb, max_steps=10)

# Run the simulation inside a context, storing the result.
with interlab.Context("negotiation", storage=storage) as ctx:
    result = env.run_until_end()
    ctx.set_result(result)
```

## Methods of BaseEnvironment

`BaseEnvironment` provides the folowing methods:

- `.step()` - Proceeds a single step in the environment. Raises an exception if the environment has already finished. Each call to `.step()` creates a new context for that step.
- `.copy()` - Creates a stand-alone copy of the environment.
- `.is_finished() -> boolean` - Checks if the environment is in a terminal state and returns True if it is.
- `.run_until_end(self, max_steps: int = None, verbose=False)` - Runs the `.step()` method on the environment until it either finishes or reaches the specified maximum number of steps.

## Attributes of BaseEnvironment

- `.result` - If the environment has finished, this attribute contains the result. If called before the environment finishes, it raises an exception.
- `.actors` - A list containing the current actors within the environment.
- `.n_actors` - An integer representing the number of actors in the environment.
