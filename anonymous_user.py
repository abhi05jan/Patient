from datetime import date


from django.db.models import Count
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseRedirect
)
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    UpdateView
)
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings


from account.models import (
    Specialties,
    City,
    Country,
    User
)
from doctor.models import DoctorPersonalProfile
from utility.pagination import custom_pagination


class AnonymousDoctorListView(ListView):
    template_name = "website/home/anonymoususer_doctor_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialities'] = Specialties.objects.available()
        context['country'] = Country.objects.available()
        page = self.request.GET.get(
            'page') if 'page' in self.request.GET else 1
        context['query'] = custom_pagination(
            page, self.get_queryset(), limit=9)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = queryset = DoctorPersonalProfile.objects.filter(
            user__publish_docter=True, user__active=True, user__deleted=False)
        if 'type' in self.request.GET and self.request.GET['type'] == 'near_by' and 'city' in self.request.session and self.request.session['city'] != 'All' and 'country' not in self.request.GET:
            queryset = queryset.filter(city__name__icontains=self.request.session['city']
                                       ).order_by('-id')
        elif 'type' in self.request.GET and self.request.GET['type'] == 'near_by' and 'city' in self.request.session and self.request.session['city'] != 'All' and 'country' in self.request.GET and self.request.GET['country'] == "":
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


class AnonymousDoctorDetailsView(DetailView):

    template_name = "website/home/anonymoususer_doctor_detail.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['waiting'] = context['user'].doctor_call.filter(
            created__date=date.today(), call_status=2
        ).count()
        return context

    def get_object(self, *args, **kwargs):
        obj = User.objects.get(uuid=self.kwargs['uuid'])
        self.kwargs['pk'] = obj.id
        return super(AnonymousDoctorDetailsView, self).get_object()
