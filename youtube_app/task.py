from celery import shared_task
from . models import UserProfileInfo,Video,Comment,Like,VideoViews,Subscription
from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from youtube_project import settings
from django.utils import timezone
from datetime import timedelta


def send_mail_7(mail_subject,message,users):
	kk = send_mail(
		subject = mail_subject,
		message=message,
		from_email=settings.EMAIL_HOST_USER,
		recipient_list=[users],
		fail_silently=True,
		)
	return kk

@shared_task(bind=True)
def subs_mail(self,ownm,count):
	# users = get_user_model().objects.get(username=ownm).email
	users = get_user_model().objects.get(username="Pulkit").email
	
	mail_subject = f"Hi {ownm}"
	message = f"You have a new subscriber \n And now your subscriber's count is {count}."
	# send_mail_7(mail_subject,message,users)
	
	return "EMAIL to channel owner is sent"

@shared_task(bind=True)
def upload_video_mail(self,title,name):
	all_sub = Subscription.objects.filter(channel_owner__username=name)

	for i in all_sub:
		mail_subject = f"Hi {i.subscribers.username}"
		message = f"{name} is upladed a new video titled {title}."
		# send_mail_7(mail_subject,message,i.subscribers.email)

	return "EMAIL to video uploader is sent"

@shared_task(bind=True)
def mail_to_subscribers(self):
	all_user = get_user_model().objects.all()
	x = {}
	y = ""
	for i in all_user:
		cc = Subscription.objects.filter(subscribers=i)
		if cc:
			for j in cc:
				dd = Video.objects.filter(user=j.channel_owner)
				for k in dd:
					y += k.video_title+", \n" 
			x[i.email] = y
			y = ""
	
	for key, value in x.items():
		users = key
		mail_subject = f"Hi {key}"
		message = value
		send_mail_7(mail_subject,message,users)

	return "EMAIL to subscribers with subscribed channel's video title is sent"





