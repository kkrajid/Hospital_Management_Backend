
from django.urls import path,include
from .Views import AdminView,DoctorView, IcuView, PatientViews
urlpatterns = [
    #-----------------------Patient side----------------------------------------#
    path('register',PatientViews.register_view,name='register_view' ),
    path('verification',PatientViews.verify_otp_view,name='verification' ),
    path('login',PatientViews.login_view,name='login_view'),
    path('user',PatientViews.user_view,name='user_view' ),
    ############################################################################

    #-------------------------Admin side----------------------------------------#
    path('admin/login',AdminView.admin_login_view,name='admin_login'),
    path('admin/add_doctor',AdminView.add_doctor,name='add_doctor'),
    path('admin/all_doctors',AdminView.all_doctors,name='all_doctors'),
    path('admin/all_patients',AdminView.all_patients,name='all_patients'),
    ############################################################################

    #---------------------------ICU side----------------------------------------#
    path('icu/login',IcuView.icu_login_view,name='icu_login'),
    ############################################################################

    #---------------------------Doctor side--------------------------------------#
    path('doctor/login',DoctorView.doctor_login_view,name='doctor_login'),
    ############################################################################


]
