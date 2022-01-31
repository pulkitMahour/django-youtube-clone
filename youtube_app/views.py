from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django. db. models import Q
from itertools import chain
from django.db import IntegrityError
import json
import base64

from django.contrib.auth.models import User
from . models import UserProfileInfo,Video,Comment,Like,VideoViews
from .forms import UserForms,UserProfileInfoForm

# Create your views here.

def base(request):
	Allvideo = Video.objects.all()
	Allviews = VideoViews.objects.all()
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

def your_channel(request):
	user_video = Video.objects.filter(user=request.user)
	Allviews = VideoViews.objects.all()
	context = {'allvideos':user_video, 'allviews':Allviews}
	return render(request,'youtube_app/defaultvideo.html',context)

def all_channel(request,pk):
	video = Video.objects.get(pk=pk)
	owner = video.user
	
	photo = UserProfileInfo.objects.get(user__username=owner)
	if photo.cover_photo != None:
		coverphoto = photo.cover_photo
	else:
		coverphoto = None

	owner_videos = Video.objects.filter(user=owner)
	Allviews = VideoViews.objects.all()
	context = {'allvideos':owner_videos, 'allviews':Allviews, 'cover_photo':coverphoto, 'profile_photo':photo.profile_photo, 'full_name':owner.get_full_name()}

	return render(request,'youtube_app/channel.html',context)

def video(request,id):
	vp = Video.objects.get(id=id)
	comments = Comment.objects.filter(video_id=id)
	likes = Like.objects.filter(video_id=id)

	if request.user.is_authenticated:
		views = VideoViews.objects.filter(viewer=request.user, video_id=vp)
		if not views:
			addview = VideoViews.objects.create(viewer=request.user,video_id=vp)
	
	all_view = VideoViews.objects.filter(video_id=id)

	context = {'video':vp, 'allcomments':comments, 'all_likes':likes, 'all_view':all_view}
	
	return render(request,'youtube_app/video.html',context)


@login_required(login_url='/login')
def add_comment(request):

	jsn_data=json.loads(request.GET.get('comment', ''))
	if jsn_data["comment"] != '':
	
		dp = UserProfileInfo.objects.get(user=request.user)
		vi = Video.objects.get(pk=jsn_data["video_pk"])
		addcomment = Comment.objects.create(commenter=request.user,commenter_dp=dp,video_id=vi,comments=jsn_data["comment"])

		image = dp.profile_photo
		show_comment = {'fullname':jsn_data["user"],'comment':jsn_data["comment"],'profile':str(image.url)}
		py_dict = json.dumps(show_comment)

		return HttpResponse(py_dict)
	else:
		return HttpResponse("Please Type Something In The Comment Box")

@login_required(login_url='/login')
def liked(request):
	try:
		jsn_data = json.loads(request.GET.get('data', ''))

		vi = Video.objects.get(pk=jsn_data["video_pk"])
		addlike = Like.objects.create(liker=request.user,video_id=vi,like=True)
		
		return HttpResponse("like is added")
		
	except IntegrityError as e:
		return HttpResponse("you have already like this video")
		
def search(request):
	search_parameter = request.GET['search_query']
	allvd = Video.objects.filter(video_title__startswith=search_parameter) | Video.objects.filter(user__first_name__startswith=search_parameter)
	Allviews = VideoViews.objects.all()
	result_list = list(allvd)

	context = {'allvideos':result_list, 'allviews':Allviews}
	return render(request,'youtube_app/defaultvideo.html',context)





