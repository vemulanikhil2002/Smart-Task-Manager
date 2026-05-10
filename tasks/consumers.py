import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TaskConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = 'tasks'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'WebSocket connected successfully!'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        # Echo back any client message (optional keep-alive ping)
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({'type': 'pong', 'data': data}))

    # Called by broadcast() in views.py via group_send
    async def task_event(self, event):
        await self.send(text_data=json.dumps({
            'type':    event['event'],
            'payload': event['payload'],
        }))
