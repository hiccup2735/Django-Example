from django.db import models
from user_app.models import CustomUser

class OnlineBusinessCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    url_name = models.CharField(max_length=50, unique=True, blank=False) 
    faceImg = models.URLField(blank=True, default='')
    realName = models.CharField(max_length=50, blank=True, default='')
    company_url = models.CharField(max_length=100, blank=True, default='')
    companyName = models.CharField(max_length=100, blank=True, default='')
    position = models.CharField(max_length=100, blank=True, default='')
    phoneNumber = models.CharField(max_length=50, blank=True, default='')
    mobilePhoneNumber = models.CharField(max_length=50, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    bgColor = models.CharField(max_length=100, blank=True, default='')
    bgURL = models.CharField(max_length=100, blank=True, default='')
    wordColor = models.CharField(max_length=100, blank=True, default='')
    cardColor = models.CharField(max_length=100, blank=True, default='')
    cardURL = models.CharField(max_length=100, blank=True, default='')
    
    idCard = models.JSONField(blank=True, default=dict)
    socialLink = models.JSONField(blank=True, default=dict)
    onlineCard_Data = models.JSONField(blank=True, default=dict)
    
class SNSTree(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    url_name = models.CharField(max_length=50, unique=True, blank=False) 
    faceImg = models.CharField(max_length=255, blank=True, default='') 
    accountName = models.CharField(max_length=50, blank=True, default='')
    profile = models.CharField(max_length=100, blank=True, default='')
    bgColor = models.CharField(max_length=100, blank=True, default='')
    bgURL = models.CharField(max_length=100, blank=True, default='')
    wordColor = models.CharField(max_length=100, blank=True, default='')
    cardColor = models.CharField(max_length=100, blank=True, default='')
    cardURL = models.CharField(max_length=100, blank=True, default='')
    
    idCard = models.JSONField(blank=True, default=dict)
    snsTree_Data = models.JSONField(blank=True, default=dict)
    
class ContactGroup(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    group_Name = models.CharField(max_length=50, blank=False, default='Business')
    
    unread_profile = models.IntegerField(default=0)
    
class ContactData(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user', on_delete=models.CASCADE)
    
    member = models.ForeignKey(CustomUser, related_name='member', on_delete=models.CASCADE)
    block_setting = models.CharField(max_length=50, blank=True, default="None")
    group_Name =  models.CharField(max_length=50, default="Business")
    memo = models.TextField(blank=True)
    
    is_chat_available = models.CharField(max_length=10, default="False")
    is_pending = models.CharField(max_length=10, default="False")
    is_incoming = models.CharField(max_length=10, default="False")
    
    is_profile_update = models.CharField(max_length=10, default="False")
