from django.urls import path, include
from social_app.views import (
    OnlineBusinessCardListAPIView, SNSTreeListAPIView,
    OnlineBusinessCardAPIView, SNSTreeAPIView,
    OnlineBusinessCardAdminAPIView, SNSTreeAdminAPIView,
    ContactGroupAPIView, ContactDataAPIView,
    )

urlpatterns = [
    #   public  GET social data
    #   "public/.../?username=username1", 
    #   "public/.../?url_name=username1url"
    path('public/online', OnlineBusinessCardListAPIView.as_view(), name='public-onlinecard'),
    path('public/snstree', SNSTreeListAPIView.as_view(), name='public-snstree'),
    
    #   private admin  GET DELETE all social data
    path('private/online/all', OnlineBusinessCardAdminAPIView.as_view(), name='admin-onlinecard'),
    path('private/snstree/all', SNSTreeAdminAPIView.as_view(), name='admin-snstree'),
    
    #   private user GET PUT DELETE social data
    path('private/online', OnlineBusinessCardAPIView.as_view(), name='private-onlinecard'),
    path('private/snstree', SNSTreeAPIView.as_view(), name='private-snstree'),
    
    #   private user GET PUT DELETE    user contact group
    #   "private/contactgroup/?old_group=friend"    PUT(update)
    #   "private/contactgroup/"    GET PUT(create) DELETE
    path('private/contactgroup', ContactGroupAPIView.as_view(), name='contact-group'),
    
    #   private user GET PUT DELETE    user contact data
    #   "private/contactdata?member=user1"    DELETE(member=user1)
    #   "private/contactdata"    DELETE all
    #   "private/contactdata?block_setting=Block"      GET blocked members
    #   "private/contactdata?group_Name=Business"       GET business members
    #   "private/contactdata?is_chat_available=1"      GET chat available members  PUT my data and members data update
    #   "private/contactdata?is_pending=True"             GET pending members         PUT(user, member only) my data and member's data
    #   "private/contactdata?is_incoming=1"            GET incoming members
    path('private/contactdata', ContactDataAPIView.as_view(), name='contact-data'),
    
]