from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from .views import (RegisterUserView, ValidateUserView, 
                    user_login, user_logout, change_password, 
                    ForgotPasswordView, ValidateVcodeView, ResetPasswordView)

urlpatterns = [
    path('register/vcode', RegisterUserView.as_view(), name='register'),
    path('register/validate', ValidateUserView.as_view(), name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('change_password', change_password, name='change_password'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('validate_code', ValidateVcodeView.as_view(), name='validate_code'),
    path('password_reset', ResetPasswordView.as_view(), name='password_reset'),
]