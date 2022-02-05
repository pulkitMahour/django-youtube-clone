from rest_framework import serializers
from .models import Like, Comment, Subscription


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
