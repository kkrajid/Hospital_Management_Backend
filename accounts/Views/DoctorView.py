from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime


@api_view(['POST'])
def doctor_login_view(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(
            email=email,
            is_superuser=False,
            role='Doctor',
        ).first()

        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"message": "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
            'role': 'doctor'
        }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
       
        response = Response({
            'token': token
        }, status=status.HTTP_200_OK)

        return response

