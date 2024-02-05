from django.urls import path, include
from chat_app.views import (
    ChatRoomAPIView, # ChatMessageAPIView,
    )


urlpatterns = [
    #   private user
    #   'private/chatroom'                          GET     user's room list    DLELETE all rooms
    #   'private/chatroom?room_name=room_name'      GET     room's user list    DELETE room
    #   'private/chatroom'                          PUT     create first room
    #   'private/chatroom?old_room_name=old_name'   PUT     change room's name
    #   'private/chatroom?new_room=True'            PUT     create new room
    #   'private/chatroom?new_member=membername'    PUT     put new member in chat room
    #   'private/chatroom?delete_member=membername'        DELETE  delete certain member from chat room
    path('private/chatroom', ChatRoomAPIView.as_view(), name='chat-room'),
    
    # path('private/chatmessage', ChatMessageAPIView.as_view(), name='chat-message')
]