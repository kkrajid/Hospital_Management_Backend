from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from .serializer import GetAppointmentSerializer
from django.core.mail import send_mail
import json

def send_otp_email(patient_email, appointment_date, doctor_name, start_time, end_time, subject, message):
    try:
        if patient_email:
            send_mail(subject, message, 'greenstorefun@gmail.com', [patient_email])
            return True
        else:
            print("Email recipient is None.")
            return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@receiver(post_save, sender=Appointment)
def post_save_timeslot(sender, instance, created, **kwargs):
    if created:
        action = "created"
    else:
        action = "updated"

    if action == "updated":
        appointment = Appointment.objects.get(id=instance.id)
        appointment_serializer = GetAppointmentSerializer(appointment)
        appointment_status = appointment_serializer.data['appointment_status']
        
        if appointment_status == "Accepted":
            patient_email = appointment_serializer.data['patient']['email']
            appointment_date = appointment_serializer.data['time_slot']['date']
            doctor_name = appointment_serializer.data['doctor_profile']['user']['full_name']
            start_time = appointment_serializer.data['time_slot']['start_time']
            end_time = appointment_serializer.data['time_slot']['end_time']
            subject = 'Your Hospital Appointment Confirmation'
            message = f'Dear Patient,\n\nThank you for choosing our hospital for your appointment.\n\nYour appointment details are as follows:\n\nDate: {appointment_date}\nTime: {start_time}-{end_time}\nDoctor: {doctor_name}\n\nPlease arrive 15 minutes before your appointment time.\n\nIf you have any questions or need to reschedule, please contact us.\n\nSincerely,\nThe Hospital Team'
            send_otp_email(patient_email, appointment_date, doctor_name, start_time, end_time, subject, message)

        elif appointment_status == "Cancelled":
            patient_email = appointment_serializer.data['patient']['email']
            appointment_date = appointment_serializer.data['time_slot']['date']
            doctor_name = appointment_serializer.data['doctor_profile']['user']['full_name']
            start_time = appointment_serializer.data['time_slot']['start_time']
            end_time = appointment_serializer.data['time_slot']['end_time']
            subject = 'Appointment Cancellation'
            message = f'Dear Patient,\n\nWe regret to inform you that your appointment scheduled for {appointment_date} with Dr. {doctor_name} from {start_time} to {end_time} has been cancelled.\n\nIf you have any questions or need to reschedule, please contact us.\n\nSincerely,\nThe Hospital Team'
            send_otp_email(patient_email, appointment_date, doctor_name, start_time, end_time, subject, message)
            
    elif action == "created":
        appointment = Appointment.objects.get(id=instance.id)
        appointment_serializer = GetAppointmentSerializer(appointment)
        patient_email = appointment_serializer.data['patient']['email']
        appointment_date = appointment_serializer.data['time_slot']['date']
        doctor_name = appointment_serializer.data['doctor_profile']['user']['full_name']
        start_time = appointment_serializer.data['time_slot']['start_time']
        end_time = appointment_serializer.data['time_slot']['end_time']
        subject = 'Appointment Waitlist Confirmation'
        message = f'Dear Patient,\n\nThank you for choosing our hospital. Your appointment is currently on our waitlist.\n\nWe will notify you if an appointment becomes available. Please be ready to confirm the appointment when notified.\n\nIf you have any questions, please contact us.\n\nSincerely,\nThe Hospital Team'
        send_otp_email(patient_email, appointment_date, doctor_name, start_time, end_time, subject, message)




@receiver(post_save, sender=DoctorProfile)
def post_save_timeslot(sender, instance, created, **kwargs):
    if created:
        action = "created"
    else:
        action = "updated"
    print(action,'-------------------------------',instance.id)

   