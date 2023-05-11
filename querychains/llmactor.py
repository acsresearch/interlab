# THIS NEEDS TO BE REWRITTEN
#
#
# from dataclasses import dataclass, field
# from typing import Callable, List
#
# from querychains import QueryEngine
# from querychains.channel import Actor, Message
#
# from querychains.text import replace, ensure_newline
#
#
# @dataclass
# class LlmActor(Actor):
#     name: str
#     main_prompt: str
#     llm: QueryEngine
#
#     history_view: Callable[["LlmActor"], str]
#     messages: List["Message"] = field(default_factory=list)
#
#     def add_message(self, message: Message):
#         self.messages.append(message)
#
#     def build_prompt(self, command):
#         replacements = {"$NAME": self.name, "$HISTORY": self.history_view(self)}
#         prompt = replace(self.main_prompt, replacements)
#         prompt = ensure_newline(prompt, 2)
#         return prompt + replace(command, replacements)
#
#     def query(self, command):
#         return self.llm.query(self.build_prompt(command))
