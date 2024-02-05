from rest_framework import generics, status
from social_app.models import (
    OnlineBusinessCard, SNSTree,
    ContactGroup, ContactData,
    )
from social_app.serializers import (
    OnlineBusinessCardSerializer, SNSTreeSerializer,
    ContactGroupSerializer, ContactDataSerializer,
    )
from chat_app.models import (
    ChatRoom, ChatMessage,
    )
from chat_app.serializers import (
    ChatRoomSerializer, ChatMessageSerializer
    )
from Degime_backend.mixins import AppAuthPermMixin
# from django.contrib.auth.models import User
from user_app.models import CustomUser
# from django.http import JsonResponse
from rest_framework.response import Response

import json
import hashlib

def get_hash_code(text):
    hash_object = hashlib.sha256(text.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

class OnlineBusinessCardListAPIView(generics.ListAPIView):
    queryset = OnlineBusinessCard.objects.all()
    serializer_class = OnlineBusinessCardSerializer
    
    def get_queryset(self):
        queryset = OnlineBusinessCard.objects.all()
        username = self.request.query_params.get('username')
        url_name = self.request.query_params.get('url_name')
        if username:
            queryset = queryset.filter(user__username=username)
            return queryset    
        
        if url_name:
            queryset = queryset.filter(url_name=url_name)
            return queryset
        
        queryset = None
        return queryset
    
class SNSTreeListAPIView(generics.ListAPIView):
    queryset = SNSTree.objects.all()
    serializer_class = SNSTreeSerializer
    
    def get_queryset(self):
        queryset = SNSTree.objects.all()
        username = self.request.query_params.get('username')
        url_name = self.request.query_params.get('url_name')
        
        if username:
            queryset = queryset.filter(user__username=username)
            return queryset    
        
        if url_name:
            queryset = queryset.filter(url_name=url_name)
            return queryset
        
        queryset = None
        return queryset
    
class OnlineBusinessCardAPIView(AppAuthPermMixin, generics.GenericAPIView):
    queryset = OnlineBusinessCard.objects.all()    
    serializer_class = OnlineBusinessCardSerializer
        
    def get(self, request, *args, **kwargs):
        queryset = OnlineBusinessCard.objects.filter(user=request.user)
        
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        queryset = OnlineBusinessCard.objects.filter(user=request.user)
        
        avatar = request.data.get('faceImg', '')
        if avatar:
            temp = CustomUser.objects.filter(username=request.user.username).first()
            temp.avatar = avatar
            temp.save()
            
        if queryset.count() == 0:
            serializer = OnlineBusinessCardSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        serializer = OnlineBusinessCardSerializer(queryset.first(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        queryset = OnlineBusinessCard.objects.filter(user=request.user)
        
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SNSTreeAPIView(AppAuthPermMixin, generics.GenericAPIView):
    queryset = SNSTree.objects.all()    
    serializer_class = SNSTreeSerializer
        
    def get(self, request, *args, **kwargs):
        queryset = SNSTree.objects.filter(user=request.user)
        
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        queryset = SNSTree.objects.filter(user=request.user)
        
        avatar = request.data.get('faceImg', '')
        if avatar:
            temp = CustomUser.objects.filter(username=request.user.username).first()
            temp.avatar = avatar
            temp.save()
        
        if queryset.count() == 0:
            serializer = SNSTreeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        serializer = SNSTreeSerializer(queryset.first(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        queryset = SNSTree.objects.filter(user=request.user)
        
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
                        
class OnlineBusinessCardAdminAPIView(AppAuthPermMixin, generics.GenericAPIView):
    serializer_class = OnlineBusinessCardSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = OnlineBusinessCard.objects.all()
        
        if not self.request.user.is_superuser:
            queryset = queryset.none()  # Return an empty queryset
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data), 
                            status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        queryset = OnlineBusinessCard.objects.all()        
        
        if not self.request.user.is_superuser:
            queryset = queryset.none()  # Return an empty queryset
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SNSTreeAdminAPIView(AppAuthPermMixin, generics.GenericAPIView):
    serializer_class = SNSTreeSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = SNSTree.objects.all()
        
        if not self.request.user.is_superuser:
            queryset = queryset.none()  # Return an empty queryset
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data), 
                            status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        queryset = SNSTree.objects.all()        
        
        if not self.request.user.is_superuser:
            queryset = queryset.none()  # Return an empty queryset
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
        # username = request.GET.get('username')
        
class ContactGroupAPIView(AppAuthPermMixin, generics.GenericAPIView):
    queryset = ContactGroup.objects.all()    
    serializer_class = ContactGroupSerializer
        
    def get(self, request, *args, **kwargs):
        queryset = ContactGroup.objects.filter(user=request.user)
        
        if queryset.count() == 0:            
            return Response(data=[], status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        queryset = ContactGroup.objects.filter(user=request.user)
        
        old_group_Name = self.request.query_params.get('old_group')
        if old_group_Name:
            queryset = queryset.filter(group_Name=old_group_Name)
            if queryset.count() == 0:
                return Response([], status=status.HTTP_404_NOT_FOUND)
            serializer = ContactGroupSerializer(queryset.first(), data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
                
        else:            
            data = json.loads(request.body)
            group_Name = data.get('group_Name')
            queryset = ContactGroup.objects.filter(user=request.user)
            queryset = queryset.filter(group_Name=group_Name)
            if queryset.count() == 0:
                serializer = ContactGroupSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=self.request.user)            
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"Already Exist."}, status=status.HTTP_400_BAD_REQUEST)
          
    
    def delete(self, request, *args, **kwargs):
        queryset = ContactGroup.objects.filter(user=request.user)
        group_Name = self.request.query_params.get("group_Name")
        if group_Name: queryset = queryset.filter(group_Name=group_Name)
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ContactDataAPIView(AppAuthPermMixin, generics.GenericAPIView):
    queryset = ContactData.objects.all()    
    serializer_class = ContactDataSerializer
        
    def get(self, request, *args, **kwargs):
        queryset = ContactData.objects.filter(user=request.user)
        
        block_setting = self.request.query_params.get('block_setting')
        if block_setting:
            queryset = queryset.filter(block_setting=block_setting)
            
        group_Name = self.request.query_params.get('group_Name')
        if group_Name:
            queryset = queryset.filter(group_Name=group_Name)
            
        is_chat_available = self.request.query_params.get('is_chat_available')
        if is_chat_available:
            print (is_chat_available)
            queryset = ContactData.objects.filter(is_chat_available=is_chat_available)
            
        is_pending = self.request.query_params.get('is_pending')
        if is_pending:
            queryset = queryset.filter(is_pending=is_pending)
            
        is_incoming = self.request.query_params.get('is_incoming')
        if is_incoming:
            queryset = queryset.filter(is_incoming=is_incoming)

        if queryset.count() == 0:            
            return Response(data=[], status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        queryset = ContactData.objects.filter(user=request.user)
        member_data = json.loads(request.body).get('member')
        member_count = CustomUser.objects.filter(username=member_data)
        if member_count.count(): 
            member = CustomUser.objects.filter(username=member_data).first()
            queryset = queryset.filter(member=member)  
            if queryset.count() == 0:   
                group_Name = json.loads(request.body).get('group_Name')
                if not group_Name: ContactGroup.objects.create(user=request.user)
                else : ContactGroup.objects.create(user=request.user, group_Name=group_Name)
                
                serializer = ContactDataSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=self.request.user, member=member)
                ContactData.objects.create(user=member, member=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)  
        
            is_pending = self.request.query_params.get('is_pending')
            if is_pending:
                temp = ContactData.objects.filter(user=member, member=request.user).first()
                temp.is_incoming = "True"
                temp.is_profile_update = "True"
                temp.save()
                temp_group = ContactGroup.objects.filter(user=member, group_Name=temp.group_Name).first()
                temp_group.unread_profile += 1
                member.unread_person += 1
                temp = ContactData.objects.filter(user=request.user, member=member).first()
                temp.is_pending = "True"
                temp.save()
                
                
            is_chat_available = self.request.query_params.get('is_chat_available')
            if is_chat_available:
                temp = ContactData.objects.filter(user=member, member=request.user).first()
                temp.is_chat_available = "True"
                temp.is_profile_update = "False"
                temp.save()
                temp_group = ContactGroup.objects.filter(user=member, group_Name=temp.group_Name).first()
                temp_group.unread_profile -= 1
                member.unread_person -= 1
                temp = ContactData.objects.filter(user=request.user, member=member).first()
                temp.is_chat_available = "True"
                temp.save()
                chat_group = request.user.username + "_" + member.username
                room_name = get_hash_code(request.user.username + chat_group)
                chatroom_temp = ChatRoom(room_name=room_name, chat_group=chat_group, creator=request.user)
                chatroom_temp.save()
                chatroom_temp.member.add(request.user, member)
                
            
        serializer = ContactDataSerializer(queryset.first(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
          
    
    def delete(self, request, *args, **kwargs):
        queryset = ContactData.objects.filter(user=request.user)
        member_data = self.request.query_params.get('member')
        member = CustomUser.objects.filter(username=member_data).first()
        if member: queryset = queryset.filter(member=member) 
        if queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        queryset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
