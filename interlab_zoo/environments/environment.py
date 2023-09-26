

class Environment:

    def __init__(self, n_actors: int):
        self.n_actors = n_actors

    def initial_situation(self) -> "Situation":
        raise NotImplementedError

