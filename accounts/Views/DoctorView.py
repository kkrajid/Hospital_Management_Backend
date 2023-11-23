from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from ..serializer import *
from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404

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
        if user.is_blocked:
            return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)


        if not user.check_password(password):
            return Response({"message": "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow(),
            'role': 'doctor'
        }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        response = Response({'token': token}, status=status.HTTP_200_OK)
        return response





# @api_view(['GET'])
# def doctor_profile_view(request):
#     user_id = request.META.get('user')
    
#     if not user_id:
#         return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    

#     try:
#         doctor = User.objects.get(id=user_id, role='Doctor')
#     except User.DoesNotExist:
#         return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     if doctor.is_blocked:
#         return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)



#     try:
#         doctor_profile = doctor.doctorprofile
#         doctor_profile_serializer = DoctorProfileSerializer(doctor_profile)
#         return Response(doctor_profile_serializer.data, status=status.HTTP_200_OK)
#     except DoctorProfile.DoesNotExist:
#         return Response({"message": "Doctor profile not found"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# def add_doctor_profile(request):
#     user_id = request.META.get('user')
    
#     if not user_id:
#         return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         doctor = User.objects.get(id=user_id, role='Doctor')
#     except User.DoesNotExist:
#         return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     if doctor.is_blocked:
#         return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

#     # Check if the doctor already has a DoctorProfile
#     if hasattr(doctor, 'doctorprofile'):
#         return Response({"message": "Doctor profile already exists"}, status=status.HTTP_400_BAD_REQUEST)

#     # Assuming you pass the DoctorProfile data in the request data
#     doctor_profile_data = request.data
#     doctor_profile_data['user'] = doctor.id

#     # Create a DoctorProfile associated with the doctor
#     doctor_profile_serializer = DoctorProfileSerializer(data=doctor_profile_data)
#     if doctor_profile_serializer.is_valid():
#         doctor_profile_serializer.save()
#         return Response(doctor_profile_serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(doctor_profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# def update_doctor_profile(request, user_id):
#     user_id = request.META.get('user')
    
#     if not user_id:
#         return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         doctor = User.objects.get(id=user_id, role='Doctor')
#     except User.DoesNotExist:
#         return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
#     if doctor.is_blocked:
#         return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

#     # Check if the doctor has a DoctorProfile
#     if not hasattr(doctor, 'doctorprofile'):
#         return Response({"message": "Doctor profile not found"}, status=status.HTTP_404_NOT_FOUND)

#     # Retrieve the existing DoctorProfile
#     doctor_profile = doctor.doctorprofile

#     # Assuming you pass the updated DoctorProfile data in the request data
#     doctor_profile_data = request.data

#     # Make sure to set the 'user' field to the doctor's user ID
#     doctor_profile_data['user'] = doctor.id

#     # Use the existing DoctorProfile instance and update its fields
#     doctor_profile_serializer = DoctorProfileSerializer(doctor_profile, data=doctor_profile_data)

#     if doctor_profile_serializer.is_valid():
#         doctor_profile_serializer.save()
#         return Response(doctor_profile_serializer.data, status=status.HTTP_200_OK)
#     else:
#         return Response(doctor_profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_doctor_profiles(request):
    doctor_profiles = DoctorProfile.objects.all()
    serializer = DoctorProfileSerializer(doctor_profiles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def doctor_dashboard(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META.get('user')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        doctor_profile = DoctorProfile.objects.get(user=user)
    except DoctorProfile.DoesNotExist:
        return Response({"message": "Doctor profile not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorProfileSerializer(doctor_profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def doctor_profile_detail(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_404_NOT_FOUND)
    user_id = request.META.get('user')
    user = User.objects.filter(id=user_id).first()
 
    try:
        doctor_profile = DoctorProfile.objects.get(user=user)
    except DoctorProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DoctorProfileSerializer(doctor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data_s = request.data
        s = data_s['user'].pop('email')
        print(s)
        serializer = DoctorProfileSerializer(doctor_profile, data=data_s,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        doctor_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
# def get_patient_profiles(request):
#     patient_profiles = PatientProfile.objects.all()
#     serializer = PatientProfileSerializer(patient_profiles, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def create_patient_profile(request):
#     serializer = PatientProfileSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def patient_profile_detail(request, pk):
#     try:
#         patient_profile = PatientProfile.objects.get(pk=pk)
#     except PatientProfile.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = PatientProfileSerializer(patient_profile)
#         return Response(serializer.data)

#     if request.method == 'PUT':
#         serializer = PatientProfileSerializer(patient_profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'DELETE':
#         patient_profile.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
def create_time_slots(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META.get('user')
    
    doctor = User.objects.filter(id=user_id, role='Doctor').first()

    if doctor is not None:
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        print('------------------------------')
        print(start_time)
        print(end_time)
        print(date)
        print('------------------------------')
        step = timedelta(minutes=30)
        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

        current_time = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), start_time)
        end_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), end_time)

        time_slots = []

        while current_time < end_datetime:
            existing_slot = TimeSlot.objects.filter(doctor=doctor, date=date, start_time=current_time.time()).first()
            if existing_slot is not None:
                current_time += step
                continue

            time_slot_data = {
                'doctor': doctor.id,
                'date': date,
                'start_time': current_time.time(),
                'end_time': (current_time + step).time(),
                'available': True
            }
            time_slot_serializer = TimeSlotSerializer(data=time_slot_data)

            if time_slot_serializer.is_valid():
                time_slot_serializer.save()
                time_slots.append(time_slot_serializer.data)
            else:
                return Response(time_slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            current_time += step

        return Response(time_slots, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "n"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def all_time_slots(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META['user']
    doctor = User.objects.filter(id=user_id, role='Doctor').first()
    
    if doctor is None:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if doctor.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    # date = request.query_params.get('date')  # Use query_params to get 'date' parameter from the request
    date = request.query_params.get('date')
    print(date,'----------------------------------------')
    


    if date is None:
        return Response({"message": "Date parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

    slots = TimeSlot.objects.filter(doctor=doctor, date=date)
    time_slot_serializer = TimeSlotSerializer(slots, many=True)  # Use 'many=True' if you expect multiple time slots

    return Response(time_slot_serializer.data)


@api_view(['POST'])
def doctor_delete_time_slots(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.META['user']
    doctor = User.objects.filter(id=user_id, role='Doctor').first()
    if doctor.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    if doctor is not None:
        time_slots = request.data.get('time_slot')
        for time_slot_id in time_slots:
            slot = TimeSlot.objects.filter(id=time_slot_id).first()

            if slot is not None:
                slot.delete()
            else:
                return Response({"message": "Time slot not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Deleted successfully"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Bad Request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def all_appointment(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Doctor').first()

    if user is None:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    appointments = Appointment.objects.filter(doctor=user.id)
    appointment_serializer = AppointmentSerializer(appointments, many=True)  
    return Response(appointment_serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def confirm_appointment(request, appointment_id):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Doctor').first()

    if user is None:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)

    try:
        appointment = Appointment.objects.get(id=appointment_id, doctor=user.id, is_confirmed=False)
    except Appointment.DoesNotExist:
        return Response({"message": "Appointment not found or already confirmed"}, status=status.HTTP_404_NOT_FOUND)

    appointment.is_confirmed = True
    appointment.save()

    appointment_serializer = AppointmentSerializer(appointment)
    return Response(appointment_serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_all_appointment_of_doctor(request):
    user_id = request.META.get('user')
    data = request.GET.get('data')

    if not user_id:
        return Response({'message': "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id, role='Doctor')  
    except User.DoesNotExist:
        return Response({"message": "Doctor does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if user.is_blocked:
        return Response({"message": "User is blocked"}, status=status.HTTP_403_FORBIDDEN)
    try:
        all_appointments_ = Appointment.objects.filter(doctor=user).order_by('-appointment_datetime')
    except Appointment.DoesNotExist:
        return Response({'message': "Currently no appointment"}, status=status.HTTP_200_OK)
    data_dict = None
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        return Response({'message': "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

    appointment_id = data_dict.get('appointment_id')
    status_val = data_dict.get('status_val')

    if appointment_id and status_val:
        appointment = Appointment.objects.filter(id=appointment_id, doctor=user).first()
        if appointment:
            appointment.appointment_status = status_val
            appointment.save()
        else:
            return Response({'message': "Appointment not found or does not belong to this doctor"}, status=status.HTTP_404_NOT_FOUND)
    appointment_serializer = Get_for_doctor_AppointmentSerializer(all_appointments_, many=True)
    return Response(appointment_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_icu_patients(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Doctor').first()

    if user is None:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)
    doctor_info = User.objects.filter(id=user.id).first()
    all_appointments_ = Appointment.objects.filter(doctor=doctor_info,icu_selected=True)
    appointment_serializer = Get_for_doctor_AppointmentSerializer(all_appointments_, many=True)
    return Response(appointment_serializer.data)


@api_view(['POST'])
def add_icu_patient(request):
    if 'user' not in request.META:
        return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.META['user']
    user = User.objects.filter(id=user_id, role='Doctor').first()

    if user is None:
        return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.is_blocked:
        return Response({"message": "Your Account is Blocked"}, status=status.HTTP_403_FORBIDDEN)
    admintDate = request.data.get('admintDate')
    appointmentId = request.data.get('appointmentId')
    print(admintDate,appointmentId,"11111111111111111111111111111111111111111111111111111")
    appointment_ = Appointment.objects.filter(id=appointmentId).first()
    appointment_.icu_selected = True
    appointment_.save()
    serializer = Get_for_doctor_AppointmentSerializer(appointment_)
    return Response(serializer.data)



@api_view(['POST'])
def create_prescription(request):
    if request.method == 'POST':
        serializer = PrescriptionSerializer(data=request.data)
        print("fddddddddd",request.data)
        if serializer.is_valid():
            appointment_instance = serializer.validated_data.get('appointment')
            appointment_id = appointment_instance.id if appointment_instance else None
            
            if appointment_id is None:
                return Response({'error': 'Invalid appointment.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(appointment_id=appointment_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_prescriptions(request, appointment_id):
    if request.method == 'GET':
        try:
            # Assuming 'appointment_id' is an integer, adjust accordingly if it's a different type
            prescriptions = Prescription.objects.filter(appointment_id=appointment_id)
            serializer = PrescriptionSerializer(prescriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Prescription.DoesNotExist:
            return Response({'error': 'Prescriptions not found for the given appointment ID.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def doctor_get_appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    serializer = doctor_side_get_pateint_detialis_AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['PATCH'])
def doctor_manage_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    print(request.data,"*********************************")
    serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        print(serializer.data,"-----------------------------------")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)