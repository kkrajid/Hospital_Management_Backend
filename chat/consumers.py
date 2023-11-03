

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
# from channels.db import database_sync_to_async
# from accounts.models import User
# from accounts.models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        message = data["message"]
        sender_id = data["sender_id"]
        receiver_id = data["recipient"]

        # await self.save_message(message, sender_id, receiver_id)

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "message": message,
                "sender_id": sender_id,
                "receiver_id": receiver_id
            }
        )

    async def send_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]
        receiver_id = event["receiver_id"]

        await self.send(text_data=json.dumps({
            "type": "message",
            "sender_id": sender_id,
            "recipient_id": receiver_id,
            "content": message,
        }))

    # @database_sync_to_async
    # def save_message(self, message, sender_id, receiver_id):
    #     try:
    #         sender = User.objects.get(id=int(sender_id))
    #         receiver = User.objects.get(id=int(receiver_id))
    #         message = Message.objects.create(sender=sender, receiver=receiver, content=message, timestamp=timezone.now())
    #         return message
    #     except User.DoesNotExist:
    #         return None




# import json
# from channels.consumer import AsyncConsumer
# from django.utils import timezone
# # from accounts.models import User
# # from accounts.models import Message

# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.send({
#             'type': 'websocket.accept'
#         })

#     async def websocket_disconnect(self, event):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def websocket_receive(self, event):
#         data = json.loads(event['text'])
#         message = data["message"]
#         sender_id = data["sender_id"]
#         receiver_id = data["recipient"]

#         await self.save_message(message, sender_id, receiver_id)

#         await self.channel_layer.group_send(
#             self.room_group_name, {
#                 "type": "send_message",
#                 "message": message,
#                 "sender_id": sender_id,
#                 "receiver_id": receiver_id
#             }
#         )

#     async def send_message(self, event):
#         message = event["message"]
#         sender_id = event["sender_id"]
#         receiver_id = event["receiver_id"]

#         await self.send({
#             "type": "websocket.send",
#             "text": json.dumps({
#                 "type": "message",
#                 "sender_id": sender_id,
#                 "recipient_id": receiver_id,
#                 "content": message,
#             })
#         })

#     async def save_message(self, message, sender_id, receiver_id):
#         try:
#             sender = await self.get_user_by_id(sender_id)
#             receiver = await self.get_user_by_id(receiver_id)
#             message = Message.objects.create(sender=sender, receiver=receiver, content=message, timestamp=timezone.now())
#         except User.DoesNotExist:
#             return None

#     async def get_user_by_id(self, user_id):
#         try:
#             return await self.get_user_by_id_query(user_id)
#         except User.DoesNotExist:
#             return None

#     @staticmethod
#     async def get_user_by_id_query(user_id):
#         return User.objects.get(id=user_id)


# import asyncio
# from channels.consumer import AsyncConsumer



# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self,event):
#         print('connected',event)
#         await self.send({
#             "type":"websocket.accept"
#         })

#     async def websocket_receive(self, event):
#         print('receive',event)
#         # received_data = json.loads(event['text'])
#         # msg = received_data.get('message')
#         # if msg:
#         #     response = {
#         #         'message': msg,
#         #     }
#         #     await self.send({
#         #         'type': 'websocket.send',
#         #         'text': json.dumps(response),
#         #     })



#     async def websocket_disconnect(self,event):
#         print('disconnected',event)
     

# app1/consumer.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from django.utils import timezone
# from channels.db import database_sync_to_async
# from accounts.models import User
# from accounts.models import Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data=None):
#         data = json.loads(text_data)
#         message = data["message"]
#         sender_id = data["sender_id"]
#         receiver_id = data["recipient"]

#         await self.save_message(message, sender_id, receiver_id)

#         await self.channel_layer.group_send(
#             self.room_group_name, {
#                 "type": "send_message",
#                 "message": message,
#                 "sender_id": sender_id,
#                 "receiver_id": receiver_id
#             }
#         )

#     async def send_message(self, event):
#         message = event["message"]
#         sender_id = event["sender_id"]
#         receiver_id = event["receiver_id"]

#         await self.send(text_data=json.dumps({
#             "type": "message",
#             "sender_id": sender_id,
#             "recipient_id": receiver_id,
#             "content": message,
#         }))

#     @database_sync_to_async
#     def save_message(self, message, sender_id, receiver_id):
#         try:
#             sender = User.objects.get(id=int(sender_id))
#             receiver = User.objects.get(id=int(receiver_id))
#             message = Message.objects.create(sender=sender, receiver=receiver, content=message, timestamp=timezone.now())
#             return message
#         except User.DoesNotExist:
            
#             return None


# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.utils import timezone
# from accounts.models import User
# from accounts.models import Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data["message"]
#         sender_id = data["sender_id"]
#         receiver_id = data["recipient"]

#         await self.save_message(message, sender_id, receiver_id)

#         await self.channel_layer.group_send(
#             self.room_group_name, {
#                 "type": "send_message",
#                 "message": message,
#                 "sender_id": sender_id,
#                 "receiver_id": receiver_id
#             }
#         )

#     async def send_message(self, event):
#         message = event["message"]
#         sender_id = event["sender_id"]
#         receiver_id = event["receiver_id"]

#         await self.send(text_data=json.dumps({
#             "type": "message",
#             "sender_id": sender_id,
#             "recipient_id": receiver_id,
#             "content": message,
#         }))

#     async def save_message(self, message, sender_id, receiver_id):
#         try:
#             sender = await self.get_user_by_id(sender_id)
#             receiver = await self.get_user_by_id(receiver_id)
#             message = Message.objects.create(sender=sender, receiver=receiver, content=message, timestamp=timezone.now())
#         except User.DoesNotExist:
#             return None

#     async def get_user_by_id(self, user_id):
#         try:
#             return await self.get_user_by_id_query(user_id)
#         except User.DoesNotExist:
#             return None

#     @staticmethod
#     async def get_user_by_id_query(user_id):
#         return User.objects.get(id=user_id)
