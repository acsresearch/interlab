## Subclassing BaseEnvironment

To create custom environments, you must inherit from `BaseEnvironment` and implement the `_advance()` method:

```python
class MyEnv(BaseEnvironment):
    def _advance(self):
        # Implement the logic for a single step.
```

Value returns of

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