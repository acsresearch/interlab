# THIS NEEDS TO BE REWRITTEN
#
# import json
#
# from serde import to_dict
#
# from querychains import Context
# from querychains.channel import Channel, Actor
# from tests.testutils import strip_tree
#
#
# def test_send_message():
#     channel = Channel("emails")
#
#     alice = Actor("Alice")
#     bob = Actor("Bob")
#     charlie = Actor("Charlie")
#
#     channel.add_actors([alice, bob, charlie])
#
#     with Context("dialog") as dialog:
#         channel.send_message(alice, [bob], "Hello!")
#         channel.send_message(bob, [alice, charlie], "Hi Alice and Charlie\n\nBob")
#
#     output = strip_tree(to_dict(dialog))
#     print(json.dumps(output, indent=2))
#
#     assert output == {
#         "name": "dialog",
#         "children": [
#             {
#                 "name": "send_message",
#                 "data": {
#                     "sender": "Alice",
#                     "receivers": ["Bob"],
#                     "content": "Hello!",
#                     "_type": "MessageEvent",
#                 },
#                 "_type": "Event",
#             },
#             {
#                 "name": "send_message",
#                 "data": {
#                     "sender": "Bob",
#                     "receivers": ["Alice", "Charlie"],
#                     "content": "Hi Alice and Charlie\n\nBob",
#                     "_type": "MessageEvent",
#                 },
#                 "_type": "Event",
#             },
#         ],
#     }
