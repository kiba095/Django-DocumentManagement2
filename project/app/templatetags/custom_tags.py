from django import template
from app.models import Notification

register = template.Library()

@register.simple_tag
def get_notification_count(user):
    count = Notification.objects.filter(is_read=False,recipient__username=user).count()
    
    if count == 0:
        return ''
    else:
        return count 