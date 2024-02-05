from rest_framework import generics, status
from chat_app.models import (
    ChatRoom, ChatMessage,
    )
from chat_app.serializers import (
    ChatRoomSerializer, ChatMessageSerializer
    )
from social_app.models import (
    OnlineBusinessCard, SNSTree,
    ContactGroup, ContactData,
    )
from social_app.serializers import (
    OnlineBusinessCardSerializer, SNSTreeSerializer,
    ContactGroupSerializer, ContactDataSerializer,
    )
from Degime_backend.mixins import AppAuthPermMixin
from django.contrib.auth.models import User
from user_app.models import CustomUser
from django.http import JsonResponse
from rest_framework.response import Response

import json
import hashlib

def get_hash_code(text):
    hash_object = hashlib.sha256(text.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

class ChatRoomAPIView(AppAuthPermMixin, generics.GenericAPIView):
    queryset = ChatRoom.objects.all()    
    serializer_class = ChatRoomSerializer
    
    def get(self, request, *args, **kwargs):
        
        room_name = self.request.query_params.get('room_name')
        if room_name:
            queryset = ChatRoom.objects.filter(room_name=room_name)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        queryset = ChatRoom.objects.filter(member=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        queryset = ChatRoom.objects.filter(member=request.user)
        
        if queryset.count() == 0:   
            chat_group = json.loads(request.body).get('chat_group')
            members = json.loads(request.body).get('member')
            room_name = get_hash_code(request.user.username + chat_group)
            chatroom_temp = ChatRoom(room_name=room_name, chat_group=chat_group, creator=request.user)
            chatroom_temp.save()
            for member in members:
                user = CustomUser.objects.filter(username=member).first()
                chatroom_temp.member.add(user)
            chatroom_temp.member.add(request.user)
            return Response({"Successfully Created!"}, status=status.HTTP_201_CREATED)  
        
        old_room_name = self.request.query_params.get('old_room_name')
        if old_room_name:
            temp = queryset.filter(room_name=old_room_name).first()
            new_chat_group = json.loads(request.body).get('chat_group')
            new_room_name = get_hash_code(request.user.username + new_chat_group)
            temp.room_name = new_room_name
            temp.chat_group = new_chat_group
            temp.save()
            return Response({"Successfully Changed!"}, status=status.HTTP_200_OK)
        
        new_room = self.request.query_params.get('new_room')
        if new_room:
            new_chat_group = json.loads(request.body).get('chat_group')
            new_room_name = get_hash_code(request.user.username + new_chat_group)
            queryset = ChatRoom.objects.filter(room_name=new_room_name)
            if queryset.count():
                return Response({"There is already such Chatroom!"}, status=status.HTTP_400_BAD_REQUEST)
            chatroom_temp = ChatRoom(room_name=new_room_name, chat_group=new_chat_group, creator=request.user)
            chatroom_temp.save()
            members = json.loads(request.body).get('member')
            for member in members:
                user = CustomUser.objects.filter(username=member).first()
                chatroom_temp.member.add(user)
            chatroom_temp.member.add(request.user)
            chatroom_temp.save()
            return Response({"Successfully Created!"}, status=status.HTTP_201_CREATED)
        
        new_member_name = self.request.query_params.get('new_member')    
        if new_member_name:
            room_name = json.loads(request.body).get('room_name')
            temp = ChatRoom.objects.filter(room_name=room_name).first()
            new_member = CustomUser.objects.filter(username=new_member_name).first()
            if temp.member.filter(id=new_member.id).exists():
                return Response({"There is already such member in chatroom."}, status=status.HTTP_400_BAD_REQUEST)
            temp.member.add(new_member)
            temp.save()
            return Response({"New Memeber is added."}, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
          
    
    def delete(self, request, *args, **kwargs):   
        queryset = ChatRoom.objects.filter(member=request.user)
        
        room_name = self.request.query_params.get('room_name')
        if room_name: 
            queryset = ChatRoom.objects.filter(room_name=room_name)
            temp = queryset.first().member
            members = []
            if temp.count() == 2:
                all_member = temp.all()
                for member in all_member: members.append(member)
                temp = ContactData.objects.filter(user=members[0], member=members[1]).first()
                temp.is_chat_available = "False"
                temp.is_pending = "False"
                temp.is_incoming = "Flase"
                temp.save()
                temp = ContactData.objects.filter(user=members[1], member=members[0]).first()
                temp.is_chat_available = "False"
                temp.is_pending = "False"
                temp.is_incoming = "Flase"
                temp.save()
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        member_name = self.request.query_params.get('delete_member')
        if member_name:
            member = CustomUser.objects.filter(username=member_name).first()
            room_name = json.loads(request.body).get('room_name')
            temp = ChatRoom.objects.filter(room_name=room_name).first()
            temp.member.remove(member)
            return Response({"Successfully Removed."}, status=status.HTTP_202_ACCEPTED)
        
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class ChatMessageAPIView(AppAuthPermMixin, generics.GenericAPIView):
#     queryset = ChatRoom.objects.all()    
#     serializer_class = ChatMessageSerializer
    
#     def get (self, request, *args, **kwargs):
        
#         room_name = self.request.query_params.get('room_name')
#         chatroom = ChatRoom.objects.filter(room_name=room_name).first()
#         # num = self.request.query_params.get('num')
        
#         if room_name:
#             queryset = ChatMessage.objects.filter(room_name_id=chatroom.id, user=request.user)
#             # if num:
#             #     queryset = reversed(queryset)[num:]
#             serializer = self.get_serializer(queryset, many=True)
#             print (1)
#             return Response(serializer.data, status==status.HTTP_200_OK)
        
#         return Response(status=status.HTTP_400_BAD_REQUEST)
        
        