from rest_framework import serializers
from .models import Like, Comment, Subscription, Video
from django.utils.timezone import now
from . models import VideoViews,Video
from django.db.models import Case, When

class LikeSerializers(serializers.ModelSerializer):
	class Meta:
		model = Like
		fields = '__all__'

class CommentSerializers(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = '__all__'

class SubscriptionSerializers(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = '__all__'


class VideoSerializers(serializers.ModelSerializer):
	channel_name = serializers.CharField(source='user.get_full_name')
	channel_photo = serializers.ImageField(source='user.userprofileinfo.profile_photo')
	view_time_since = serializers.SerializerMethodField()

	class Meta:
		model = Video
		exclude = ['video','video_desc','added_time']

	def get_view_time_since(self, obj):
		all_views = VideoViews.objects.filter(video_id__id=obj.id)
		ids = []
		for i in reversed(all_views):
			ids.append(i.viewer.pk)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
		video = Video.objects.filter(pk__in=ids).order_by(preserved)

		views_count = video.count()

		dd = (now() - obj.added_time).days
		if dd < 7:
			return str(views_count) + " views  •  " + str(int(dd)) + " days ago"
		elif dd < 31:
			return str(views_count) + " views  •  " + str(int(dd/7)) + " weeks ago"
		elif dd < 365:
			return str(views_count) + " views  •  " + str(int(dd/30)) + " months ago"
		else:
			return str(views_count) + " views  •  " + str(int(dd/365)) + " year ago"
