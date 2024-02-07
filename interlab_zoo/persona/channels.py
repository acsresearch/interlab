from dataclasses import dataclass


@dataclass
class Channel:
    name: str
    message_name: str
    message_header: str

    def _create_message(self, sender, receivers, body, me):
        header = self.message_header
        header = header.replace("$sender", self.make_name(sender, me))
        header = header.replace(
            "$receivers", ",".join(self.make_name(r, me) for r in receivers)
        )
        return header + body

    @staticmethod
    def make_name(persona, me) -> str:
        if persona == me:
            return persona.name + " (me)"
        else:
            return persona.name

    def query_and_send_message(self, sender, receiver, observers=None):
        self.query_and_send_message_to_all(sender, [receiver], observers)

    def query_and_send_message_to_all(self, sender, receivers, observers=None):
        names = ",".join(r.name for r in receivers)
        text = sender.query(f"Create {self.message_name} to {names}.")
        sender.observe(self._create_message(sender, receivers, text, sender))
        for receiver in receivers:
            receiver.observe(self._create_message(sender, receivers, text, receiver))
        if observers:
            for actor in observers:
                actor.observe(self._create_message(sender, receivers, text, actor))


ChatChannel = Channel(
    "chat", "a chat message", "## A chat message from $sender to $receivers:\n"
)
