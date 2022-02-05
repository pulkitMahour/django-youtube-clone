from django.contrib import admin
from . models import UserProfileInfo,Video,Comment,Like,VideoViews,Subscription
# Register your models here.

admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(UserProfileInfo)
admin.site.register(Like)
admin.site.register(VideoViews)
admin.site.register(Subscription)