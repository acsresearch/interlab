# THIS NEEDS TO BE REWRITTEN
#
#
# from dataclasses import dataclass
# from typing import Dict, List, Sequence
# from querychains.context import add_event
#
#
from typing import Optional, List, Sequence, Dict

from dataclasses import field, dataclass

import uuid

from .context import add_event


@dataclass
class Actor:
    name: str
    kind: Optional[str] = field(default=None)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Message:
    sender: Actor
    receivers: List["Actor"]
    content: str
    kind: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


class Channel:
    def __init__(
        self,
        *,
        actors: Sequence[Actor]
    ):
        self.uuid = str(uuid.uuid4())
        self.actors: Dict[Actor] = {actor.uuid: actor for actor in actors}
        self.messages = []

    def __log__(self):
        return {"uuid": self.uuid}

    def send(self, message: Message):
        assert message.sender.uuid in self.actors
        assert [actor.uuid in self.actors for actor in message.receivers]
        add_event(f"Message -> {message.sender.name} -> {','.join(a.name for a in message.receivers)}", kind="message",
                  data={"channel": self.uuid, "message": message})


#
#
# @dataclass
# class SendEvent:
#     sender: str
#     receivers: List[str]
#     content: str
#
#
# @dataclass
# class Message:
#     sender: "Actor"
#     receivers: List["Actor"]
#     content: str
#
#     def to_event(self) -> SendEvent:
#         return SendEvent(
#             sender=self.sender.name,
#             receivers=[r.name for r in self.receivers],
#             content=self.content,
#         )
#
#
# class Channel:
#     def __init__(self, name):
#         self.name = name
#         self.messages = []
#         self.actors: Dict[str, Actor] = {}
#
#     def add_actor(self, actor: Actor):
#         assert actor.name not in self.actors
#         self.actors[actor.name] = actor
#
#     def add_actors(self, actors: Sequence[Actor]):
#         for actor in actors:
#             self.add_actor(actor)
#
#     def send_message(
#         self, sender: Actor, receivers: List[Actor], content: str
#     ) -> Message:
#         assert receivers
#         assert len(set(id(r) for r in receivers)) == len(receivers)
#         assert sender not in receivers
#         assert sender.name in self.actors
#         assert all(r.name in self.actors for r in receivers)
#
#         message = Message(sender, receivers, content)
#         add_event("send_message", message.to_event())
#         self.messages.append(message)
#         message.sender.add_message(message)
#         for receiver in message.receivers:
#             receiver.add_message(message)
#         return message
