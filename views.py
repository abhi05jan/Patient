import stripe
import json
from datetime import date, datetime

from django.db.models import Count
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    UpdateView
)
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.views.generic import View
from django.template.loader import render_to_string


from utility.decorator import login_required_front_end
from account.models import (
    User,
    DiseaseHistory,
    Specialties,
    City,
    Country,
    State,
    HelpAndSupport,
)
from doctor.models import (
    DoctorWalletHistory,

)
from utility.pagination import custom_pagination

from patient.forms import (
    UpdatePatientProfileForm,
    MakePaymentFormForm, HelpAndSupportForm,
    LabResultForm,
)
from adminmanagement.models import PlanFeature
from patient.models import (
    PatientWallet,
    Summary,
    FollowUnfollow,
    PlanPurchaseHistory,
    CallRequest,
    CallRequestNotification,
    LabResult,
    LabResultAttachment
)
from doctor.models import DoctorPersonalProfile
from utility.helpers import FirebasePushMessage
from utility.signals import (
    post_save_notificaion,
    dispatch_notification
)
from utility.helpers import ordinal
from utility.helpers import (
    CreateRoom,
    CreateAccessToken,
    TwilioRoom
)

stripe.api_key = settings.SECRET_STRIPE_KEY


@method_decorator(login_required_front_end, name='dispatch')
class UpdatePatientProfileView(UpdateView):
    template_name = "website/patient/complete_profile.html"
    model = User
    form_class = UpdatePatientProfileForm

    def get_object(self):
        self.kwargs['pk'] = self.request.user.pk
        return super(UpdatePatientProfileView, self).get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, 'patient_profile'):
            gender = self.object.patient_profile.gender
            if self.request.user.patient_profile.step == "1":
                context['step'] = 2
        else:
            gender = 0
            context['step'] = 0
        context["gender"] = gender
        context['country'] = Country.objects.available().order_by('-name')
        if hasattr(self.object, 'patient_profile') and self.object.patient_profile.country:
            context['state'] = State.objects.filter(
                country=self.object.patient_profile.country).order_by('name')
        else:
            context['state'] = State.objects.none()
        if hasattr(self.object, 'patient_profile') and self.object.patient_profile.state:
            context['city'] = City.objects.filter(
                state=self.object.patient_profile.state).order_by('name')
        else:
            context['city'] = City.objects.none()
        context['desease'] = DiseaseHistory.objects.available()
        return context

    def get_form(self):
        form = super().get_form()
        user = self.request.user
        if hasattr(self.object, 'patient_profile'):
            form.fields['address'].initial = self.object.patient_profile.address
            form.fields['birth_date'].initial = self.object.patient_profile.birth_date
            form.fields['language'].initial = self.object.patient_profile.language.all()
        if hasattr(self.object, 'medicale_history'):
            form.fields['primary_hospitale'].initial = self.object.medicale_history.primary_hospitale
            form.fields['primary_doctor'].initial = self.object.medicale_history.primary_doctor
            form.fields['medicale_history'].initial = self.object.medicale_history.medicale_history.all()
            form.fields['surgical_history'].initial = self.object.medicale_history.surgical_history.all()
            form.fields['obstetric_history'].initial = self.object.medicale_history.obstetric_history
        form.fields['email'].disabled = True
        form.fields['phone_number'].disabled = True
        form.fields['primary_doctor'].disabled = True
        form.fields['primary_hospitale'].disabled = True
        return form

    def get_success_url(self):
        messages.success(self.request, 'Profile changed successfully.')
        if hasattr(self.object, 'patient_profile') and hasattr(self.object, 'medicale_history'):
            if self.request.user.patient_profile.step == "1":
                return reverse_lazy('patient:update_patient_profile')
            else:
                return reverse_lazy('patient:patient_dashboard')
        return reverse_lazy('patient:patient_dashboard')


