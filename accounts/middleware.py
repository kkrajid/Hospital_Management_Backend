from typing import Any

import jwt

from .models import User

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = None
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user_details = User.objects.get(id=payload['id'])
            user = user_details.id
        except jwt.exceptions.DecodeError:
            user = None
        
        request.META['user'] = user
        print(user)
        response = self.get_response(request)
        return response


# from typing import Any
# import jwt
# from .models import User
# from django.http import JsonResponse
# from rest_framework import status

# class CustomMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         user = None
#         token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#             user_details = User.objects.get(id=payload['id'])
#             user = user_details

#             # Check if the user is OTP verified
#             if not user.otp_verified and request.path != '/verify-otp/':
#                 return JsonResponse({"message": "OTP not verified. Please verify your OTP."}, status=status.HTTP_401_UNAUTHORIZED)
#         except jwt.exceptions.DecodeError:
#             user = None

#         request.user = user  # Set the user object in the request
#         response = self.get_response(request)
#         return response
