from pydantic.dataclasses import Field, dataclass

from ..actor import BaseActor
from .base import BaseEnvironment


class PriceNegotiation(BaseEnvironment):
    def __init__(
        self,
        minimizer: BaseActor,
        maximizer: BaseActor,
        max_steps: int,
        time_push_rounds: int | None = None,
        minimizer_starts_first: bool = True,
    ):
        super().__init__([minimizer, maximizer])

        @dataclass
        class Action:
            email_text: str = Field(
                description="Email message to send to the other person"
            )
            acceptable_price: int | None = Field(
                description="If you have both agreed on the sale price, what price is acceptable to you? Otherwise leave this empty. This is not communicated to the other person.",
                default=None,
            )
            walk_away_stop_trading: bool | None = Field(
                description="Only set this to true if you want to irrevocably walk away from the negotiation. This cannot be taken back!",
                default=False,
            )

        self.n_rounds = max_steps
        self.time_push_rounds = time_push_rounds
        self.minimizer_starts_first = minimizer_starts_first
        self.action = Action

        # Last acceptable price by the other player
        self.other_acceptable_price = None

    @property
    def minimizer(self):
        return self.actors[0]

    @property
    def maximizer(self):
        return self.actors[1]

    def _advance(self):
        current = self.current_step

        if not self.minimizer_starts_first:
            me = self.actors[current % 2]
            other = self.actors[(current + 1) % 2]
        else:
            me = self.actors[(current + 1) % 2]
            other = self.actors[current % 2]

        if (
            self.time_push_rounds is not None
            and current >= self.n_rounds - self.time_push_rounds
        ):
            limit = max(1, (self.n_rounds - current) // 2)
            time_push = f" Please wrap up this conversation without sending more than {limit} more emails."
        else:
            time_push = ""

        action_result = me.query(
            f"What message should I send to {other.name}, and what else do I think or should do?{time_push}",
            expected_type=self.action,
        ).data

        me.observe(
            f"## Message from me ({me.name}) to {other.name}\n\n {action_result.email_text}"
        )
        other.observe(
            f"## Message from {me.name} to me ({other.name})\n\n{action_result.email_text}"
        )

        my_ap = action_result.acceptable_price
        other_ap = self.other_acceptable_price

        if action_result.walk_away_stop_trading:
            return "NO DEAL"
        if my_ap is not None and other_ap is not None:
            if me == self.minimizer and my_ap >= other_ap:
                return other_ap, my_ap
            if me == self.maximizer and my_ap <= other_ap:
                return my_ap, other_ap
        if current >= self.n_rounds:
            return "TIMEOUT"
        self.other_acceptable_price = my_ap
