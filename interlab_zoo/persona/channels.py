from dataclasses import dataclass


@dataclass
class Channel:
    name: str
    message_name: str = "a message"
    message_header: str = "Message from $sender to $receiver:"

    def _create_message(self, sender_name, receiver_name, body):
        header = self.message_header
        header = header.replace("$sender", sender_name)
        header = header.replace("$receiver", receiver_name)
        return header + body

    def query_and_send_message(self, sender, receiver, observers=None):
        text = sender.query(f"Create {self.message_name} to {receiver.name}.")
        sender.observe(self._create_message(sender.name + " (me)", receiver.name, text))
        receiver.observe(
            self._create_message(sender.name, receiver.name + " (me)", text)
        )
        if observers:
            for actor in observers:
                actor.observe(self._create_message(sender.name, receiver.name, text))


ChatChannel = Channel("chat", "a chat message", "Message from $sender to $receiver:")
