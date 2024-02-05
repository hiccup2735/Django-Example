import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_vcode(length=6):
    characters = string.digits
    vcode = ''.join(random.choice(characters) for _ in range(length))
    return vcode

def send_vcode_email(email, vcode):
    subject = 'Email Verification'
    message = f'Verify Code is: {vcode}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
