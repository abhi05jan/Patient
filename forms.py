from django import forms
from django.forms import ValidationError
from django.db.models import Q


from phonenumber_field.formfields import PhoneNumberField


from account.models import (
    User,
    Language,
    Country,
    State,
    City,
    MedicalHistory,
    SurgicalHistory,
    ObstetricsHistory,
    HelpAndSupport
)
from patient.models import (
    PatientPersonalProfile,
    GENDER,
    PatientMedicaleHistory,
    PatientDisease,
    PlanPurchaseHistory,
    PatientWallet,
    LabResult
)
from utility.s3 import upload_user_image


class UpdatePatientProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField()
    email = forms.EmailField(required=False)
    birth_date = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=GENDER, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    step = forms.CharField(required=False)
    other_lan = forms.CharField(required=False)
    primary_hospitale = forms.ModelChoiceField(queryset=User.objects.filter(
        active=True, role__role=1), required=False, empty_label="Select Primary Hospital")
    primary_doctor = forms.ModelChoiceField(queryset=User.objects.filter(
        active=True, role__role=1), required=False, empty_label="Select Primary Doctor")
    obstetric_history = forms.ModelChoiceField(queryset=ObstetricsHistory.objects.available(
    ), required=False, empty_label="Select Obstetrics History")
    surgical_history = forms.ModelMultipleChoiceField(
        queryset=SurgicalHistory.objects.available(), required=False)
    medicale_history = forms.ModelMultipleChoiceField(
        queryset=MedicalHistory.objects.available(), required=False)
    language = forms.ModelMultipleChoiceField(
        queryset=Language.objects.available(), required=False)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'gender',
            'address',
            'birth_date',
            'primary_hospitale',
            'primary_doctor',
            'medicale_history',
            'surgical_history',
            'language',
            'obstetric_history',
            'step',
            'other_lan'
        )

    def clean_phone_number(self):
        field = self.cleaned_data['phone_number']
        if User.objects.exclude(pk=self.instance.pk).filter(phone_number=field).exists():
            raise ValidationError('Phone already exists')
        return field

    def save(self):
        personal_info_data = {
            'country_id': self.data['country'],
            'state_id': self.data['state'],
            'city_id': self.data['city'],
            'birth_date': self.cleaned_data.pop('birth_date'),
            'address': self.cleaned_data.pop('address'),
            'step': self.cleaned_data.pop('step')
        }
        if 'gender' in self.cleaned_data and self.cleaned_data['gender'] != "":
            gender = self.cleaned_data.pop('gender')
            personal_info_data['gender'] = gender
        if 'other_lan' in self.cleaned_data and self.cleaned_data['other_lan'] != "":
            personal_info_data['other_lan'] = self.cleaned_data.pop(
                'other_lan')
        medicle_history_data = {
            'primary_hospitale': self.cleaned_data.pop('primary_hospitale'),
            'primary_doctor': self.cleaned_data.pop('primary_doctor'),
            'obstetric_history': self.cleaned_data.pop('obstetric_history'),
        }
        patient, created = PatientPersonalProfile.objects.update_or_create(
            user=self.instance, defaults=personal_info_data)
        patient.language.add(*self.cleaned_data.pop('language'))
        obj, created = PatientMedicaleHistory.objects.update_or_create(
            user=self.instance, defaults=medicle_history_data)

        obj.medicale_history.add(*self.cleaned_data.pop('medicale_history'))
        obj.surgical_history.add(*self.cleaned_data.pop('surgical_history'))
        get_inut_id = [int(p.split('_')[1])
                       for p in self.data if 'desease_' in p]
        for data in get_inut_id:
            try:
                data_bj = PatientDisease.objects.get(
                    user=self.instance, primary_desease_id=self.data['desease_'+str(data)])
                data_bj.desease = self.data.get('name_'+str(data))
                data_bj.save()
            except:
                PatientDisease.objects.create(
                    user=self.instance,
                    primary_desease_id=self.data['desease_'+str(data)],
                    desease=self.data.get('name_'+str(data))
                )
        PatientDisease.objects.filter(
            ~Q(primary_desease_id__in=get_inut_id), user=self.instance).delete()
        if 'image' in self.files and self.files['image'] != "":
            data, url = upload_user_image(
                self.data['x'],
                self.data['y'],
                self.data['width'],
                self.data['height'],
                self.files['image']
            )
            self.instance.image = url
            self.instance.save()
        return super().save()


class MakePaymentFormForm(forms.ModelForm):

    class Meta:
        model = PlanPurchaseHistory
        fields = (
            'user', 'plan', 'card_number', 'card_name'
        )

    def save(self):
        add_coin = 0
        if hasattr(self.instance.user, 'patientwallet'):
            add_coin = self.instance.user.patientwallet.wallet
        total_coin = add_coin + self.instance.plan.coin
        try:
            PatientWallet.objects.create(
                user=self.instance.user, wallet=self.instance.plan.coin)
        except:
            PatientWallet.objects.filter(
                user=self.instance.user).update(wallet=total_coin)
        return super().save()


class HelpAndSupportForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True)

    class Meta:
        model = HelpAndSupport
        fields = (
            "name", "phone_number", "email", "message", "user"
        )

    def clean_message(self):
        field = self.cleaned_data['message']
        if field is None or field == "":
            raise ValidationError('This field is required.')
        return field


class LabResultForm(forms.ModelForm):

    class Meta:
        model = LabResult
        fields = ("test_name", "test_date", "patient", 'description')
