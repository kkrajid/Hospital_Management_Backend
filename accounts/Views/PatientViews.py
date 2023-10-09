from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from ..serializer import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
import random
import string
from django.core.mail import send_mail
from django.core.cache import cache
#----------------------------------###registration###-------------------------------------------------#
#-----------------------------------------------------------------------------------------------------#
def generate_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_email(recipient_email, otp):
    subject = 'Hospital Website Verification Code'
    message = f'Dear User,\n\nThank you for choosing our hospital website.\n\nYour OTP verification code is: {otp}\n\nThis code is essential for account security and to verify your identity. Please enter it on our website to complete the verification process.\n\nIf you did not request this code, please ignore this email.\n\nSincerely,\nThe Hospital Team'
    from_email = 'greenstorefun@gmail.com'
    try:
        send_mail(subject, message, from_email, [recipient_email])
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_otp_in_cache(user, otp):
    cache_key = f"otp_{user.id}"
    cache.set(cache_key, otp, 300)

def retrieve_otp_from_cache(user):
    o_key = f"otp_{user.id}"
    return cache.get(o_key)

@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            otp = generate_otp()
            user = serializer.save()
            recipient_email = user.email

            if send_otp_email(recipient_email, otp):
                print(f"OTP sent to {recipient_email}")
                store_otp_in_cache(user, otp)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Failed to send OTP via email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




#-------------------------------------------------------------------------------------------------------#
#----------------------------------### OTP VERIFICATION ###---------------------------------------------#
@api_view(['POST'])
def verify_otp_view(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        cache_key = f"otp_{user_id}"
        stored_otp = cache.get(cache_key)

        if user.otp_verified:
            return Response({'message': 'already otp verified'}, status=status.HTTP_400_BAD_REQUEST)
        if stored_otp is None:
            return Response({'message': 'OTP has expired or does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp != stored_otp:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        user.otp_verified = True
        user.is_active = True
        user.save()
    
        cache.delete(cache_key)
        
        return Response({'message': 'OTP verification successful.'}, status=status.HTTP_200_OK)

    return Response({'message': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(
            email=email,
            is_superuser=False,
            otp_verified=True,
            role = 'Patient'
        ).first()

        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_blocked:
            return Response({"message": "User is blocked"}, status=status.HTTP_403_FORBIDDEN)

        if not user.otp_verified:
            serializer = UserSerializer(user)
            return Response({"message": "OTP not verified", "data": serializer.data}, status=status.HTTP_200_OK)

        if not user.check_password(password):
            return Response({"message": "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
            'role':"patient"
        }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        response = Response()

        response.data = {
            'token': token
        }
        return response



@api_view(['GET'])
def user_view(request):
    if 'user' not in request.META:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Patient').first()

    if user is not None:
        serializer = UserSerializer(user)
        return Response({"message": serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)



# @api_view(['GET'])
# def user_view(request):
#     token = request.COOKIES.get('jwt')

#     if not token:
#         return redirect(reverse('login_view'))

#     try:
#         payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#     except jwt.ExpiredSignatureError:
#         return redirect(reverse('login_view'))

#     user = User.objects.get(id=payload['id'])
#     serializer = UserSerializer(user)
#     return Response(serializer.data)

# @api_view(['POST'])
# def logout_view(request):
#     if request.method == 'POST':
#         response = Response()
#         response.delete_cookie("jwt")
#         response.data = {
#             'message': "success"
#         }
#         return response
