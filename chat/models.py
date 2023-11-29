from django.db import models
from accounts.models import User


class Room(models.Model):
    slug = models.SlugField(unique=True)


    def __str__(self):
        return self.slug

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    
