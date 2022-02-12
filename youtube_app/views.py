from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django. db. models import Q
from itertools import chain
from django.db import IntegrityError
import json
import base64
from datetime import datetime

from django.db.models import Case, When
from django.contrib.auth.models import User
from . models import UserProfileInfo,Video,Comment,Like,VideoViews,Subscription
from .forms import UserForms,UserProfileInfoForm

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LikeSerializers,CommentSerializers,SubscriptionSerializers

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

def base(request):
	Allvideo = Video.objects.all()
	Allviews = VideoViews.objects.all()
	
	if str(request.user) != 'AnonymousUser':
		user_subs = Subscription.objects.filter(subscribers=request.user)
		profile = UserProfileInfo.objects.all()
		
		context = {'allvideos':Allvideo, 'allviews':Allviews, 'subs_chnl':user_subs, 'chnl_pic':profile}
	else:
		context = {'allvideos':Allvideo, 'allviews':Allviews}

	return render(request,'youtube_app/defaultvideo.html',context)

@login_required
def user_logout(request):
	logout(request)
	return render(request, 'youtube_app/defaultvideo.html')

def signup(request):
	if request.method == 'POST':
		user_form = UserForms(data=request.POST)
		profile_form = UserProfileInfoForm(data=request.POST)
		password = request.POST['password']
		cpassword = request.POST['cpassword']
		if cpassword != password:
			messages.warning(request,"Password Dosn't Match")
			user_form = UserForms()
			profile_form = UserProfileInfoForm()
			return redirect('signup')
		else:
			if user_form.is_valid() and profile_form.is_valid():
				user = user_form.save()
				user.set_password(user.password)
				user.save()
				profile = profile_form.save(commit=False)
				profile.user = user

				if 'profile_photo' in request.FILES:
					profile.profile_photo = request.FILES['profile_photo']

				if 'cover_photo' in request.FILES:
					profile.cover_photo = request.FILES['cover_photo']

				profile.save()
				
				if user:
					return redirect('login')
			else:
				return HttpResponse("This Email Address and Password is already exist")
	else:
		user_form = UserForms()
		profile_form = UserProfileInfoForm()
	return render(request,'youtube_app/signup.html',{})


def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username,password=password)
		if user:
			if user.is_active:	
				login(request,user)
				return redirect("base")
			else:
				return render(request,"account not active")
		else:
			messages.warning(request,"Invalid Username and Password")
			return redirect("login")
	return render(request,'youtube_app/login.html',{})


def videoupload(request):
	context = {}
	if request.method == 'POST':
		video_title = request.POST['videoTitle']
		video = request.FILES['video']
		video_thumbnail = request.FILES['thumbnail']
		video_desc = request.POST['description']
		channel_thumbnail = UserProfileInfo.objects.get(user=request.user)
	
		video = Video.objects.create(user=request.user,video_thumbnail=video_thumbnail,video_title=video_title,video=video,video_desc=video_desc,channel_thumbnail=channel_thumbnail)
		if video:
			sab = Video.objects.filter(user=request.user)
			context = {'uploaded':True,'videos':sab}

	return render(request,'youtube_app/videoupload.html',context)

def all_channel(request,pk):
	owner_videos = Video.objects.filter(user=pk)
	Allviews = VideoViews.objects.all()
	photo = UserProfileInfo.objects.get(user=pk)

	if str(request.user) != 'AnonymousUser':
		user_subs = Subscription.objects.filter(subscribers=request.user)
		profile = UserProfileInfo.objects.all()

	else:
		user_subs = None
		profile = None

	if photo.cover_photo:
		coverphoto = photo.cover_photo
	else:
		coverphoto = None

	chnl_subs = Subscription.objects.filter(channel_owner=pk)

	context = {'allvideos':owner_videos, 'allviews':Allviews, 'cover_photo':coverphoto, 'profile_photo':photo.profile_photo, 'full_name':photo, 'subs_chnl':user_subs, 'chnl_pic':profile, 'chnl_subs':chnl_subs}

	return render(request,'youtube_app/channel.html',context)

@login_required(login_url='/login')
def likevideo_page(request):
	like_video = Like.objects.filter(liker=request.user, like=True).order_by("-like_time")
	user_subs = Subscription.objects.filter(subscribers=request.user)
	profile = UserProfileInfo.objects.all()

	context = {"video":like_video, 'subs_chnl':user_subs, 'chnl_pic':profile, "type":"liked"}
	return render(request,'youtube_app/like_and_history.html',context)


@login_required(login_url='/login')
def history(request):
	history = VideoViews.objects.filter(viewer=request.user)
	user_subs = Subscription.objects.filter(subscribers=request.user)
	profile = UserProfileInfo.objects.all()

	ids = []
	for i in reversed(history):
		ids.append(i.video_id.pk)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	video = Video.objects.filter(pk__in=ids).order_by(preserved)

	context = {"video":video, 'subs_chnl':user_subs, 'chnl_pic':profile, "type":"liked"}
	return render(request,'youtube_app/like_and_history.html',context)


