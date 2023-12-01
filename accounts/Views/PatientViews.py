from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..serializer import *
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
import random
import string
from django.core.mail import send_mail
from django.core.cache import cache
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
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
        # print(request.data)
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
            'role':"patient",
            'name':user.full_name
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

@api_view(['GET'])
def patient_dashboard_view(request):
    user_id = request.META.get('user')
    
    if not user_id:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    

    try:
        patient = User.objects.get(id=user_id, role='Patient')
    except User.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    if patient.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    patient_serializer = UserSerializer(patient)
    patient_profile = PatientProfile.objects.filter(user=patient).first()
    
    if patient_profile:
        profile_serializer = PatientProfileSerializer(patient_profile)
        return Response({'user':patient_serializer.data,'profile_data':profile_serializer.data}, status=status.HTTP_200_OK)
    return Response({'user':patient_serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def patient_profile_view(request):
    user_id = request.META.get('user')
    
    if not user_id:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    

    try:
        patient = User.objects.get(id=user_id, role='Patient')
    except User.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    if patient.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    patient_serializer = UserSerializer(patient)
    patient_profile = PatientProfile.objects.filter(user=patient).first()
    
    if patient_profile:
        profile_serializer = PatientProfileSerializer(patient_profile)
        return Response({'user':patient_serializer.data,'profile_data':profile_serializer.data}, status=status.HTTP_200_OK)
    return Response({'user':patient_serializer.data}, status=status.HTTP_200_OK)


    
    


# @api_view(['POST'])
# def add_patient_profile(request):
#     user_id = request.META.get('user')
    
#     if not user_id:
#         return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         patient = User.objects.get(id=user_id, role='Patient')
#     except User.DoesNotExist:
#         return Response({"message": "patient not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     if patient.is_blocked:
#         return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)
#     if hasattr(patient, 'patientprofile'):
#         return Response({"message": "patient profile already exists"}, status=status.HTTP_400_BAD_REQUEST)


#     patient_profile_data = request.data
#     patient_profile_data['user'] = patient.id

   
#     patient_profile_serializer = PatientProfileSerializer(data=patient_profile_data)
#     if patient_profile_serializer.is_valid():
#         patient_profile_serializer.save()
#         return Response(patient_profile_serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(patient_profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['PUT'])
def update_or_add_patient_profile(request):
    user_id = request.META.get('user')
    # print(user_id, '------------------------------------------------------------------------')
    
    if not user_id:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient = User.objects.filter(id=user_id, role='Patient').first()
    except User.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if patient.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    patient_serializer = UserSerializer(patient, data=request.data, partial=True)
    
    if patient_serializer.is_valid():
        patient_serializer.save()
    # print(request.data)


    if hasattr(patient,'patientprofile'):
        print('*******************************************')
        patient_profile = patient.patientprofile
        patient_profile_data = request.data
        patient_profile_data['user'] = patient.id
        patient_profile_serializer = PatientProfileSerializer(patient_profile, data=patient_profile_data,partial=True)
    else:
        patient_profile_data = request.data
        patient_profile_data['user'] = patient.id
        print('---------------------------------------')
        patient_profile_serializer = PatientProfileSerializer(data=patient_profile_data)

    if patient_profile_serializer.is_valid():
        patient_profile_serializer.save()

    return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def doctor_list(request):
#     paginator = PageNumberPagination()
#     paginator.page_size = 3
#     doctor_list = User.objects.filter(role='Doctor', is_blocked=False)
#     result_page = paginator.paginate_queryset(doctor_list, request)
#     doctor_data = []
#     for user in result_page:
#         doctor_profile_data = UserSerializer(user).data
#         if hasattr(user,'doctorprofile'):
#             doctor_profile_data['specialization'] = DoctorProfileSerializer(user.doctorprofile).data['specialization']
#         doctor_data.append(doctor_profile_data)
#     return paginator.get_paginated_response(doctor_data)


@api_view(['GET'])
def doctor_list(request):
    doctor_profiles = DoctorProfile.objects.all()
    serializer = DoctorProfileSerializer(doctor_profiles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def doctor_select(request, pk):
    try:
        doctor_profile = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DoctorProfileSerializer(doctor_profile)
        # print(serializer.data['user']['id'])
        return Response(serializer.data, status=status.HTTP_200_OK)
    



    
@api_view(['GET'])
def doctor_time_slot_in_patientside(request, pk, date):
    if date is None:
        return Response({"message": "Date parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

    doc = DoctorProfile.objects.filter(pk=pk).first()
    
    if not doc:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    profile = DoctorProfileSerializer(doc)


    id = profile.data['user']['id']
    print(id, '-------------------------------->')
    
    doctor = User.objects.filter(id=id).first()

    if not doctor:
        return Response({"message": "Doctor's user not found"}, status=status.HTTP_404_NOT_FOUND)

    slots = TimeSlot.objects.filter(doctor=doctor, date=date)
    time_slot_serializer = TimeSlotSerializer(slots, many=True) 
   

    return Response(time_slot_serializer.data)


@api_view(['POST'])
def make_appointments(request):
    user_id = request.META.get('user')
    if not user_id:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient = User.objects.get(id=user_id, role='Patient')
    except User.DoesNotExist:
        return Response({"message": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    if patient.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    doctor_id = request.data.get('doctor_id')
    time_slot_id = request.data.get('time_slot')  
    
    try:
        doctor = User.objects.get(id=doctor_id)
    except User.DoesNotExist:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        time_slot = TimeSlot.objects.get(id=time_slot_id)
    except TimeSlot.DoesNotExist:
        return Response({"message": "Time slot not found"}, status=status.HTTP_404_NOT_FOUND)

    if not time_slot.available:
        return Response({"message": "Time slot is not available"}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        "time_slot": time_slot.id,
        "patient": patient.id,
        "doctor": doctor.id,
    }
    make_appoint_serializer = AppointmentSerializer(data=data)
    
    if make_appoint_serializer.is_valid():
        make_appoint_serializer.save()
        time_slot.available = False
        time_slot.save()  # Save the updated time_slot
        
        return Response({"message": "Appointment successfully created","data":make_appoint_serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response(make_appoint_serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_all_appointment(request):
    user_id = request.META.get('user')
    if not user_id:
        return Response({'message': "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id, role='Patient')  
    except User.DoesNotExist:
        return Response({"message": "Patient does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if user.is_blocked:
        return Response({"message": "User is blocked"}, status=status.HTTP_403_FORBIDDEN)
    try:
        all_appointments_of_patient = Appointment.objects.filter(patient=user).order_by('-appointment_datetime')
    except Appointment.DoesNotExist:
        return Response({'message': "Currently no appointment"}, status=status.HTTP_200_OK)
    appointment_serializer = GetAppointmentSerializer(all_appointments_of_patient, many=True)
    return Response(appointment_serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    serializer = patient_side_get_pateint_detialis_AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['GET'])
def prescriptions_for_appointment(request, appointment_id):
    prescriptions = Prescription.objects.filter(appointment__id=appointment_id)
    serializer = PrescriptionCreateSerializer(prescriptions, many=True)
    return Response({'prescriptions': serializer.data})





@api_view(['POST'])
def cancel_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    if appointment.is_cancelled:
        return Response({'error': 'Appointment is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    appointment.is_cancelled = True
    appointment.appointment_status = 'Cancelled'
    appointment.save()
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def doctor_time_slot_in_patientside(request, pk, date):
#     if date is None:
#         return Response({"message": "Date parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
        
#         doc = DoctorProfile.objects.filter(pk=pk).first()
#         profile = DoctorProfileSerializer(doc)
#         id = profile.data['user']['id']
#         print(id,'-------------------------------->')
#         doctor = User.objects.filter(id=id).first()
#         slots = TimeSlot.objects.filter(doctor=doctor, date=date)
#         time_slot_serializer = TimeSlotSerializer(slots, many=True)  # Use 'many=True' if you expect multiple time slots
#         print(time_slot_serializer.data)
#         return Response(time_slot_serializer.data)
#     except Exception as e:
#         # Log the exception for debugging
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.error(str(e))
#         return Response({"message": "An error occurred on the server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # try:
    #     doctor = User.objects.filter(is_blocked=False, role='Doctor', id=pk).first()

    #     if not doctor:
    #         return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    #     doctor_serializer = UserSerializer(doctor)
    #     doctor_profile = DoctorProfile.objects.filter(user=doctor_serializer.data['id']).first()
        
    #     if doctor_profile:
    #         doctor_profile_serializer = DoctorProfileSerializer(doctor_profile)
    #         response_data = {
    #             'user_data': doctor_serializer.data,
    #             'profile_data': doctor_profile_serializer.data
    #         }
    #     else:
    #         response_data = {
    #             'user_data': doctor_serializer.data,
    #             'profile_data': None
    #         }
    #     return Response(response_data)
    # except Exception as e:
    #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def doctor_list(request):
#     paginator = PageNumberPagination()
#     paginator.page_size = 3

#     # Use select_related to perform an inner join between User and DoctorProfile
#     doctor_list = DoctorProfile.objects.all().select_related("user")
#     for doctor in doctor_list:
#         print(f"Doctor ID: {doctor.id}")
#         print(f"User Email: {doctor.user.email}")
#         print(f"Specialization: {doctor.specialization}")
#         print(f"License Number: {doctor.license_number}")
#         # Access other fields as needed
#         print("-------------------------------")

#     result_page = paginator.paginate_queryset(doctor_list, request)

#     # Serialize the data as needed
#     doctor_data = UserSerializer(result_page, many=True).data

#     return paginator.get_paginated_response(doctor_data)
