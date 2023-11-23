from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,AbstractUser

from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
    ('Doctor', 'Doctor'),
    ('Patient', 'Patient'),
    ('Admin', 'Admin'),
)   

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('otp_verified', True)
        extra_fields.setdefault('role', "Admin")

        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=220)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=100)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
    
class Address(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.zip_code}, {self.country}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.TextField()

    class Meta:
        abstract = True


class DoctorProfile(UserProfile):
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    service_charge = models.CharField(max_length=100)

class PatientProfile(UserProfile):
    insurance_info = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)


class TimeSlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor.full_name} - {self.date} - {self.start_time} to {self.end_time}"

@receiver(post_save, sender=TimeSlot)
def post_save_timeslot(sender, instance, created, **kwargs):
    if created:
        action = "created"
    else:
        action = "updated"
    print(f"TimeSlot {instance.id} {action}")


APPOINTMENT_STATUS = (
    ('Pending', 'Pending'),
    ('Cancelled', 'Cancelled'),
    ('Accepted', 'Accepted'),
    ('Completed', 'Completed'),
)

ICU_STATUS = (
    ('ICU Admitted', 'ICU Admitted'),
    ('ICU Critical', 'ICU Critical'),
    ('ICU Recovered', 'ICU Recovered'),
    ('ICU Not Needed', 'ICU Not Needed'),
    ('ICU Discharged', 'ICU Discharged'), 
)


class Appointment(models.Model):
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    appointment_datetime = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    appointment_status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='Pending')
    icu_selected = models.BooleanField(default=False)
    icu_status = models.CharField(max_length=20, choices=ICU_STATUS, default='ICU Not Needed')
    icu_admitted_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    icu_discharged_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"Appointment with {self.doctor} on {self.appointment_datetime}"


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medications = models.TextField()
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    instructions = models.TextField()
    issued_date = models.DateField(auto_now_add=True)
  

    def __str__(self):
        return f"Prescription for {self.appointment.patient} by {self.appointment.doctor} on {self.issued_date}"


class Instruction(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    instruction_text = models.TextField()

    def __str__(self):
        return f"Instruction for Prescription {self.prescription.id}"


# class Address(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     street_address = models.CharField(max_length=100)
#     city = models.CharField(max_length=50)
#     state = models.CharField(max_length=50)
#     postal_code = models.CharField(max_length=10)

#     def __str__(self):
#         return f"{self.street_address}, {self.city}, {self.state} {self.postal_code}"
    

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content}"