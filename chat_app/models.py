from django.db import models
from user_app.models import CustomUser


# Create your models here.

class ChatRoom(models.Model):
    member = models.ManyToManyField(CustomUser, related_name='member_group')
    room_name = models.CharField(max_length=100, blank=False, unique=True)
    chat_group = models.CharField(max_length=50, default='')
    creator = models.ForeignKey(CustomUser, related_name='creator', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.room_name
    
class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    room_name = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    
    message = models.JSONField()
            
    def __str__(self):
        return '%s' %(self.message['timestamp'])
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ChatRoom.objects.get(id = self.room_name.id).save()
        
    @staticmethod
    def count_overall_unread_msg(username):
        total_unread_msg = 0
        user = CustomUser.objects.filter(username=username).first()
        user_all_friends = ChatRoom.objects.filter(member=user)
        unread_data = []
        for ch_session in user_all_friends:
            un_read_msg_count = ChatMessage.objects.filter(room_name=ch_session.id, message__read=False).exclude(user=user).count()
            unread_data.append({ch_session.room_name:un_read_msg_count})
            total_unread_msg += un_read_msg_count
        return total_unread_msg, unread_data
    
    @staticmethod
    def message_read_true(message_id):
        msg_inst = ChatMessage.objects.filter(id=message_id).first()
        msg_inst.message['read'] = True
        msg_inst.save(update_fields=['message', ])
        return None
    
    @staticmethod
    def all_msg_read(room_name, username):
        chatroom = ChatRoom.objects.filter(room_name=room_name).first()
        all_msg = ChatMessage.objects.filter(room_name=chatroom)
        for msg in all_msg:
            if msg.message['read'] == False or msg.user.username == username:
                pass
            msg.message['read'] = True
            msg.save(update_fields=['message', ])
        return None
    
    @staticmethod
    def sender_inactive_msg(message_id):
        return ChatMessage.objects.filter(id=message_id).update(message__Sclr=True)
    
    @staticmethod
    def receiver_inactive_msg(message_id):
        return ChatMessage.objects.filter(id=message_id).update(message__Rclr=True)
        