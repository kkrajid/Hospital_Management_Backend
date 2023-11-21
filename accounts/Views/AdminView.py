from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from datetime import datetime, timedelta
from ..serializer import *
# from datetime import datetime, timedelta



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
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow(),
            'role':"admin"
        }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        response = Response({'token': token}, status=status.HTTP_200_OK)
        return response





@api_view(['GET'])
def get_all_doctor_profiles(request):
    if 'user' not in request.META:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    user_id = request.META.get('user')
    doctor = User.objects.filter(id=user_id, role='Admin').first()

    if doctor is not None:
        doctor_profiles = DoctorProfile.objects.all()
        serializer = DoctorProfileSerializer(doctor_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def create_doctor_profile(request):
    serializer = DoctorProfileSerializer(data=request.data)
   
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET', 'PUT', 'DELETE'])
def doctor_profile_detail(request, pk):
    try:
        doctor_profile = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DoctorProfileSerializer(doctor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = DoctorProfileSerializer(doctor_profile, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        doctor_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET'])
# def all_doctors(request):
#     if 'user' not in request.META:
#         return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#     user_id = request.META['user']
#     user = User.objects.filter(id=user_id).first()

#     if user is not None:
#         doctors = User.objects.filter(role='Doctor')
#         user_serializer = UserSerializer(doctors, many=True)
        
#         doctor_models = DoctorModel.objects.filter(user__in=doctors)
#         doctor_serializer = DoctorSerializer(doctor_models, many=True)

#         combined_data = []
#         for user_data, doctor_data in zip(user_serializer.data, doctor_serializer.data):
#             combined_data.append({**user_data, **doctor_data})
        
#         return Response({"doctors": combined_data}, status=status.HTTP_200_OK)
#     else:
#         return Response({"message": "User not found 2"}, status=status.HTTP_404_NOT_FOUND)



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








