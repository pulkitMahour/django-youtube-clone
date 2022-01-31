from django import forms
from django.contrib.auth.models import User
from youtube_app.models import UserProfileInfo

class UserForms(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta():
		model = User
		fields = ('username','first_name','last_name','email','password')

class UserProfileInfoForm(forms.ModelForm):

	class Meta():
		model = UserProfileInfo
		fields = ('profile_photo','age','cover_photo')