@method_decorator(login_required_front_end, name='dispatch')
class PatientDashboardView(TemplateView):
    template_name = "website/patient/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_call_processing:
            self.request.user.is_call_processing = False
            self.request.user.save()
        if 'city' in self.request.session and self.request.session['city'] != 'All':
            context['doctors_near_by_you'] = DoctorPersonalProfile.objects.filter(
                user__publish_docter=True, user__active=True,
                user__deleted=False, city__name__icontains=self.request.session['city']
            ).order_by('-id')[0:3]
        else:
            context['doctors_near_by_you'] = DoctorPersonalProfile.objects.filter(
                user__publish_docter=True,  user__active=True, user__deleted=False
            ).order_by('-id')[0:3]
        context['follow_doctor_by_you'] = FollowUnfollow.objects.filter(
            follow_by=self.request.user).order_by('-id')[0:3]
        total_completed_consultations = CallRequest.objects.filter(
            patient=self.request.user, call_status=1
        ).count()
        context['total_completed_consultations'] = total_completed_consultations
        context['total_lab_result'] = LabResult.objects.filter(
            patient=self.request.user).count()

        self.request.session['doctor_page'] = 1
        if self.request.GET.get('type') == 'calling':
            # ---------------------- Send Push Notification Doctor For Not Attending the Attending Call
            get_call_rqust = CallRequest.objects.filter(
                uuid=self.request.GET.get('call_request'))
            if get_call_rqust and get_call_rqust[0].call_status == 2 or get_call_rqust[0].call_status == 3:
                get_call_rqust.update(call_status=3)
                get_call = get_call_rqust.first()
                data = {
                    "id": get_call.id,
                    'title': 'Call From Doctor',
                    'message': 'DR. {} is calling'.format(get_call.doctor.full_name),
                    'icon': 'firebase-icon.png',
                    'type': "call_not_attended_by_patient",
                    'patient_id': get_call.patient.id,
                    'patient_uuid': str(get_call.patient.uuid),
                    'doctor_uuid': str(get_call.doctor.uuid),
                    'call_uuid': str(get_call.uuid),
                    'doctor_id': get_call.doctor.id,
                    "device_token": get_call.doctor.fcm_token,
                    'user_type': 1
                }
                FirebasePushMessage.send_single_web_message(data)
                messages.success(
                    self.request, 'You have not attended the call.')
        return context

# ---------------------------------------------
# My Walet
# ==========================================


@method_decorator(login_required_front_end, name='dispatch')
class PatientWalletView(ListView):
    template_name = "website/patient/wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MakePaymentFormForm
        context['purchase_history'] = custom_pagination(
            1, PlanPurchaseHistory.objects.filter(
                user=self.request.user), limit=10)
        context['spent_history'] = custom_pagination(
            1, self.request.user.patient_wallet_history.all(
            ).order_by('-id'), limit=10)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = PlanFeature.objects.available().order_by('-id')
        return queryset

    # -------Make Payment --------------------
    def post(self, *args, **kwargs):
        if self.request.is_ajax:
            # -------------------------------Create Card Token
            try:
                str_obj = stripe.Token.create(
                    card={
                        "number": self.request.POST['card_number'],
                        "exp_month": self.request.POST['month'],
                        "exp_year": self.request.POST['year'],
                        "cvc":  self.request.POST['cvv'],
                    },
                )
            except Exception as e:
                data = {'html': str(e).split(':')[1].strip(), 'status': 1}
                return JsonResponse(data)

            # Create Charge By Token
            get_plan_amount = PlanFeature.objects.filter(
                active=True, deleted=False, id=self.request.POST['plan'])
            if get_plan_amount:
                try:
                    charge_obj = stripe.Charge.create(
                        amount=int(get_plan_amount[0].amount)*100,
                        currency="usd",
                        source=str_obj.id,
                        description="Charge create by {}".format(
                            self.request.user.email),
                    )
                    make_payment = MakePaymentFormForm(self.request.POST)
                    if make_payment.is_valid():
                        obj = make_payment.save()
                        obj.charge_id = charge_obj.id
                    data = {'html': "Plan purchased successfully.", 'status': 2}
                    messages.success(
                        self.request, "Plan purchased successfully")
                    return JsonResponse(data)

                except Exception as e:
                    data = {'html': str(e).split(':')[1].strip(), 'status': 1}
                    return JsonResponse(data)
            else:
                data = {
                    'html': "Plan is not available. Please refresh your page.", 'status': 2}
                return JsonResponse(data)
        else:
            data = {'html': "This is not valid request.", 'status': 2}
            return JsonResponse(data)


@method_decorator(login_required_front_end, name='dispatch')
class GetPurchaseHistoryView(View):
    def get(self, request):
        params = request.GET
        purchase_history = custom_pagination(params['page'], PlanPurchaseHistory.objects.filter(
            user=self.request.user), limit=10)
        data = render_to_string(
            'website/patient/purchase_history.html', {'purchase_history': purchase_history})
        return JsonResponse({'status': 200, 'data': data})


