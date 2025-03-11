from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import MediaFile,Notification
from django.contrib.auth.models import User

@receiver(post_save,sender=MediaFile)
def mediafile_notification(sender,instance,created,**kwargs):

    admin_group = User.objects.filter(groups__name="admin_group").first()

    if created:
        #Notify Admin when a new file is uploaded
        Notification.objects.create(
            recipient=admin_group,
            message=f"New Document uploaded by: ['{instance.user.username} {instance.user.first_name} {instance.user.last_name}']"
        )
    else:
        # Existing Media File Updated -> Notify Admin
        if admin_group:

            Notification.objects.create(
                recipient=admin_group,
                #message=f"Document file ['{instance.title}]' was updated by: ['{instance.user.username} {instance.user.first_name} {instance.user.last_name}']"
                message=f"A Document file ['{instance.title}]' created by: ['{instance.user.username} {instance.user.first_name} {instance.user.last_name}'] was updated successfuly."
            )
        #elif not admin_group:
        #    Notification.objects.create(
        #        recipient=admin_group,
        #        message=f"Modified Document file ['{instance.title}]' was updated by: ['{admin_group.username} {admin_group.first_name} {admin_group.last_name}']"
        #    )

# Detect changes in the status field
@receiver(pre_save,sender=MediaFile)
def notify_status_change(sender,instance,**kwargs):
    if instance.pk: #Ensure its an existing object
        previous_instance = MediaFile.objects.get(pk=instance.pk)
        if previous_instance.status != instance.status:
            #Notify staff when status changes
            Notification.objects.create(
                recipient=instance.user,
                message=f"You Document File '{instance.title}' was {instance.status}"
            )