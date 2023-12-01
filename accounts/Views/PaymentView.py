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
        print(appointment_id, "dsdsfsdf")
        if appointment_id:
            appointment = Appointment.objects.filter(id=int(appointment_id)).first()
            if appointment:
                doctor = User.objects.filter(id=appointment.doctor.id).first()
                doctor_profile = DoctorProfile.objects.filter(id=doctor.id).first()

                # Check if the doctor_profile and service_charge exist
                if doctor_profile and doctor_profile.service_charge:
                    payment_amount = 500
                else:
                    return JsonResponse({'error': 'Invalid doctor or service charge not found.'}, status=500)

                appointment_serializer = patient_side_get_pateint_detialis_AppointmentSerializer(appointment)

                try:
                    if payment_amount < 1:
                        return JsonResponse({'error': 'Payment amount must be greater than or equal to 1.'}, status=400)

                    intent = stripe.PaymentIntent.create(
                        amount=payment_amount,
                        currency='INR',
                        payment_method_types=['card'],
                    )

                    return JsonResponse({'clientSecret': intent.client_secret, 'amount': payment_amount, 'appointment_data': appointment_serializer.data})

                except Exception as e:
                    print(e)
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Appointment not found.'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid appointment ID.'}, status=400)



class ConfirmPaymentView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        stripe_payment_intent_id = data.get('stripePaymentIntentId')
        appointment_id = data.get('appointmentId')
        amount= data.get('amount')
        print(amount,"32323232323******************************************")

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.payment_status = "Paid"
            appointment.appointment_status = "Accepted"
            appointment.amount_paid=amount
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