@method_decorator(login_required_front_end, name='dispatch')
class GetSpentHistoryView(View):
    def get(self, request):
        params = request.GET
        spent_history = custom_pagination(params['page'], request.user.patient_wallet_history.all(
        ).order_by('-id'), limit=10)
        data = render_to_string(
            'website/patient/spent_history.html', {'spent_history': spent_history})
        return JsonResponse({'status': 200, 'data': data})


@method_decorator(login_required_front_end, name='dispatch')
class DoctorListView(ListView):
    template_name = "website/patient/doctor_listing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialities'] = Specialties.objects.available()
        context['country'] = Country.objects.available()
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=9)
        self.request.session['doctor_page'] = 2
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = queryset = DoctorPersonalProfile.objects.filter(user__publish_docter=True, user__active=True, user__deleted=False)
        if  'city' in self.request.session and self.request.session['city'] != 'All' and 'country' not in self.request.GET:
            queryset = queryset.filter(city__name__icontains=self.request.session['city']
                                       ).order_by('-id')
        elif  'city' in self.request.session and self.request.session['city'] != 'All' and 'country' in self.request.GET and self.request.GET['country'] == "":
            queryset = queryset.filter(city__name__icontains=self.request.session['city']
                                       ).order_by('-id')
        if 'name' in self.request.GET and self.request.GET['name'] != "":
            queryset = queryset.filter(
                Q(user__full_name__icontains=self.request.GET['name']) |
                Q(user__email__icontains=self.request.GET['name'])
            )
        if 'specialities' in self.request.GET and self.request.GET['specialities'] != "":
            queryset = queryset.filter(
                specialties_id=self.request.GET['specialities'])
        if 'country' in self.request.GET and self.request.GET['country'] != "":
            queryset = queryset.filter(
                country_id=self.request.GET['country'])
        if 'clinic_status' in self.request.GET and self.request.GET['clinic_status'] != "":
            queryset = queryset.filter(
                clinic_status=self.request.GET['clinic_status'])
        if 'type' in self.request.GET and self.request.GET.get('type') == "top_doctor":
            queryset = queryset.annotate(count=Count(
                'user__doctor_call__doctor_id')).order_by('-count')
        return queryset


@method_decorator(login_required_front_end, name='dispatch')
class DoctorDetailsView(DetailView):

    template_name = "website/patient/doctor_details.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context['user'].doctor_call.filter(
            created__date=date.today(),
        ).values('patient', 'id')
        queryset = queryset.filter(
            Q(call_status=2) |
            Q(call_status=3)
        )
        context['waiting'] = queryset.count()
        call_request = list(queryset.order_by('-updated'))
        position = [patient for patient, data in enumerate(
            call_request) if data['patient'] == self.request.user.id]
        if position and self.request.user.patient_call.filter(created__date=date.today(), call_status=2, doctor=context['user']).exists():
            context['message'] = "You are on the {} position in the queue. Expected waiting time: {} minutes.".format(
                ordinal(position[0]+1), int(
                    (queryset.count()*context['user'].doctor.specialties.max_minutes) /
                    context['user'].doctor.specialties.max_minutes
                )
            )
        elif self.request.user.patient_call.filter(created__date=date.today(), call_status=4, doctor=context['user']).exists():
            context['message'] = "Your request is pending. Please wait doctor will accept your request"
        elif self.request.user.patient_call.filter(created__date=date.today(), call_status=5, doctor=context['user'], rejected_by=1).exists():
            context['message'] = "Your request is has been rejected by the doctor. Please try again tomorrow."
        elif self.request.user.patient_call.filter(created__date=date.today(), call_status=5, doctor=context['user'], rejected_by=2).exists():
            context['message'] = "You have rejected the call. Please try again tomorrow."
        elif self.request.user.patient_call.filter(created__date=date.today(), call_status=1, doctor=context['user']).exists():
            context['message'] = "Your call has been completed."
        elif self.request.user.patient_call.filter(created__date=date.today(), call_status=3, doctor=context['user']).exists():
            context['message'] = "You have not attend the call. Please wait some time.."
        return context

    def get_object(self, *args, **kwargs):
        obj = User.objects.get(uuid=self.kwargs['uuid'])
        self.kwargs['pk'] = obj.id
        return super(DoctorDetailsView, self).get_object()


