from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
import json
from datetime import datetime

from django.db.models import Case, When
from django.contrib.auth.models import User
from . models import UserProfileInfo,Video,Comment,Like,VideoViews,Subscription
from .forms import UserForms,UserProfileInfoForm

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LikeSerializers,CommentSerializers,SubscriptionSerializers,VideoSerializers

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer

from django.views import generic

from .task import subs_mail,upload_video_mail
from rest_framework.pagination import PageNumberPagination

class Base(generic.ListView):
	serializer_class = SubscriptionSerializers
	context_object_name = 'subs_chnl'
	template_name = "youtube_app/defaultvideo.html"

	def get_queryset(self):
		if self.request.user.is_authenticated:
			return Subscription.objects.filter(subscribers=self.request.user)
	
class CP(PageNumberPagination):
	page_size = 4

class LoadMore(generics.ListAPIView):
	queryset = Video.objects.all().order_by('id')
	serializer_class = VideoSerializers
	pagination_class = CP

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
	
		video = Video.objects.create(user=request.user,video_thumbnail=video_thumbnail,video_title=video_title,video=video,video_desc=video_desc)
		upload_video_mail.delay(str(video_title), str(request.user))
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

	else:
		user_subs = None

	if photo.cover_photo:
		coverphoto = photo.cover_photo
	else:
		coverphoto = None

	chnl_subs = Subscription.objects.filter(channel_owner=pk)

	context = {'allvideos':owner_videos, 'allviews':Allviews, 'cover_photo':coverphoto, 'profile_photo':photo.profile_photo, 'full_name':photo, 'subs_chnl':user_subs, 'chnl_subs':chnl_subs}

	return render(request,'youtube_app/channel.html',context)

@login_required(login_url='/login')
def likevideo_page(request):
	like_video = Like.objects.filter(liker=request.user, like=True).order_by("-like_time")
	user_subs = Subscription.objects.filter(subscribers=request.user)
	
	context = {"video":like_video, 'subs_chnl':user_subs, "type":"liked"}
	return render(request,'youtube_app/like_and_history.html',context)

@login_required(login_url='/login')
def history(request):
	history = VideoViews.objects.filter(viewer=request.user)
	user_subs = Subscription.objects.filter(subscribers=request.user)

	ids = []
	for i in reversed(history):
		ids.append(i.video_id.pk)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	video = Video.objects.filter(pk__in=ids).order_by(preserved)

	context = {"video":video, 'subs_chnl':user_subs, "type":"history"}
	return render(request,'youtube_app/like_and_history.html',context)

def video(request,id):
	vp = Video.objects.get(id=id)
	comments = Comment.objects.filter(video_id=id)
	likes = Like.objects.filter(video_id=id,like=True)

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
	
	context = {'video':vp, 'allcomments':comments, 'all_likes':likes, 'all_view':video, 'subs_chnl':user_subs, 'subornot':subornot, 'lkornt':lkornt}
	
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
	

class Addlike(generics.CreateAPIView, generics.UpdateAPIView):
	queryset = Like.objects.all()
	serializer_class = LikeSerializers
	permission_classes = [IsAuthenticated]

	def create(self, request, *args,**kwargs):
		request.data["liker"] = str(request.user.id)
		orginal_response = super(Addlike, self).create(request, *args, **kwargs)
		return Response('like is added', status=status.HTTP_201_CREATED)

	def update(self, request, *args, **kwargs):
		request.data.update({'liker':request.user.id,'like_time':datetime.now()})
		lkup = Like.objects.get(video_id=request.data["video_id"],liker=request.data["liker"])
		serializer = self.get_serializer(lkup, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)
		if request.data["like"] == 'True':
			return Response('like is added', status=status.HTTP_201_CREATED)
		elif request.data["like"] == 'False':
			return Response('like is remove', status=status.HTTP_201_CREATED)

class Subscript(generics.CreateAPIView):
	queryset = Subscription.objects.all()
	serializer_class = SubscriptionSerializers
	permission_classes = [IsAuthenticated]

	def create(self, request, *args, **kwargs):
		request.data["subscribers"] = str(request.user.id)
		orginal_response = super(Subscript, self).create(request, *args, **kwargs)
		channel_name = User.objects.get(id=request.data['channel_owner'])
		subs_mail.delay(channel_name.get_full_name(),request.data['count'])
		return Response(f"You Subscribes {channel_name.get_full_name()}'s Channel", status=status.HTTP_201_CREATED)


def subscription_page(request):
	vp = Video.objects.all()
	user_subs = Subscription.objects.filter(subscribers=request.user)
	Allviews = VideoViews.objects.all()

	Allvideo = []
	for i in user_subs:
		oo = Video.objects.filter(user=i.channel_owner)
		Allvideo.append(oo)
	context = {'allvideos':Allvideo, 'allviews':Allviews, 'subs_chnl':user_subs}

	return render(request,'youtube_app/subscription.html',context)
		
def search(request):
	search_parameter = request.GET['search_query']

	if search_parameter != "":
		allvd = Video.objects.filter(video_title__icontains=search_parameter) | Video.objects.filter(user__first_name__icontains=search_parameter)
		Allviews = VideoViews.objects.all()
		result_list = list(allvd)

		context = {'allvideos':result_list, 'allviews':Allviews}

		if request.user.is_authenticated:
			user_subs = Subscription.objects.filter(subscribers=request.user)
			context['subs_chnl'] = user_subs

		return render(request,'youtube_app/search.html',context)

	else:
		messages.warning(request,"Please Type Some Text!")
		return redirect("base")





