## Subclassing BaseEnvironment

To create custom environments, you must inherit from `BaseEnvironment` and implement the `_advance()` method 
and `copy()` method:

```python
class MyEnv(BaseEnvironment):
    def _advance(self):
        # Implement the logic for a single step.
```