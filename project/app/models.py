from django.db import models
from django.contrib.auth.models import User

class MediaFile(models.Model):
    verbose_name = 'Your Notification'

    STATUS_CHOICES = [
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]

    MEDIA_TYPES = [
        ('pdf','Pdf'),
        ('image','Image'),
        ('unknown','Unknown Format')
    ]

    title = models.CharField(max_length=255,default="none")
    remarks = models.TextField(default="")
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='pending')
    media_type = models.CharField(max_length=10,choices=MEDIA_TYPES,default='unknown')
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    class Meta:
        verbose_name = 'Uploaded Document'


class Notification(models.Model):
    recipient = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def _str__(self):
        return f"To: {self.recipient.username} - {self.message[:30]}"
    class Meta:
        verbose_name = 'Your Notification'