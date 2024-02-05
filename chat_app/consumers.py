
# chat/consumers.py
import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
import uuid
from chat_app.models import ChatMessage, ChatRoom
from social_app.models import ContactData, ContactGroup
from django.contrib.auth.models import User
from user_app.models import CustomUser


MESSAGE_MAX_LENGTH = 1200

MESSAGE_ERROR_TYPE = {
    "MESSAGE_OUT_OF_LENGTH": 'MESSAGE_OUT_OF_LENGTH',
    "UN_AUTHENTICATED": 'UN_AUTHENTICATED',
    "INVALID_MESSAGE": 'INVALID_MESSAGE',
}

MESSAGE_TYPE = {
    "WENT_ONLINE": 'WENT_ONLINE',
    "WENT_OFFLINE": 'WENT_OFFLINE',
    "IS_TYPING": 'IS_TYPING',
    "NOT_TYPING": 'NOT_TYPING',
    "MESSAGE_COUNTER": 'MESSAGE_COUNTER',
    "OVERALL_MESSAGE_COUNTER": 'OVERALL_MESSAGE_COUNTER',
    "TEXT_MESSAGE": 'TEXT_MESSAGE',
    "MESSAGE_READ": 'MESSAGE_READ',
    "ALL_MESSAGE_READ": 'ALL_MESSAGE_READ',
    "PROFILE_UPDATED": "PROFILE_UPDATED",
    "PROFILE_READ": "PROFILE_READ",
    "SEND_REQUEST": "SEND_REQUEST",
    "ALLOW_REQUEST": "ALLOW_REQUEST",
    "ERROR_OCCURED": 'ERROR_OCCURED'
}

class PersonalConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name'] #
        self.room_group_name = 'personal__%s' % self.room_name
                
        token = self.scope['url_route']['kwargs']['token']
        username = self.scope['url_route']['kwargs']['username']
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )      
        
        self.user = CustomUser.objects.filter(username=username).first()
        user_token = str(self.user.auth_token)
        if token == user_token:              

            self.accept()
            
            self.send(text_data=json.dumps({                
                'is_Connected': "True",
                'sender': self.user.username
            }))
                
        else:           
            self.close(code=4001)
            
    def disconnect(self, code):
        self.set_offline()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        
    def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('msg_type')
        user_name = data.get('user_name')
        
        if msg_type == MESSAGE_TYPE['WENT_ONLINE']:
            user_name_list = self.set_online(user_name)
            for friend_user  in user_name_list:
                async_to_sync(self.channel_layer.group_send)(
                    'personal__%s' % friend_user,{
                        'type': 'user_online',
                        'user_name': self.user.username
                    }
                )
        
        elif msg_type == MESSAGE_TYPE['WENT_OFFLINE']:
            user_name_list = self.set_offline(user_name)
            for friend_user in user_name_list:
                async_to_sync(self.channel_layer.group_send(
                    'personal__%s' % friend_user,{
                        'type': 'user_offline',
                        'user_name': self.user.username
                    }
                ))
                
        elif msg_type == MESSAGE_TYPE['PROFILE_UPDATED']:
            user_name_list = self.profile_notify(user_name)
            for friend_user, friend_group in user_name_list:
                async_to_sync(self.channel_layer.group_send(
                    'personal__%s' % friend_user,{
                        'type': 'profile_update',
                        'user_name': self.user.username,
                        'friend_group': friend_group
                    }
                ))
                
        elif msg_type == MESSAGE_TYPE['PROFILE_READ']:
            friend_name = data.get('friend_name')
            self.read_profile(user_name, friend_name)
            async_to_sync(self.channel_layer.group_send(
                'personal__%s' % friend_name,{
                    'type': 'profile_read',
                    'user_name': self.user.username
                }
            ))
            
        elif msg_type == MESSAGE_TYPE['SEND_REQUEST']:
            friend_name = data.get('friend_name')
            user_name = data.get('user_name')
            async_to_sync(self.channel_layer.group_send(
                'personal__%s' % friend_name,{
                    'type': 'request_notify',
                    'user_name': self.user.username
                }
            ))
            
        elif msg_type == MESSAGE_TYPE['ALLOW_REQUEST']:
            friend_name = data.get('friend_name')
            user_name = data.get('user_name')
            async_to_sync(self.channel_layer.group_send(
                'personal__%s' % friend_name,{
                    'type': 'allow_request',
                    'user_name': self.user.username
                }
            ))
        
    def user_online(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['WENT_ONLINE'],
            "user_name": EnvironmentError['user_name']
        }))
        
    def message_counter(self, event):
        overall_unread_msg, unread_data = self.count_unread_overall_msg(event['user_name'])
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['MESSAGE_COUNTER'],
            "overall_unread_msg": overall_unread_msg,
            "unread_data": unread_data,
            "unread_room": len(unread_data)
        }))
    
    def user_offline(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['WENT_OFFLINE'],
            "user_name": event['user_name']
        }))
        
    def profile_update(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['PROFILE_UPDATED'],
            "user_name": event['user_name'],
            "friend_group": event['friend_group']
        }))
        
    def profile_read(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['PROFILE_READ'],
            "user_name": event['user_name']
        }))
        
    def request_notify(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['SEND_REQUEST'],
            "user_name": event['user_name']
        }))
        
    def allow_request(self, event):
        self.send(text_data=json.dumps({
            "msg_type": MESSAGE_TYPE['ALLOW_REQUEST'],
            "user_name": event['user_name']
        }))
        
    # @database_sync_to_async
    def set_online(self, user_name):
        user = CustomUser.objects.filter(username=user_name).first()
        user.is_online = True
        chatrooms = ChatRoom.objects.filter(member=user)
        user_name_list = []
        for chatroom in chatrooms:
            members = chatroom.member
            for member in members:
                if member.username == user.username:
                    pass
                user_name_list.append(member.username)
        return user_name_list
    
    # @database_sync_to_async
    def set_offline(self, user_name):
        user = CustomUser.objects.filter(username=user_name).first()
        user.is_online = False
        chatrooms = ChatRoom.objects.filter(member=user)
        user_name_list = []
        for chatroom in chatrooms:
            members = chatroom.member
            for member in members:
                if member.username == user.username:
                    pass
                user_name_list.append(member.username)
        return user_name_list
    
    # @database_sync_to_async
    def profile_notify(self, user_name):
        user = CustomUser.objects.filter(username=user_name).first()
        friends = ContactData.objects.filter(member=user)
        user_name_list = []
        for friend in friends:
            if friend.block_setting == "Unannounce" or friend.block_setting == "Block" or friend.block_setting == "Deleted":
                pass
            user_name_list.append({f"{friend.username}": f"{friend.group_Name}"})
            friend.is_profile_update = "True"
            friend_group = ContactGroup.objects.filter(user=friend, group_Name=friend.group_Name).first()
            friend_group.unread_profile += 1
            friend.user.unread_person += 1
        return user_name_list
    
    # @database_sync_to_async
    def read_profile(self, user_name, friend_name):
        user = CustomUser.objects.filter(username=user_name).first()
        friend = CustomUser.objects.filter(username=friend_name).first()
        user_contactdata = ContactData.objects.filter(user=user, member=friend).first()
        user_contactdata.is_profile_update = "False"
        user_group = ContactGroup.objects.filter(user=user, group_Name=user_contactdata.group_Name).first()
        user_group.unread_profile -= 1
        user.unread_person -= 1
        return None
    
    # @database_sync_to_async
    def count_unread_overall_msg(self, username):
        return ChatMessage.count_overall_unread_msg(username=username)

