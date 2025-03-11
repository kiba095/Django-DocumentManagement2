from django.contrib import admin,messages
from .models import MediaFile,Notification
from django.http import HttpRequest
from django.utils.html import format_html
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse,path
from django.contrib.admin.sites import site
from django.template.response import TemplateResponse
from django.templatetags.static import static
from .forms import FormSubmissionForm
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
import mimetypes

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient','message','created_at','is_read')

    def get_model_perms(self, request):
        ''' Hide the NotificationModel in the django-admin'''
        return {}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        #if request.user.groups.filter(name="admin_group").first():
        if request.user.is_superuser:
            return qs
        return qs.filter(recipient=request.user)
    
    def changelist_view(self, request, extra_context=None):
        # Show notifications as Django admin messages
        notifications = Notification.objects.filter(recipient=request.user,is_read=False)

        if notifications.exists():
            for note in notifications:
                '''display green or red obx if the file is approved/rejected'''
                if "rejected" in note.message:
                    messages.error(request,note.message)
                else:
                    messages.info(request,note.message)
                note.is_read = True
                note.save()

        return super().changelist_view(request,extra_context)
    
class MediaFileAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    actions = ['approve_files','reject_files']
    ordering = ('-uploaded_at',)



    fieldsets = [
        ("Section title", {
            "classes": ("collapse", "expanded"),
            "fields": ("title","remarks"),
        }),
    ]

    

    def get_queryset(self,request):
        ''' Show records for respective user only except admin'''
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="admin_group").exists() or request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    @admin.display(description="Last Updated",ordering="uploaded_at")
    def custom_link_modified_at(self,obj):
        return obj.uploaded_at
    
    @admin.display(description="Is Approved")
    def custom_link_is_approved(self,obj):
        if obj.status == 'approved':
            icon_url = static('admin/img/icon-yes.svg')
            return format_html(f'<img src={icon_url} alt="Active" title="{obj.remarks}">')
        elif obj.status == 'rejected':
            icon_url = static('admin/img/icon-no.svg')
            return format_html(f'<img src={icon_url} alt="Active" title="{obj.remarks}">')
        
    @admin.display(description="Committee Group")
    def custom_link_com_group(self,obj):
        return obj.user
    
    @admin.display(description="Content Title")
    def custom_link_title(self,obj):
        return obj.title
    
    @admin.display(description="Format")
    def custom_link_media_type(self,obj):
        return obj.media_type

    def get_list_display_links(self,request,list_display):
        if request.user.groups.filter(name="admin_group").exists() or request.user.is_superuser:
            return ('',) 
        else:
            return('custom_link_title',)   

    def get_list_display(self,request):
        default_fields = ('custom_link_title','custom_link_com_group','custom_link_media_type','custom_link_is_approved','custom_link_modified_at',)
        specific_fields_admin = ('custom_decide_page_link',)
        specific_fields_user = ('custom_view_page_link',)

        if request.user.groups.filter(name="admin_group").exists() or request.user.is_superuser:
            return default_fields + specific_fields_admin
        return default_fields + specific_fields_user


    def get_actions(self, request):
        actions = super().get_actions(request)
        #remove actions if the group is com_group
        if request.user.groups.filter(name="com_group").exists():
            actions.pop('approve_files',None)
            actions.pop('reject_files',None)
        return actions

    def approve_files(self,request,queryset):
        queryset.update(status='approved')
        for media in queryset:
            messages.success(request,f"Approved: '{media.title}'") 
            #Notify staff when status changes
            Notification.objects.create(
                recipient=media.user,
                message=f"You Document File '{media.title}' was {media.status}"
            )   
        

    def reject_files(self,request,queryset):
        queryset.update(status='rejected')
        for media in queryset:
            messages.error(request,f"Rejected: '{media.title}'")
            #Notify staff when status changes
            Notification.objects.create(
                recipient=media.user,
                message=f"You Document File '{media.title}' was {media.status}"
            )     

    approve_files.short_description = "Approve selected media files"
    reject_files.short_description = "Reject selected media files"

    def get_readonly_fields(self, request, obj =None):
        if not request.user.groups.filter(name="admin_group").first() and not request.user.is_superuser:
            return ["status","user","remarks","media_type",]
        return []
    
    def get_exclude(self,request,obj=...):
        ''' Hide for non-superusers '''
        if not request.user.groups.filter(name="admin_group").exists() or not request.user.is_superuser:
            return('user',)
        return super().get_exclude(request,obj)
    
    def save_model(self,request:HttpRequest,obj,form,change):
        ''' Automatically set the logged-in users username/foreignkey before saving'''
        
        if not request.user.groups.filter(name="admin_group").exists() or request.user.is_superuser:
            if obj.status != 'pending':
                obj.status = 'pending'
            if not obj.user:
                obj.user = request.user

        ''' Automatically detect what file-type is uploaded '''
        uploaded_file = obj.file.url
        if uploaded_file:
            # Detect file type
            file_type = self.detect_file_type(uploaded_file)
            obj.media_type = file_type # Save the file type to a field named media_type

        super().save_model(request,obj,form,change)

    def detect_file_type(self,uploaded_file):
        # Get the file's MIME type
        mime_type,_ = mimetypes.guess_type(uploaded_file)

        if mime_type:
            if mime_type.startswith('image'):
                return 'image'
            elif mime_type == 'application/pdf':
                return 'pdf'
            else:
                return 'unknown'
        else:
            #Fallback to file extension if MIME type is not detected
            file_extension = uploaded_file.split('.')[-1].lower()
            if file_extension in ['jpg','jpeg','png','gif','bmp','webp']:
                return 'image'
            elif file_extension == 'pdf':
                return 'pdf'
            else:
                return 'unknown'
        

    
    # custom_admin_view for comittee
    def custom_view_page_link(self,obj):
        url = reverse("admin:view_page",args=[obj.id])

        if obj.status == 'pending':
            return format_html('<a href="{}" class="button" id="btn-save-continue" target="_blank">Pending</a>',url)
        else:
            return format_html('<a href="{}" class="button" id="btn-save-add-another" target="_blank">Display</a>',url)

    custom_view_page_link.short_description = "Options"

    # custom_admin_view for principal
    def custom_decide_page_link(self,obj):
        url = reverse("admin:decide_page",args=[obj.id])
        if obj.status == 'pending':
            return format_html('<a href="{}" class="button" id="btn-save-continue" target="_blank">Pending</a>',url)
        elif obj.status == 'approved':
            return format_html('<a href="{}" class="button" id="btn-save" target="_blank">ReAccess</a>',url)
        else:
            return format_html('<a href="{}" class="button" id="btn-delete" target="_blank">ReAccess</a>',url)

    custom_decide_page_link.short_description = "Options"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('decide-page/<int:obj_id>/',custom_decide_page,name="decide_page"),
            path('view-page/<int:obj_id>/',custom_view_page,name="view_page"),
        ]
        return custom_urls + urls
    

