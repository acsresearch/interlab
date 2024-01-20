# Environments

Environments in Interlab are scenarios that consist of communicating actors and follow certain rules or dynamics. An environment can simulate various situations such as pricing negotiations, turn-based games, or any other process that involves a series of interactions.

## The BaseEnvironment Class

Every environment in Interlab must inherit from the `BaseEnvironment` abstract base class, which provides the necessary interface for managing the progression and state of the scenario. The environment can exist in one of two states: "running" or "finished". The "running" state indicates that the environment can proceed to the next state, whereas the "finished" state indicates the environment has reached its conclusion.

An environment can be set to an finished by calling method `.set_finished()`. Method `.is_finished` serves for testing if an environment is in a finished state.

## Example Usage of Environments

A specific environment called `PriceNegotiation` is provided by Interlab as a sample implementation of environment. It simulates the scenario of two parties negotiating a price. Here's an example of how to use it:

```python
from interlab import actor
from interlba.environment.experimantal.negotiation import PriceNegotiation
from treetrace import TracingNode
import langchain

# Initialize the language model for the actors.
e35 = langchain.chat_models.ChatOpenAI(model_name='gpt-3.5-turbo')

# Create actors with their initial statements.
pa = actor.OneShotLLMActor("Alice", e35, "I want to buy ...")
pb = actor.OneShotLLMActor("Bob", e35, "I want to sell ...")

# Setup the PriceNegotiation environment.
env = PriceNegotiation(minimizer=pa, maximizer=pb, max_steps=10)

# Run the simulation inside a tracing node, storing the result.
with TracingNode("negotiation", storage=storage) as ctx:
    while not env.is_finished:
        env.step()
```

## Methods and attributes of BaseEnvironment

`BaseEnvironment` provides the folowing methods:

- `.step()` - Proceeds a single step in the environment. Raises an exception if the environment has already finished. Each call to `.step()` creates a new context for that step.
- `.copy()` - Creates a stand-alone copy of the environment.
- `.set_finished()` - Puts the environment in finished state.


`BaseEnvironment` provides the folowing attributes:

- `.is_finished -> boolean` - Checks if the environment is in a terminal state and returns True if it is.