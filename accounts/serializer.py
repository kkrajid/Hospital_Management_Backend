from .models import *
from rest_framework import serializers
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'phone','date_of_birth',"gender"]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'Patient'},
        }

    # def validate_phone(self, phone):
    #     phone_pattern = re.compile(r'^\+\d{1,3}\d{3,14}$')
    #     if not phone_pattern.match(phone):
    #         raise serializers.ValidationError("Invalid phone number format. Please use a valid format.")
    #     return phone
    
    # def validate_password(self, password):
    #     password_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+{}\[\]:;<>,.?~\\-]{8,}$')
    #     if not password_pattern.match(password):
    #         raise serializers.ValidationError("Invalid password format. Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit.")
    #     return password

    def create(self, validated_data):
        if 'email' not in validated_data:
            raise serializers.ValidationError("Email is required.")
        if 'password' not in validated_data:
            raise serializers.ValidationError("Password is required.")

        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance





class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    address = AddressSerializer(required=False)
    is_blocked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = '__all__'

    def get_is_blocked(self, obj):
        user_instance = obj.user
        if user_instance:
            return user_instance.is_blocked
        return None 

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        address_data = validated_data.pop('address')

        user, created = User.objects.get_or_create(email=user_data['email'], defaults=user_data)
        if 'password' in user_data:
            user.set_password(user_data['password'])
            user.save()

        address, created = Address.objects.get_or_create(**address_data)

        doctor_profile, created = DoctorProfile.objects.get_or_create(user=user, address=address, defaults=validated_data)
        return doctor_profile
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})  
        address_data = validated_data.pop('address')

        
        for attr, value in address_data.items():
            setattr(instance.address, attr, value)
        instance.address.save()

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

       
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr != 'email':  
                    setattr(user, attr, value)
            user.save()

        return instance

class PatientProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = PatientProfile
        fields = '__all__'
    def create(self, validated_data):
        # print(validated_data)
        address_data = validated_data.pop('address')  # Extract address data
        address, _ = Address.objects.get_or_create(**address_data)  # Get or create the Address
        patient_profile = PatientProfile.objects.create(address=address, **validated_data)
        return patient_profile
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address, _ = Address.objects.get_or_create(**address_data)
            instance.address = address

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class GetAppointmentSerializer(serializers.ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    doctor_profile = DoctorProfileSerializer(source='doctor.doctorprofile', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class Get_for_doctor_AppointmentSerializer(serializers.ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    Patient_profile = PatientProfileSerializer(source='patient.patientprofile', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'




class patient_side_get_pateint_detialis_AppointmentSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    doctor_profile = DoctorProfileSerializer(source='doctor.doctorprofile', read_only=True)
    patient = UserSerializer()
    time_slot = TimeSlotSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = ['id', 'time_slot', 'patient', 'doctor_profile', 'appointment_datetime',
                  'is_confirmed', 'is_cancelled', 'appointment_status', 'prescriptions']
        

class doctor_side_get_pateint_detialis_AppointmentSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    Patient_profile = PatientProfileSerializer(source='patient.patientprofile', read_only=True)
    doctor_profile = DoctorProfileSerializer(source='doctor.doctorprofile', read_only=True)
    patient = UserSerializer()
    time_slot = TimeSlotSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = ['id', 'time_slot', 'patient', 'Patient_profile', 'appointment_datetime','doctor_profile',
                  'is_confirmed', 'is_cancelled','icu_status','icu_admitted_date','icu_selected', 'appointment_status', 'prescriptions']
        

class AdminSidePatientProfileSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer(source='patientprofile', read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class DoctorAppointmentCountSerializer(serializers.Serializer):
    doctor_name = serializers.CharField(source='doctor.full_name')
    appointment_count = serializers.IntegerField()

    class Meta:
        fields = ['doctor_name', 'appointment_count']


class AdminDashboardSerializer(serializers.Serializer):
    total_patient_count = serializers.SerializerMethodField()
    icu_admitted_count = serializers.SerializerMethodField()
    appointment_completed_count = serializers.SerializerMethodField()
    total_paid_count = serializers.SerializerMethodField()
    total_revenue_count = serializers.SerializerMethodField()

    def get_total_patient_count(self, obj):
        return User.objects.filter(role='Patient').count()

    def get_icu_admitted_count(self, obj):
        return Appointment.objects.filter(icu_status=ICU_STATUS[0][0]).count()

    def get_appointment_completed_count(self, obj):
        return Appointment.objects.filter(appointment_status='Completed').count()

    def get_total_paid_count(self, obj):
        return Appointment.objects.filter(payment_status=PAYMENT_STATUS[1][0]).count()


    def get_total_revenue_count(self, obj):
        total_revenue = Prescription.objects.filter(appointment__payment_status=PAYMENT_STATUS[1][0]).aggregate(
            total_revenue=models.Sum(models.F('quantity') * models.F('appointment__doctor__doctorprofile__service_charge'), output_field=models.PositiveIntegerField())
        )['total_revenue']
        return total_revenue