## MAKES custompage view forms inside the buildin admin dashboard
def custom_decide_page(request,obj_id):
    media = MediaFile.objects.filter(id=obj_id).first()
    
    if not request.user.is_active or not request.user.is_staff:
        return admin.site.login(request)

    ####################################################################    
    if request.method == 'POST':
        remarks = request.POST.get('remarks','')
        status = request.POST.get('status',)
        action = request.POST.get('action',)

        if media:
            media.remarks = remarks
            media.status = status
            if action in ['approved','rejected']: #only update status if action is valid
                media.status = 'approved' if action == 'approved' else 'rejected'

                if media.status == 'approved':
                    messages.success(request,"The Document: [{0}] has been approved successfully.".format(media.title))
                    action = 'approved'
                else:
                    messages.error(request,"The Document: [{0}] has been rejected.".format(media.title))
                    action = 'rejected'
        else:
            media = FormSubmissionForm(
                remarks = remarks,
                status = 'pending',
            )
        media.save()
        return redirect(reverse("admin:app_mediafile_changelist"))
        #################################################################

    media = get_object_or_404(MediaFile,id=obj_id)
    context = {
        **site.each_context(request),
        'media':media,
    }
    return render(request,'admin/decide_page.html',context)

def custom_view_page(request,obj_id):
    if not request.user.is_active  or not request.user.is_staff:
        return admin.site.login(request)
    
    media = get_object_or_404(MediaFile,id=obj_id)
    context = {
        **site.each_context(request),
        'media':media,
    }
    return render(request,'admin/view_page.html',context)

admin.site.register(Notification,NotificationAdmin)
admin.site.register(MediaFile,MediaFileAdmin)