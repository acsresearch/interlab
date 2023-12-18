from interlab.environment import BaseEnvironment


def test_environment():
    class SimpleEnv(BaseEnvironment):
        def _step(self):
            if self.current_step == 3:
                return "Result"

    env = SimpleEnv([])
    assert not env.is_finished()

    assert env.run_until_end() == "Result"
    assert env.is_finished()
    assert env.current_step == 3
    assert env.result == "Result"

    env = SimpleEnv([])
    assert env.run_until_end(max_steps=10) == "Result"
    assert env.is_finished()
    assert env.current_step == 3
    assert env.result == "Result"

    env = SimpleEnv([])
    assert env.run_until_end(max_steps=2) is None
    assert not env.is_finished()
    assert env.current_step == 2
    assert env.result is None
