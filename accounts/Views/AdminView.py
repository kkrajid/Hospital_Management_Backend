from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User,DoctorModel
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from ..serializer import UserSerializer,DoctorSerializer



@api_view(['POST'])
def admin_login_view(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        print(password,email)
        user = User.objects.filter(
            email=email,
            is_superuser=True,
            role = 'Admin'
        ).first()

        if user is None:
            return Response({"message": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.check_password(password):
            return Response({"message": "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
            'role':"admin"
        }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        response = Response({'token': token}, status=status.HTTP_200_OK)
        return response




@api_view(['POST'])
def add_doctor(request):
    if 'user' not in request.META:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Admin').first()

    if user is not None:
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user_instance = user_serializer.save()
            doctor_serializer = DoctorSerializer(data=request.data)

            if doctor_serializer.is_valid():
                doctor_instance = doctor_serializer.save(user=user_instance)
                return Response({"message": "Doctor added successfully"}, status=status.HTTP_201_CREATED)
            else:
                user_instance.delete()
                return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
def all_doctors(request):
    if 'user' not in request.META:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id).first()

    if user is not None:
        doctors = User.objects.filter(role='Doctor')
        user_serializer = UserSerializer(doctors, many=True)
        
        doctor_models = DoctorModel.objects.filter(user__in=doctors)
        doctor_serializer = DoctorSerializer(doctor_models, many=True)

        combined_data = []
        for user_data, doctor_data in zip(user_serializer.data, doctor_serializer.data):
            combined_data.append({**user_data, **doctor_data})
        
        return Response({"doctors": combined_data}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "User not found 2"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def all_patients(request):
    if 'user' not in request.META:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id).first()

    if user is not None:
        patients = User.objects.filter(role='Patient')
        user_serializer = UserSerializer(patients, many=True)
        
        return Response({"patients": user_serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "User not found 2"}, status=status.HTTP_404_NOT_FOUND)






