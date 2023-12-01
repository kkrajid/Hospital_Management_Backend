
from django.urls import path,include
from .Views import AdminView,DoctorView, IcuView, PatientViews,PaymentView,ChatView
urlpatterns = [
    #-----------------------Patient side----------------------------------------#
    path('register',PatientViews.register_view,name='register_view' ),
    path('verification',PatientViews.verify_otp_view,name='verification' ),
    path('login',PatientViews.login_view,name='login_view'),
    path('user',PatientViews.user_view,name='user_view' ),
    path('patient/profile',PatientViews.patient_profile_view,name='patient_profile_view' ),
    path('patient/dashboard',PatientViews.patient_dashboard_view,name='patient_dashboard_view' ),
    path('patient/doctor_list',PatientViews.doctor_list,name='patient_doctor_list' ),
    path('patient/add_or_updateprofile',PatientViews.update_or_add_patient_profile,name='update_or_add_patient_profile' ),
    path('patient/doctor_select/<int:pk>',PatientViews.doctor_select,name='doctor_select' ),
    path('patient/doctor/time-slots/<int:pk>/<str:date>/', PatientViews.doctor_time_slot_in_patientside, name='doctor_time_slot_in_patientside'),
    path('patient/make_appointments',PatientViews.make_appointments,name='make_appointments' ),
    path('patient/get_all_appointment',PatientViews.get_all_appointment,name='get_all_appointment' ),
    path('patient/appointments/<int:appointment_id>/', PatientViews.appointment_details, name='appointment-details'),
    path('patient/prescriptions/appointment/<int:appointment_id>/', PatientViews.prescriptions_for_appointment, name='prescriptions-for-appointment'),
    path('patient/cancel_appointment/<int:appointment_id>/', PatientViews.cancel_appointment, name='cancel_appointment'),
   
    ############################################################################

    #-------------------------Admin side----------------------------------------#
    path('admin/login',AdminView.admin_login_view,name='admin_login'),
    path('admin/all_doctors/<int:pk>/',AdminView.doctor_profile_detail,name='admin_doctor_profile_detail'),
    path('admin/all_doctors',AdminView.get_all_doctor_profiles,name='get_all_doctor_profiles'),
    path('admin/all_patients',AdminView.all_patients,name='all_patients'),
    path('admin/doctor/create', AdminView.create_doctor_profile, name='create-doctor-profile'),
    path('admin/block-users/', AdminView.block_users, name='block_users'),
    path('admin/unblock-users/', AdminView.unblock_users, name='unblock_users'),
    path('admin/admin_dashboard_data/', AdminView.admin_dashboard_data, name='admin_dashboard_data'),
    path('admin/updateBlockStatusOfDoctor/', AdminView.update_block_status_of_doctor, name='update_block_status_of_doctor'),
    ############################################################################

    #---------------------------ICU side----------------------------------------#
    path('icu/login',IcuView.icu_login_view,name='icu_login'),
    ############################################################################

    #---------------------------Doctor side--------------------------------------#
    path('doctor/login',DoctorView.doctor_login_view,name='doctor_login'),
    path('doctor/create_time_slots',DoctorView.create_time_slots,name='create_time_slots'),
    path('doctor/all_time_slots',DoctorView.all_time_slots,name='all_time_slots'),
    path('doctor/doctor_delete_time_slots',DoctorView.doctor_delete_time_slots,name='doctor_delete_time_slots'),

    path('doctor-profiles/', DoctorView.get_doctor_profiles, name='doctor-profile-list'),
    path('doctor_profile_detail', DoctorView.doctor_profile_detail, name='doctor_profile_detail'),
    path('doctor/get_all_appointment_of_doctor', DoctorView.get_all_appointment_of_doctor, name='get_all_appointment_of_doctor'),
    path('doctor/dashboard',DoctorView.doctor_dashboard,name='doctor_dashboard'),
    path('doctor/create_prescription/', DoctorView.create_prescription, name='create_prescription'),
    path('doctor/get-prescriptions/<int:appointment_id>/', DoctorView.get_prescriptions, name='get-prescriptions'),
    path('doctor/appointments/<int:appointment_id>/', DoctorView.doctor_get_appointment_details, name='doctor_get_appointment_details'),
    path('doctor/all_icu_patients/', DoctorView.all_icu_patients, name='all_icu_patients'),
    path('doctor/add_icu_patient/', DoctorView.add_icu_patient, name='add_icu_patient'),
    path('doctor/appointments/<int:appointment_id>/update-status/', DoctorView.doctor_manage_appointment_status, name='update_appointment_status'),

    
    # path('create-payment-intent/', PaymentView.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('confirm-payment/', PaymentView.ConfirmPaymentView.as_view(), name='confirm_payment'),
    path('create-payment-intent/', PaymentView.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('messages/<str:room_slug>/', ChatView.fetch_messages, name='fetch_messages'),
    
    
    
    # path('doctor/profile',DoctorView.doctor_profile_view,name='doctor_profile_view'),
    # path('doctor/addprofile',DoctorView.add_doctor_profile,name='add_doctor_profile'),
    
    
    
    ############################################################################


]
