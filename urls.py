from django.urls import path


from patient.views import (
    PatientDashboardView,
    UpdatePatientProfileView,
    PatientWalletView,
    DoctorListView,
    DoctorDetailsView,
    FollowUnfollowUpDoctorView,
    FollowListView,
    RequestForCall,
    PatientNotificationListView,
    HelpView,
    LabResultView,
    PatientInviteFriendView,
    AddLabResultView,
    PatientCallView,
    HistoryView,
    GetDoctorsView,
    DisconnectCall,
    LabDetailsPage,
    SummaryDetail,
    GetPurchaseHistoryView,
    GetSpentHistoryView
)
from patient.anonymous_user import (
    AnonymousDoctorListView,
    AnonymousDoctorDetailsView
)


app_name= 'patient'


urlpatterns = [
    path('update-profile/', UpdatePatientProfileView.as_view(), name='update_patient_profile'),
    path('dashboard/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('wallet/', PatientWalletView.as_view(), name='patient_wallet'),
    path('get-purchase-history/', GetPurchaseHistoryView.as_view(), name='get_purchase_history'),
    path('get-spent-history/', GetSpentHistoryView.as_view(), name='get_spent_history'),


    
    path('doctor-listing/', DoctorListView.as_view(), name='doctor_listing'),
    path('doctor-details/<str:uuid>/', DoctorDetailsView.as_view(), name='doctor_details'),
    path('follow-unfollow/doctor/', FollowUnfollowUpDoctorView.as_view(), name='follow_unfollow_doctor'),
    path('follow-list/', FollowListView.as_view(), name='follow_list'),
    path('notification-list/', PatientNotificationListView.as_view(), name='notification_list'),
    path('invite-friend/', PatientInviteFriendView.as_view(), name="patient_invite_friend"),
    path('help/', HelpView.as_view(), name="help"),
    path('lab-results/', LabResultView.as_view(), name="lab_result"),
    path('add-result/', AddLabResultView.as_view(), name="add_result"),
    path('get-doctors/', GetDoctorsView.as_view(), name="get_doctors"),

    path('patient-call/', PatientCallView.as_view(), name="patient_call"),
    path('history/', HistoryView.as_view(), name="history"),
    path('lab-detail-page/<int:pk>/', LabDetailsPage.as_view(), name='lab_detail_page'),
    path('summary-detail-page/<str:uuid>/<str:type>/', SummaryDetail.as_view(), name='summary_detail_page'),
    
    
    # -------- Anonymous -----------
    path('doctor-search-list/', AnonymousDoctorListView.as_view(), name='doctor_search_result'),
    path('doctor-search-details/<str:uuid>/', AnonymousDoctorDetailsView.as_view(), name='doctor_search_details'),
    path('requesr-for-call/<str:uuid>/', RequestForCall.as_view(), name='request_for_call'),
    path('dis-connect-call/', DisconnectCall.as_view(), name='dis-connect-caall'),
]