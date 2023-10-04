from typing import Sequence

from interlab.actor import ActorBase
from .environment import RoundRobinEnv
from pydantic.dataclasses import dataclass, Field


class Negotiation(RoundRobinEnv):

    def __init__(
        self,
        actors: Sequence[ActorBase],
        item: str,
        currency: str = "dollars",
        message_desc: str | None = None,
        acceptable_price_desc : str | None = None,
        walk_away_desc: str | None = None,
        market_price_desc: str | None = None,
    ):
        assert len(actors) == 2

        message_desc = message_desc or "Email message to send to the other person"
        acceptable_price_desc = acceptable_price_desc or "If you have both agreed on the sale price, what price is acceptable to you? Otherwise leave this empty. This is not communicated to the other person."
        walk_away_desc = walk_away_desc or "Only set this to true if you want to irrevocably walk away from the negotiation. This cannot be taken back!"
        market_price_desc = market_price_desc or f"Your unbiased best-guess estimate of the market value of the {item} in {currency}. This is not communicated to the other person."

        @dataclass
        class Action:
            message_text: str = Field(
                description=message_desc)
            private_market_price_estimate: int = Field(
                description=market_price_desc)
            acceptable_price: int | None = Field(
                description=acceptable_price_desc,
                default=None)
            walk_away_stop_trading: bool | None = Field(
                description=walk_away_desc,
                default=False)

        self.action_class = Action

        super().__init__(actors)

    def create_prompt(self):
        pass