@method_decorator(login_required_front_end, name='dispatch')
class FollowUnfollowUpDoctorView(TemplateView):
    template_name = "website/patient/wallet.html"

    # --------------------------
    def post(self, *args, **kwargs):
        if self.request.is_ajax:
            obj = FollowUnfollow.objects.filter(
                follow_by=self.request.user, id=self.request.POST.get('id'))
            if obj:
                obj.delete()
                msg = "Doctor Unfollow Successfully."
                data = {'html': msg, 'status': 1}
            else:
                obj = FollowUnfollow.objects.create(
                    follow_by=self.request.user, follow_id=self.request.POST.get('id'))
                msg = "Doctor follow Successfully"
                data = {'html': msg, 'status': 0}
                dispatch_notification.send(
                    sender=CallRequestNotification, instance=obj, types="follow"
                )
            return JsonResponse(data)
        else:
            data = {'html': "This is not valid request.", 'status': 2}
            return JsonResponse(data)


@method_decorator(login_required_front_end, name='dispatch')
class FollowListView(ListView):
    template_name = "website/patient/follow_list.html"

    def get_context_data(self, **kwargs):
        context = {}
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=9)
        self.request.session['doctor_page'] = 3
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = FollowUnfollow.objects.filter(
            follow_by=self.request.user).order_by('-id')
        return queryset


@method_decorator(login_required_front_end, name='dispatch')
class RequestForCall(View):

    def post(self, request, uuid):
        params = request.POST
        language = request.POST.getlist('language')
        doctor = User.objects.get(uuid=uuid)
        instance, _ = CallRequest.objects.get_or_create(
            doctor=doctor,
            patient=request.user,
            created__date=date.today()
        )
        instance.call_type = int(params['call_type'])
        instance.language.add(*language)
        instance.save()
        messages.success(request, 'Your request is pending.')
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


@method_decorator(login_required_front_end, name='dispatch')
class PatientNotificationListView(ListView):
    template_name = "website/patient/notification_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=5)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = CallRequestNotification.objects.filter(
            receiver=self.request.user).order_by('-id')
        queryset.update(active=True)
        queryset = queryset
        return queryset


@method_decorator(login_required_front_end, name='dispatch')
class HelpView(CreateView):
    model = HelpAndSupport
    form_class = HelpAndSupportForm
    template_name = "website/patient/help.html"

    def get_form(self):
        form = super().get_form()
        user = self.request.user
        form.fields['name'].initial = user.full_name
        form.fields['email'].initial = user.email
        form.fields['phone_number'].initial = user.phone_number
        return form

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                self.request, 'Your help and support request has been submited sucessfully.')
            return redirect("patient:help")
        return render(self.request, self.template_name, {'form': form})


@method_decorator(login_required_front_end, name='dispatch')
class LabResultView(TemplateView):
    template_name = "website/patient/lab_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=20)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = self.request.user.patient_lab_result.all().order_by('-test_date')
        return queryset


@method_decorator(login_required_front_end, name='dispatch')
class AddLabResultView(TemplateView):
    template_name = "website/patient/add_lab_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=10)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = self.request.user.patient_call.filter(
            call_status=1).order_by('-id')
        return queryset

    def post(self, request):
        params = request.POST
        form = LabResultForm(params)
        if form.is_valid():
            instance = form.save(commit=False)
            if 'call_request' in params:
                instance.call_request = CallRequest.objects.get(
                    id=params['call_request'])
            instance.save()
            if 'attachment' in request.FILES:
                for data in request.FILES.getlist('attachment'):
                    LabResultAttachment.objects.create(
                        lab=instance,
                        attachment=data
                    )
            return redirect('patient:lab_result')
        query = custom_pagination(1, self.get_queryset(), limit=10)
        return render(request, 'website/patient/add_lab_result.html', {'query': query, 'form': form})


@method_decorator(login_required_front_end, name='dispatch')
class GetDoctorsView(View):

    def post(self, request):
        params = request.POST
        query = request.user.patient_call.filter(call_status=1).order_by('-id')
        if params['name'] != "":
            try:
                date_obj = datetime.strptime(params['name'], '%Y-%m-%d')
                query = query.filter(
                    created__date=date_obj
                )
            except ValueError:
                query = query.filter(
                    doctor__full_name__icontains=params['name']
                )
        data = render_to_string(
            "website/patient/doctor_table.html", {"query": query})
        return JsonResponse({'data': data})


@method_decorator(login_required_front_end, name='dispatch')
class PatientInviteFriendView(TemplateView):
    template_name = "website/patient/invite_friend.html"


