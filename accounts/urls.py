
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
    ############################################################################

    #---------------------------ICU side----------------------------------------#
    path('icu/login',IcuView.icu_login_view,name='icu_login'),
    ############################################################################

    #---------------------------Doctor side--------------------------------------#
    path('doctor/login',DoctorView.doctor_login_view,name='doctor_login'),
    ############################################################################


]
