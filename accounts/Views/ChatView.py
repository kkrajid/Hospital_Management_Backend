from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from chat.models import Room, Message
# Create your views here.
def fetch_messages(request, room_slug):
    room = get_object_or_404(Room, slug=room_slug)
    messages = Message.objects.filter(room=room).order_by('timestamp')

    message_data = []
    for message in messages:
        message_data.append({
            'username': message.user.id,
            'message': message.content,
            'timestamp': message.timestamp.isoformat(),
        })

    return JsonResponse(message_data, safe=False)