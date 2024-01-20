## Subclassing BaseEnvironment

To create custom environments, you shold inherit from `BaseEnvironment` and implement the `_step_()`:

```python
class MyEnv(BaseEnvironment):
    def _step(self):
        # Implement the logic for a single step.
```

If a deep copy is not optimal for you, you may also write your own implementation of `copy()` method.