from django import template
from youtube_app.models import Video
from django.db.models import Case, When

register = template.Library()

def filterview(value,elements):

	all_views = value.filter(video_id__id=elements)

	ids = []
	for i in reversed(all_views):
		ids.append(i.viewer.pk)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	video = Video.objects.filter(pk__in=ids).order_by(preserved)

	views_count = video.count()
	
	return views_count

register.filter("filter_view",filterview)