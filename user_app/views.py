from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, ChangePasswordSerializer, ResetPasswordSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser
from django.contrib.auth import update_session_auth_hash
from rest_framework.views import APIView
from .utils import generate_vcode, send_vcode_email
from django.core.signing import TimestampSigner, BadSignature
from django.shortcuts import redirect
from datetime import datetime


# Register with Email vcode
class RegisterUserView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'This user is not created exactly.'}, status=status.HTTP_400_BAD_REQUEST)

        vcode = generate_vcode()
        user.vcode = vcode
        user.save()

        send_vcode_email(email, vcode)

        return Response({'message': 'Verification code has been sent to your email.'}, status=status.HTTP_200_OK)

class ValidateUserView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        vcode = request.data.get('vcode', '')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.vcode == vcode and not user.email_verified:
            user.vcode = None
            user.email_verified = True
            user.save()
            
            # Authenticate the user and create or get an authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid vcode.'}, status=status.HTTP_400_BAD_REQUEST)

# LOGIN
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except:
                pass

        if not user:
            user = authenticate(username=username, password=password)
        
        if user:
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'username': user.username,'email': user.email, 'avatar': user.avatar}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# LOGOUT
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Change Password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Pssword Reset with Email vcode
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = CustomUser.objects.get(email=email)
        except:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        vcode = generate_vcode()
        user.vcode = vcode
        user.save()

        send_vcode_email(email, vcode)

        return Response({'message': 'Verification code has been sent to your email.'}, status=status.HTTP_200_OK)

class ValidateVcodeView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        vcode = request.data.get('vcode', '')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.vcode == vcode:
            user.vcode = None
            user.save()
            
            # Authenticate the user and create or get an authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid vcode.'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = request.user
            except CustomUser.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)  # To update session after password change
            return Response({'message': 'Password is reset succesfully.'}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