class TextRoomConsumer(WebsocketConsumer):
    def connect(self):
        # gets 'room_name' and open websocket connection
        self.room_name = self.scope['url_route']['kwargs']['room_name'] #
        self.room_group_name = 'chat_%s' % self.room_name
        
        token = self.scope['url_route']['kwargs']['token']
        username = self.scope['url_route']['kwargs']['username']
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )      
        
        self.user = CustomUser.objects.filter(username=username).first()
        user_token = str(self.user.auth_token)
        if token == user_token:              

            self.accept()
            self.send(text_data=json.dumps({                
                    'is_Connected': "True",
                    'sender': self.user.username
                }))
            
            chatroom = ChatRoom.objects.filter(room_name=self.room_name).first()
            # Send last 20 messages to the client upon connection
            last_messages = ChatMessage.objects.filter(room_name=chatroom)
            for message in reversed(last_messages):
                self.send(text_data=json.dumps({                
                    'msg': message.message,
                    'sender': self.user.username
                }))
                
        else:            
            self.accept()
            self.send(text_data=json.dumps({
                "msg_type": MESSAGE_TYPE['ERROR_OCCURED'],
                "error_message": MESSAGE_ERROR_TYPE["UN_AUTHENTICATED"],
                "user": username,
            }))
            self.close(code=4001)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        
    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        msg_type = data.get('msg_type')
        username = data.get('user')
        user = CustomUser.objects.filter(username=username).first()
        if msg_type == MESSAGE_TYPE['TEXT_MESSAGE']:
            if len(message) <= MESSAGE_MAX_LENGTH:
                msg_id = uuid.uuid4()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,{
                        'type': 'chat_message',
                        'message': message,
                        'user': username,
                        'msg_id': str(msg_id)
                    }
                )
                members = self.save_text_message(msg_id, message, user)
                for member in members:
                    async_to_sync(self.channel_layer.group_send)(
                        f'personal__{member.username}',
                        {
                            'type': 'message_counter',
                            'user_name' : member.username,
                        }
                    )
            else: 
                self.send(text_data=json.dumps({
                    'msg_type': MESSAGE_TYPE['ERROR_OCCURED'],
                    "error_message": MESSAGE_ERROR_TYPE['MESSAGE_OUT_OF_LENGTH'],
                    "message": message,
                    "user": username,
                    "timestampe": str(datetime.now()),
                }))
                
        elif msg_type == MESSAGE_TYPE['MESSAGE_READ']:
            msg_id = data['msg_id']
            self.msg_read(msg_id)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'msg_as_read',
                    'msg_id': msg_id,
                    'user': username
                }
            )
        
        elif msg_type == MESSAGE_TYPE['ALL_MESSAGE_READ']:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'all_msg_read',
                    'user': username,
                }
            )
            print (self.room_name)
            print (username)
            self.read_all_msg(self.room_name, username)
            
        elif msg_type == MESSAGE_TYPE['IS_TYPING']:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'user_is_typing',
                    'user': username,
                }
            )
            
        elif msg_type == MESSAGE_TYPE['NOT_TYPING']:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'user_not_typing',
                    'user': username,
                }
            )
            
    # Receive message from room group
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['TEXT_MESSAGE'],
            'message': event['message'],
            'user': event['user'],
            'timestampe': str(datetime.now()),
            'msg_id': event['msg_id']
        }))
        
    def msg_as_read(self, event):
        self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['MESSAGE_READ'],
            'msg_id': event['msg_id'],
            'user' : event['user']
        }))
    
    def all_msg_read(self,event):
        self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['ALL_MESSAGE_READ'],
            'user' : event['user']
        }))

    def user_is_typing(self,event):
        self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['IS_TYPING'],
            'user' : event['user']
        }))

    def user_not_typing(self,event):
        self.send(text_data=json.dumps({
            'msg_type': MESSAGE_TYPE['NOT_TYPING'],
            'user' : event['user']
        }))
        
    # @database_sync_to_async
    def save_text_message(self, msg_id, message, user):
        session = ChatRoom.objects.filter(room_name=self.room_name).first()
        message_json = {            
            "msg": message,
            "read": False,
            "timestamp": str(datetime.now()),
        }
        ChatMessage.objects.create(id=msg_id, room_name=session, user=user, message=message_json)
        return session.member.all()
    
    # @database_sync_to_async
    def msg_read(self, msg_id):
        return ChatMessage.message_read_true(msg_id)
    
    # @database_sync_to_async
    def read_all_msg(self, room_name, username):
        return ChatMessage.all_msg_read(room_name, username)