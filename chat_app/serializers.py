from rest_framework import serializers
from chat_app.models import ChatRoom, ChatMessage
# from django.contrib.auth.models import User
from user_app.models import CustomUser
from user_app.serializers import UserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    member = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = '__all__'
        
class ChatMessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # room_name = serializers.ReadOnlyField(source='chatroomroom_name')
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
        extra_kwargs = {
            'user': {'queryset': CustomUser.objects.all()}
        }