@method_decorator(login_required_front_end, name='dispatch')
class PatientCallView(TemplateView):
    template_name = "website/audio_video/patient_call.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_call_rqust = CallRequest.objects.filter(id=self.request.GET['id'])
        if get_call_rqust:
            get_call = get_call_rqust.first()
            access_token = CreateAccessToken.create_access_token(
                self.request.GET['room_name'], str(
                    get_call.patient.phone_number)
            ).decode('utf-8')
            context['token'] = access_token
            context['room_name'] = self.request.GET['room_name']
            context['room_id'] = self.request.GET['room_id']
            # ---------------------- Send Push Notification Doctor Attending Call
            context['call_request'] = get_call
            data = {
                'id': get_call.id,
                'title': 'Call From Doctor',
                'message': 'DR. {} is calling'.format(get_call.doctor.full_name),
                'icon': 'firebase-icon.png',
                'type': "call_accept_by_patient",
                'patient_id': get_call.patient.id,
                'patient_uuid': str(get_call.patient.uuid),
                'doctor_uuid': str(get_call.doctor.uuid),
                'call_uuid': str(get_call.uuid),
                'doctor_id': get_call.doctor.id,
                'device_token': get_call.doctor.fcm_token,
                'room_name': self.request.GET['room_name'],
                'room_id': self.request.GET['room_id'],
                'access_token': access_token,
                'user_type': 1
            }
            dispatch_notification.send(
                sender=CallRequestNotification, instance=get_call, types="call_accept"
            )
            FirebasePushMessage.send_single_web_message(data)
        # get_call.patient.patientwallet.wallet = get_call.patient.patientwallet.wallet - \
        #     get_call.doctor.doctor.specialties.fees
        # get_call.doctor.doctor.wallet = get_call.doctor.doctor.wallet + \
        #     get_call.doctor.doctor.specialties.fees
        # get_call.patient.patientwallet.save()
        # get_call.doctor.doctor.save()
        # history, _ = DoctorWalletHistory.objects.get_or_create(
        #     patient=get_call.patient,
        #     doctor=get_call.doctor,
        #     call_request=get_call,
        # )
        # history.coin +=  get_call.doctor.doctor.specialties.fees
        # history.save()
        get_call.patient.is_call_processing = True
        get_call.patient.save()
        return context


@method_decorator(login_required_front_end, name='dispatch')
class HistoryView(TemplateView):
    template_name = "website/patient/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=5)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = self.request.user.patient_call.filter(
            call_status=1).order_by('-id')
        return queryset


@method_decorator(login_required_front_end, name='dispatch')
class DisconnectCall(TemplateView):
    template_name = "website/audio_video/patient_call.html"

    def get(self, *args, **kwargs):
        # -- Send Push Notification Doctor For Not Attending the Attending Call**********
        get_call_rqust = CallRequest.objects.filter(
            uuid=self.request.GET.get('call_request'))
        get_call_rqust.update(call_status=5)
        get_call_rqust.update(rejected_by=2)

        get_call = get_call_rqust.first()
        get_room = TwilioRoom.update_room(self.request.GET['room_id'])
        data = {
            "id": get_call.id,
            'title': 'Call From Doctor',
            'message': 'DR. {} is calling'.format(get_call.doctor.full_name),
            'icon': 'firebase-icon.png',
            'type': "call_disconnected_automatically",
            'patient_id': get_call.patient.id,
            'patient_uuid': str(get_call.patient.uuid),
            'doctor_uuid': str(get_call.doctor.uuid),
            'call_uuid': str(get_call.uuid),
            'doctor_id': get_call.doctor.id,
            "device_token": get_call.doctor.fcm_token,
            'user_type': 1
        }
        dispatch_notification.send(
            sender=CallRequestNotification, instance=get_call, types="call_reject"
        )
        FirebasePushMessage.send_single_web_message(data)
        messages.success(self.request, 'You have disconnected the call.')
        return redirect('patient:patient_dashboard')


@method_decorator(login_required_front_end, name='dispatch')
class LabDetailsPage(TemplateView):
    template_name = "website/patient/lab_results_detail.html"

    def get(self, *args, **kwargs):
        objects = LabResult.objects.filter(id=kwargs['pk'])
        if objects:
            get_lab_result = objects
        else:
            get_lab_result = LabResult.objects.filter(
                call_request_id=kwargs['pk'])
        return render(self.request, self.template_name, {'get_lab_result': get_lab_result})


@method_decorator(login_required_front_end, name='dispatch')
class SummaryDetail(TemplateView):
    template_name = "website/patient/summary_details.html"

    def get(self, *args, **kwargs):
        try:
            summary = Summary.objects.get(call_request__uuid=kwargs['uuid'])
        except:
            summary = ''
        return render(self.request, self.template_name, {'get_lab_result': summary, 'type': kwargs['type']})

