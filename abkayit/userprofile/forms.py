# -*- coding:utf-8  -*-
import logging

from django import forms

from django.forms.models import ModelForm, ModelChoiceField
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import TextInput

from userprofile.models import UserProfile, Accommodation, UserAccomodationPref
from userprofile.dynamicfields import DynmcFields 
from userprofile.userprofileops import UserProfileOPS

log=logging.getLogger(__name__)

class CreateUserForm(ModelForm):
	passwordre = forms.CharField(label=_("Confirm Password"),
									max_length=30,
									widget=forms.PasswordInput(attrs={'placeholder':_('Confirm Password'), 'class':'form-control'})) 
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'password', 'username']
		widgets = {
					'first_name': forms.TextInput(attrs={'placeholder':_('First Name'), 'class':'form-control'}),
					'last_name': forms.TextInput(attrs={'placeholder':_('Last Name'), 'class':'form-control'}),
					'email': forms.EmailInput(attrs={'placeholder':_('Email Address'), 'class':'form-control'}),
					'password': forms.PasswordInput(attrs={'placeholder':_('Password'), 'class':'form-control'}),
					'username': forms.HiddenInput()
				  }
	def __init__(self, *args, **kwargs):
		super(CreateUserForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].required = True
		self.fields['username'].required = False

	def clean_email(self):
		email = self.cleaned_data.get('email')
		users = User.objects.filter(email=email)
		if len(users) > 0:
			raise forms.ValidationError(_("This email address already exists in this system"))
		return email

	def clean_passwordre(self):
		password = self.cleaned_data.get('password')
		passwordre = self.cleaned_data.get('passwordre')
		if password != passwordre:
			raise forms.ValidationError(_("Your passwords do not match"))
		return passwordre
	
	def clean_username(self):
		username = self.cleaned_data.get('email')
		return username	

class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
                    'first_name': forms.TextInput(attrs={'placeholder':_('First Name'), 'class':'form-control'}),
                    'last_name': forms.TextInput(attrs={'placeholder':_('Last Name'), 'class':'form-control'}),
                    'email': TextInput(attrs={'readonly':'readonly'}),
                    'username': forms.HiddenInput()
                  }
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
        self.fields['username'].required = False

class CreateInstForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'password', 'username']
		widgets = {
					'first_name': forms.TextInput(attrs={'placeholder':'Ad'}),
					'last_name': forms.TextInput(attrs={'placeholder':'Soyad'}),
					'email': forms.EmailInput(attrs={'placeholder':'E-posta'}),
					'password': forms.HiddenInput(),
					'username': forms.HiddenInput()
				 }
	def __init__(self, *args, **kwargs):
		super(CreateInstForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].required = True
		self.fields['username'].required = False
		self.fields['password'].required = False

	def clean_email(self):
		email = self.cleaned_data.get('email')
		users = User.objects.filter(email=email)
		if len(users) > 0:
			raise forms.ValidationError(_("This email address already exists in this system"))
		return email
	def clean_username(self):
		username = self.cleaned_data.get('email')
		return username

class InstProfileForm(ModelForm):
	# TODO: egitimci icin form
	class Meta:
		model = UserProfile
		exclude = {}
		fields = ['job', 'title', 'organization', 'country', 'is_instructor', 'is_student', 'is_speaker', 'is_participant', 'user']
		widgets = {
					'is_instructor':forms.HiddenInput(),
					'is_student':forms.HiddenInput(),
					'is_speaker':forms.HiddenInput(),
					'is_participant':forms.HiddenInput(),
					'user':forms.HiddenInput(),
				  }
	def __init__(self, *args, **kwargs):
		super(InstProfileForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].required = True
		self.fields['is_instructor'].required = False
		self.fields['is_student'].required = False
		self.fields['is_speaker'].required = False
		self.fields['is_participant'].required = False
		self.fields['user'].required = False

