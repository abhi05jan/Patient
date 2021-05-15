import uuid
import random


from phonenumber_field.modelfields import PhoneNumberField


from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


from account.models import (
    User,
    Language,
    Country,
    State,
    City,
    MedicalHistory,
    SurgicalHistory,
    ObstetricsHistory,
    DiseaseHistory,
    Investigations,
    JoinReferral
)
from utility.models import BaseModel
from utility.helpers import filename_path
from adminmanagement.models import PlanFeature

def patient_summary(instance, filename):
    return filename_path('patient/summary', instance, filename)

def lab_attachment(instance, filename):
    return filename_path('patient/lab/attachment', instance, filename)

GENDER = (
    (1, 'Male'),
    (2, 'Female'),
    (3, 'Other'),
)


class PatientPersonalProfile(BaseModel):
    user = models.OneToOneField(
        User,  on_delete=models.CASCADE, related_name="patient_profile")
    other_lan = models.TextField(null=True, blank=True)
    language = models.ManyToManyField(Language)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,  null=True, blank=True)
    step = models.CharField(max_length=5, null=True, blank=True, default='')
    gender = models.IntegerField(choices=GENDER, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)


class PatientMedicaleHistory(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="medicale_history")
    primary_hospitale =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="primar_hospitale")
    primary_doctor =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,  related_name="primar_doctor")
    medicale_history =  models.ManyToManyField(MedicalHistory)
    surgical_history =  models.ManyToManyField(SurgicalHistory)
    obstetric_history =  models.ForeignKey(ObstetricsHistory, on_delete=models.CASCADE, null=True, blank=True)


class PatientWallet(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patientwallet")
    wallet = models.FloatField(default=0.0)


class PatientDisease(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_desease")
    primary_desease =  models.ForeignKey(DiseaseHistory, on_delete=models.CASCADE, null=True, blank=True)
    desease = models.TextField(null=True, blank=True)


class PlanPurchaseHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plan_purchase")
    plan = models.ForeignKey(PlanFeature, on_delete=models.CASCADE)
    card_number = models.CharField(
        max_length=16, null=False, blank=False, default='')
    card_name = models.CharField(
        max_length=100, null=False, blank=False, default='')
    charge_id = models.CharField(
        max_length=100, null=False, blank=False, default='')


class FollowUnfollow(BaseModel):
    follow_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="patient_user")
    follow = models.ForeignKey(User, on_delete=models.CASCADE,related_name="doctor_user")


class CallRequest(BaseModel):
    STATUS = (
        (1, 'Completed'),
        (2, 'Waiting'),
        (3, 'Not Attended'),
        (4, 'Pending'),
        (5, 'Rejected'),
        (6, 'In Progress'),
        (7, 'Cancelled'),

    )
    CALL_TYPE = (
        (1, 'Audio'),
        (2, 'Video'),
    )
    REJECTED_BY=(
        (1,'Doctor'),
        (2,'Patient'),
        (3,'None'),

    )
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_call')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_call')
    call_type = models.IntegerField(choices=CALL_TYPE, default=1)
    call_status = models.IntegerField(choices=STATUS, default=4)
    rejected_by = models.IntegerField(choices=REJECTED_BY, default=3)
    language = models.ManyToManyField(Language, blank=True, related_name="language_call")
    duration_minutes = models.IntegerField(default=0)
    duration = models.CharField(max_length=100, null=False, blank=False, default='')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ('id',)


class CallRequestNotification(BaseModel):
    STATUS = (
        (1, 'Pending'),
        (2, 'Accept'),
        (3, 'Reject'),
        (4, 'None'),
    )
    TYPE=(
        (1,'CALL REQUEST'),
        (2,'CLINIC STATUS'),
        (3,'FOLLOW'),
        (3,'FOLLOW'),
        (4,'Referral'),

    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_notif_request')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_notif_request')
    call_request = models.ForeignKey(CallRequest, on_delete=models.CASCADE,null=True,related_name='call_notif_request')
    referal = models.ForeignKey(JoinReferral, on_delete=models.CASCADE,null=True,related_name='referal')
    message = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    notification_type =models.IntegerField(choices=TYPE, default=1) 

    class Meta:
        ordering = ('id',)


class Summary(BaseModel):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_summary')
    doctor = models.ForeignKey(User,on_delete=models.CASCADE, related_name='doctor_summary')
    call_request = models.ForeignKey(CallRequest,on_delete=models.CASCADE, related_name='call_request_summary')
    medical_history=models.TextField("Medical History",null=True,blank=True,default='')
    doctor_note=models.TextField("Doctor Note",null=True,blank=True,default='')
    blood_pressure = models.CharField("Blood Pressure",null=True,blank=True,default='',max_length=255)
    pulse_rate = models.CharField("Pulse Rate",null=True,blank=True,default='',max_length=255)
    temperature = models.CharField("Temperature",null=True,blank=True,default='',max_length=255)
    weight = models.CharField("Weight",null=True,blank=True,default='',max_length=255)
    blood_sugar = models.CharField("Blood Sugar",null=True,blank=True,default='',max_length=255)
    saturation = models.CharField("Saturation",null=True,blank=True,default='',max_length=255)
    respiratory_rate = models.CharField("Respiratory Rate",null=True,blank=True,default='',max_length=255)
    urinalysis = models.CharField("Urinalysis",null=True,blank=True,default='',max_length=255)
    impressions = models.TextField("Impressions",null=True,blank=True,default='')
    plan = models.TextField("Plan",null=True,blank=True,default='')
    prescriptions =  models.TextField("Prescriptions",null=True,blank=True,default='')
    investigations =  models.ManyToManyField(Investigations,blank=True, related_name="investigations")
    other_investigation =  models.TextField("Other Investigations",null=True,blank=True,default='')

    class Meta:
        ordering = ('id',)


class SummaryAttachment(BaseModel):
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='attachment_summary')
    attachment = models.FileField(upload_to=patient_summary, blank=True, null=True) 
    class Meta:
        ordering = ('id',)


class LabResult(BaseModel):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_lab_result')
    call_request = models.ForeignKey(CallRequest,on_delete=models.SET_NULL, null=True,  related_name='call_request')
    test_name = models.CharField("Test Name",null=True,blank=True,default='',max_length=255)
    description =  models.TextField("Description", null=True, blank=True, default='')
    test_date = models.DateField("Created Date",)

    class Meta:
        ordering = ('-id',)


class LabResultAttachment(BaseModel):
    lab = models.ForeignKey(LabResult, on_delete=models.CASCADE, related_name='attachment_lab')
    attachment = models.FileField(upload_to=lab_attachment, blank=True, null=True) 
    class Meta:
        ordering = ('id',)
