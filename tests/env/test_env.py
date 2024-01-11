from interlab.environment import BaseEnvironment


def test_environment_until_end():
    class SimpleEnv(BaseEnvironment):
        def _advance(self):
            if self.current_step == 3:
                self.set_result("Result")

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


def test_environment_advance_result():
    class SimpleEnv(BaseEnvironment):
        def _advance(self):
            return self.current_step * 10

    env = SimpleEnv([])
    assert not env.is_finished()

    assert env.advance() == 10
    assert env.advance() == 20
    assert env.advance() == 30
