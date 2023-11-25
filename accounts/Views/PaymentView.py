# Remove unused imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import stripe
from django.http import JsonResponse
from ..models import *
from django.conf import settings
from ..serializer import patient_side_get_pateint_detialis_AppointmentSerializer
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        appointment_id = data.get('appointmentId')
        print(appointment_id,"dsdsfsdf")
        if appointment_id:
            appointment = Appointment.objects.filter(id=int(appointment_id)).first()
            doctor = User.objects.filter(id=appointment.doctor.id).first()
            doctor = DoctorProfile.objects.filter(id=doctor.id).first()
            print(doctor.service_charge)
            payment_amount = int(doctor.service_charge)
            appointment_serializer = patient_side_get_pateint_detialis_AppointmentSerializer(appointment)
            
        try:
            intent = stripe.PaymentIntent.create(
                amount=payment_amount,
                currency='INR',
                payment_method_types=['card'],
            )

            return JsonResponse({'clientSecret': intent.client_secret, 'amount': payment_amount,'appointment_data':appointment_serializer.data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ConfirmPaymentView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        stripe_payment_intent_id = data.get('stripePaymentIntentId')
        appointment_id = data.get('appointmentId')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.payment_status = "Paid"
            appointment.appointment_status = "Accepted"
            appointment.save()

            # Payment.objects.create(
            #     stripe_id=stripe_payment_intent_id,
            #     appointment=appointment
            # )

            return JsonResponse({'success': True, 'message': 'Payment successful'})

        except Appointment.DoesNotExist:
            return JsonResponse({'error': True, 'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({'error': True, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
