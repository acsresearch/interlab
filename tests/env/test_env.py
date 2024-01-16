from interlab.environment import BaseEnvironment


def test_basic_environment():
    class SimpleEnv(BaseEnvironment):
        def _advance(self, foo=0):
            if self.advance_counter == 3:  # Actually the 4th call
                self.set_finished()
            return foo + 1

    env = SimpleEnv(["Dummy agent"])
    assert env.advance(41) == 42
    assert env.advance_counter == 1
    assert len(env.actors) == 1
    env2 = env.copy()

    assert not env.is_finished
    while not env.is_finished:
        env.advance()
    assert env.is_finished
    assert env.advance_counter == 4  # 3 + 1

    assert not env2.is_finished
    assert env2.advance_counter == 1
