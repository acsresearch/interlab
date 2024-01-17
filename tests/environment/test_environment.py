from interlab.environment import BaseEnvironment


def test_basic_environment():
    class SimpleEnv(BaseEnvironment):
        def _step(self, foo=0):
            if self.steps == 3:  # Actually the 4th call
                self.set_finished()
            return foo + 1

    env = SimpleEnv()
    assert env.step(41) == 42
    assert env.steps == 1
    env2 = env.copy()

    assert not env.is_finished
    while not env.is_finished:
        env.step()
    assert env.is_finished
    assert env.steps == 4  # 3 + 1

    assert not env2.is_finished
    assert env2.steps == 1
