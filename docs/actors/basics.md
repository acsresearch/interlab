# Actors

The Actor subsystem within the Interlab library provides a mechanism to create agent-based models with varying levels of complexity. The base class within this subsystem is the BaseActor, which implements the basic interface that all other actors should comply with.

## BaseActor Class


### BaseActor Class

The `BaseActor` class serves as an abstract class defining the standard interface for all actors. It contains two essential methods that need to be implemented by any subclass:

#### `observe(self, observation: Event | None, source: str | None = None)`

- **Description**: Processes the given observation. The observation is expected to be a piece of information that the actor perceives from its environment, which should then be integrated into the actor's internal memory or state.

- **Parameters**:

  - `observation`: Any digestible information, likely in the form of a string or structured data, that should affect the actor's memory or state.

- **Returns**: None.

#### `query(self, prompt=None, expected_type=None) -> Any`

- **Description**: Generates a response from the actor based on the provided query and the actor's current memory or state.

- **Parameters**:
  - `prompt`: A string that contains the question or request for information to which the actor should respond.

- **Returns**: An event with string or structured data (if expected_type is provided) representing the actor's response.

Note: `BaseActor` does not prescribe a specific implementation for these methods or the structure of the memory.

### `Event` dataclass

Dataclass `Event` is defined as follows:

```python
@dataclass(frozen=True)
class Event:
    # str or any JSON-serializable type
    data: Any
    # Origin of the event, usually agent name or None (if environmental observation)
    origin: str | None = None
```

It serves as a class for exchanging observations. 
If method `observe` is called on an actor with non-event argument, then 
data automatically wrapped into an event.

Method `query` always returns an instance of `Event` where `origin` is set to the actor's name. 

Actor's name is a string that has to be provided in constructor.


### Example Usage

The `OneShotLLMActor` is a concrete implementation provided by Interlab that extends the `BaseActor`. It utilizes a language model to perform observations and queries in a one-shot manner. This actor stores all observations in its memory and considers them when making a single query through a Language Model.


```python
import langchain
from interlab.actor import OneShotLLMActor

# Create a language model instance
engine = langchain.chat_models.ChatOpenAI(model_name='gpt-3.5-turbo')

# Initialize the OneShotLLMActor with a name, language model, and initial prompt
actor = OneShotLLMActor("Alice",                                 # Actor's name
                        engine,                                  # LLM model
                        "You are Alice, expert on apples.")      # Initial prompt

# Feed observations into the actor's memory
actor.observe("Fall is coming.")
actor.observe("You see an apple tree.")

# Query the actor to generate a response
response = actor.query("What do you do with the tree?")

# Print out the response from the actor
print(response)
```

This will perform a one-shot query with the provided language model, including all previous observations within the context.
