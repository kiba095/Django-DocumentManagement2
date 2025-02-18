from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Notification,MediaFile
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect
from django.urls import reverse



@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user,is_read=False)
    return render(request,'notifications.html',{'notifications':user_notifications})

@login_required
def media_detail(request,detail_id):
    media_files = MediaFile.objects.filter(id=detail_id).first()

    return render(request,'mediaapp/media_detail.html',{'media' : media_files})

# for the approver button 
def is_approver(user):
    return user.groups.filter(name="admin_group").exists()

@login_required
@user_passes_test(is_approver)
def approve_document(request,doc_id):
    document = get_object_or_404(MediaFile,id=doc_id)
    document.status = 'approved'
    document.save()
    messages.success(request,"The Document has been approved successfully.")
    return redirect(reverse("admin:mediaapp_mediafile_changelist"))

@login_required
@user_passes_test(is_approver)
def reject_document(request,doc_id):
    document = get_object_or_404(MediaFile,id=doc_id)
    document.status = 'rejected'
    document.save()
    messages.error(request,"The Document has been rejected.")
    return redirect(reverse("admin:mediaapp_mediafile_changelist"))