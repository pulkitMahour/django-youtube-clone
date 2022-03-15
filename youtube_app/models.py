from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfileInfo(models.Model):
	# user = models.OneToOneField(User,on_delete=models.CASCADE,related_name=)
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	age = models.IntegerField(null=True)
	profile_photo = models.ImageField(upload_to='profile_photo',default='/round-account-button-with-user-inside_icon-icons.com_72596.png')
	cover_photo = models.ImageField(upload_to='cover_photo',null=True,blank=True)

	def __str__(self):
		return self.user.username

class Video(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	video_thumbnail = models.ImageField(upload_to="thumbnails")
	video_title = models.CharField(max_length=255)
	video_desc = models.TextField()
	video = models.FileField(upload_to="videos")
	added_time = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.video_title

class VideoViews(models.Model):
	viewer = models.ForeignKey(User,on_delete=models.CASCADE)
	video_id = models.ForeignKey(Video,on_delete=models.CASCADE)
	view_time = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.viewer.username}|{self.video_id.video_title}"

class Like(models.Model):
	liker = models.ForeignKey(User,on_delete=models.CASCADE)
	video_id = models.ForeignKey(Video,on_delete=models.CASCADE)
	like = models.BooleanField(default=False)
	like_time = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ["liker", "video_id"]

	def __str__(self):
		return f"{self.liker.username}|{self.video_id.video_title}"

class Comment(models.Model):
	commenter = models.ForeignKey(User,on_delete=models.CASCADE)
	video_id = models.ForeignKey(Video,on_delete=models.CASCADE)
	comments = models.TextField()
	commented_time = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.commenter.username}|{self.video_id.video_title}"

class Subscription(models.Model):
	channel_owner = models.ForeignKey(User,on_delete=models.CASCADE, related_name='owner')
	subscribers = models.ForeignKey(User,on_delete=models.CASCADE, related_name='follower')
	subscribe_date = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ["channel_owner", "subscribers"]

	def __str__(self):
		return f"{self.channel_owner.username}|{self.subscribers.username}"


	

