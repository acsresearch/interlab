from interlab.environment import BaseEnvironment


def test_environment():
    class SimpleEnv(BaseEnvironment):
        def _advance(self):
            if self.current_step == 3:
                self.set_finished()

    env = SimpleEnv([])
    assert not env.is_finished()

    assert env.run_until_end()
    assert env.is_finished()
    assert env.current_step == 3

    env = SimpleEnv([])
    assert env.run_until_end(max_steps=10)
    assert env.is_finished()
    assert env.current_step == 3

    env = SimpleEnv([])
    assert not env.run_until_end(max_steps=2)
    assert not env.is_finished()
    assert env.current_step == 2
