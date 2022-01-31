from django import template

register = template.Library()

def filterview(value,elements):

	all_views = value.filter(video_id__id=elements)
	views_count = all_views.count()
	
	return views_count

register.filter("filter_view",filterview)