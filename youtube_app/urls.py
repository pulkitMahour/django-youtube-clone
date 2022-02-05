from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
	path('',views.base,name='base'),
	path('signup/',views.signup,name='signup'),
	path('login/',views.user_login,name='login'),
	path('logout/',views.user_logout,name='logout'),
	path('videoupload/',views.videoupload,name='videoupload'),
	path('video/<int:id>/',views.video,name='video'),
	path('videosearch/',views.search,name='videosearch'),
	path('likevideo/',views.liked,name='likevideo'),
	path('addcomment/',views.add_comment,name='addcomment'),
	path('allchannel/<int:pk>/',views.all_channel,name='allchannel'),
	path('likevideo_page/',views.likevideo_page,name='likevideo_page'),
	path('history/',views.history,name='history'),
	path('subscription/',views.subscription,name='subscription'),
]