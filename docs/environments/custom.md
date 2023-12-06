## Subclassing BaseEnvironment

To create custom environments, you must inherit from `BaseEnvironment` and implement the `_step()` method:

```python
class MyEnv(BaseEnvironment):
    def _step(self):
        # Implement the logic for a single step.
        # Should return None if the environment isn't finished.
        # Otherwise, return a result object.
```

### Implementing the "copy" method

Default copy methods makes a shallow copy of all attributes (except actors). A shallow copy may not be sufficient for all environments, especially if the environment contains mutable objects. You can override the "copy" method to ensure a proper copy is made:

```python
    class MyEnv(BaseEnvironment):
        def __init__(self, ...):
            ...
            self.shallow_copyable_argument = 5.0
            self.my_list = []

        ...

        def copy(self):
            env = super().copy()            # Call the original `copy` method.
            env.my_list = self.my_list[:]   # Make a copy of the list.
            return env
```

### Additional Overrides

- `current_actor` - If there's a clear "actor" for each step, you can override this property to indicate who the current actor is.
- `current_step_style` - You may customize the style for the context of each step by overriding this property.