def video(request,id):
	vp = Video.objects.get(id=id)
	comments = Comment.objects.filter(video_id=id)
	likes = Like.objects.filter(video_id=id,like=True)
	profile = UserProfileInfo.objects.all()

	if request.user.is_authenticated:
		subornot = Subscription.objects.filter(channel_owner=vp.user,subscribers=request.user)
		addview = VideoViews.objects.create(viewer=request.user,video_id=vp)

		likedornot = Like.objects.filter(video_id=id,liker=request.user)
		if likedornot:
			lkornt = likedornot
		else:
			lkornt = None
	else:
		subornot = None
		lkornt = None

	all_view = VideoViews.objects.filter(video_id=id)
	ids = []
	for i in reversed(all_view):
		ids.append(i.viewer.pk)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	video = Video.objects.filter(pk__in=ids).order_by(preserved)

	user_subs = Subscription.objects.filter(channel_owner=vp.user)
	
	context = {'video':vp, 'allcomments':comments, 'all_likes':likes, 'all_view':video, 'all_profile':profile, 'subs_chnl':user_subs, 'subornot':subornot, 'lkornt':lkornt}
	
	return render(request,'youtube_app/video.html',context)


@login_required(login_url='/login')
@api_view(['POST'])
def add_comment(request):

	if request.method == "POST":
		if request.data["comments"] != '':
			request.data["commenter"] = str(request.user.id)
			serializers = CommentSerializers(data=request.data)
			if serializers.is_valid():
				serializers.save()
				
			image = UserProfileInfo.objects.get(user=request.user).profile_photo

			show_comment = {'fullname':request.user.get_full_name(),'comment':request.data["comments"],'profile':str(image.url)}
			py_dict = json.dumps(show_comment)

			return HttpResponse(py_dict)
		else:
			return HttpResponse("Please Type Something In The Comment Box")
	
# @login_required(login_url='/login')
@api_view(['POST','PUT'])
@permission_classes((IsAuthenticated, ))
def liked(request):
	if request.method == "POST":
		request.data["liker"] = str(request.user.id)
		serializers = LikeSerializers(data=request.data)
		if serializers.is_valid():
			serializers.save()
			return HttpResponse(json.dumps({'added': 'like is added'}), content_type='application/json')
		else:
			return HttpResponse("You have already like this video",status=status.HTTP_404_NOT_FOUND)

	if request.method == "PUT":
		print("\n\n\n",request.data,"\n\n\n")

		request.data["liker"] = str(request.user.id)
		request.data["like_time"] = datetime.now()

		lkup = Like.objects.get(video_id=request.data["video_id"],liker=request.data["liker"])
		serializers = LikeSerializers(lkup, data=request.data, partial=True)

		if request.data["like"] == 'True':
			if serializers.is_valid():
				serializers.save()
				return HttpResponse(json.dumps({'added': 'like is added'}), content_type='application/json')

		elif request.data["like"] == 'False':
			if serializers.is_valid():
				serializers.save()
				return HttpResponse(json.dumps({'added': 'like is remove'}), content_type='application/json')


@login_required(login_url='/login')
@api_view(['POST'])	
def subscription(request):
	if request.method == "POST":
		request.data["subscribers"] = str(request.user.id)
		serializers = SubscriptionSerializers(data=request.data)
		if serializers.is_valid():
			channel_name = User.objects.get(id=request.data['channel_owner'])
			serializers.save()
			return HttpResponse(json.dumps({'response':f"You Subscribes {channel_name.get_full_name()}'s Channel"}), content_type='application/json')
		else:
			return HttpResponse("You have already subscribes this channel",status=status.HTTP_404_NOT_FOUND)

def subscription_page(request):
	vp = Video.objects.all()
	user_subs = Subscription.objects.filter(subscribers=request.user)
	profile = UserProfileInfo.objects.all()
	Allviews = VideoViews.objects.all()

	Allvideo = []
	for i in user_subs:
		oo = Video.objects.filter(user=i.channel_owner)
		Allvideo.append(oo)
	context = {'allvideos':Allvideo, 'allviews':Allviews, 'subs_chnl':user_subs, 'chnl_pic':profile}

	return render(request,'youtube_app/subscription.html',context)
		
def search(request):
	search_parameter = request.GET['search_query']

	if search_parameter != "":
		allvd = Video.objects.filter(video_title__icontains=search_parameter) | Video.objects.filter(user__first_name__icontains=search_parameter)
		Allviews = VideoViews.objects.all()
		result_list = list(allvd)

		if str(request.user) != 'AnonymousUser':
			user_subs = Subscription.objects.filter(subscribers=request.user)
			profile = UserProfileInfo.objects.all()
			
			context = {'allvideos':result_list, 'allviews':Allviews, 'subs_chnl':user_subs, 'chnl_pic':profile}
		else:
			context = {'allvideos':result_list, 'allviews':Allviews}

		return render(request,'youtube_app/defaultvideo.html',context)

	else:
		messages.warning(request,"Please Type Some Text!")
		return redirect("base")




