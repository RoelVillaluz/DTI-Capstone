import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting user:", self.scope["user"])
        if self.scope["user"].is_authenticated:
            self.group_name = f"notifications_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            print("User not authenticated, closing socket")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Optional: echo back
        await self.send(text_data=json.dumps({'message': data.get('message')}))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))