class StuProfileForm(ModelForm):
	class Meta:
		dyncf = DynmcFields()
		model = UserProfile
		exclude = {}
		# fields=['name','surname','username','email','password','password',]
		widgets = {
					'is_instructor':forms.HiddenInput(),
					'is_student':forms.HiddenInput(),
					'is_speaker':forms.HiddenInput(),
					'is_participant':forms.HiddenInput(),
					'user':forms.HiddenInput(),
					'birthdate': SelectDateWidget(years=dyncf.BirthDateYears),
				 }
	def __init__(self,user=None, *args, **kwargs):
		#User.objects.get(email=request.user)
		self.ruser=kwargs.pop('ruser', None)
		super(StuProfileForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].required = True
		self.fields['tckimlikno'].required=False
		self.fields['ykimlikno'].required=False
		self.fields['is_instructor'].required = False
		self.fields['is_student'].required = False
		self.fields['is_speaker'].required = False
		self.fields['is_participant'].required = False
		self.fields['user'].required = False
		if user:
			try:
				self.fields['user'].initial=user
			except:
				self.fields['user']='1'
	def clean(self):
		cleaned_data = super(StuProfileForm, self).clean()
		ruser = self.ruser
		if ruser:
			first_name = ruser.first_name
			last_name = ruser.last_name
			byear = cleaned_data['birthdate'].year
			if cleaned_data['tckimlikno'] and cleaned_data['ykimlikno']:
				raise forms.ValidationError(_("Please fill only one of them:tckimlikno,ykimlikno"))
			elif not cleaned_data['tckimlikno'] and cleaned_data['country'] == 'TR':
				raise forms.ValidationError(_("TR vatandaslari icin TCKimlikNo bos birakilamaz."))
			elif not cleaned_data['ykimlikno'] and cleaned_data['country'] != 'TR':
				raise forms.ValidationError(_("TR vatandasi olmayanlar icin Yabanci Kimlik No bos birakilamaz."))
			elif cleaned_data['tckimlikno'] and cleaned_data['country'] == 'TR':
				tckisvalid=UserProfileOPS.validateTCKimlikNo(cleaned_data['tckimlikno'], first_name, last_name, byear)
				if tckisvalid == -1:
					raise forms.ValidationError(_("TC Kimlik no dogrulanirken hata olustu"))
				elif not tckisvalid:
					raise forms.ValidationError(_("Kimlik bilgileriniz dogrulanamadi, TC Kimlik numaranizi, adinizi, soyadinizi (Turkce karakterler ile ve birden fazla varsa tam olarak) ve dogum tarihinizi tam olarak yaziniz"))
		else:
			raise forms.ValidationError(_("User not found"))
		return cleaned_data

class SpeProfileForm(ModelForm):
	# TODO: Seminer verecekler icin ayri form
	class Meta:
		model = UserProfile
		exclude = {}
		widgets = {
					'is_instructor':forms.HiddenInput(),
					'is_student':forms.HiddenInput(),
					'is_speaker':forms.HiddenInput(),
					'is_participant':forms.HiddenInput(),
					'user':forms.HiddenInput(),
				  }
class ParProfileForm(ModelForm):
	# TODO: Seminer dinleyecekler icin ayrı form olusturulacak
	class Meta:
		model = UserProfile
		exclude = {}
		widgets = {
					'is_instructor':forms.HiddenInput(),
					'is_student':forms.HiddenInput(),
					'is_speaker':forms.HiddenInput(),
					'is_participant':forms.HiddenInput(),
					'user':forms.HiddenInput(),
				  }

class ChangePasswordForm(ModelForm):
	passwordre = forms.CharField(label=_("Confirm Password"),
									max_length=30,
									widget=forms.PasswordInput(attrs={'placeholder':_('Confirm Password'), 'class':'form-control'})) 
	class Meta:
		model = User
		fields = ['password']
		widgets = {'password': forms.PasswordInput(attrs={'placeholder':_('Password'), 'class':'form-control'})}
	def __init__(self, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].required = True

	def clean_passwordre(self):
		password = self.cleaned_data.get('password')
		passwordre = self.cleaned_data.get('passwordre')
		if password != passwordre:
			raise forms.ValidationError(_("Your passwords do not match"))
		return passwordre

class AccomodationPrefForm(forms.Form):
	achoices=Accommodation.objects.filter(usertype__in=['stu','hepsi']).values_list('id','name').order_by('name')
	accomodation = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=achoices)
	def __init__(self,achoices=None, *args, **kwargs):
		super(AccomodationPrefForm, self).__init__(*args, **kwargs)
		if achoices:
			self.fields['accomodation'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=achoices)
