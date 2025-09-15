from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_user_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user{user_id}",  
        {
            'type': 'send_notification',
            'message': message,
        }
    )
