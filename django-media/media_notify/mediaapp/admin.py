from django.contrib import admin,messages
from .models import MediaFile,Notification
from django.http import HttpRequest
from django.utils.html import format_html


#admin.site.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient','message','created_at','is_read')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.groups.filter(name="admin_group").first() or request.user.is_superuser:
            return qs
        return qs.filter(recipient=request.user)

    
    def changelist_view(self,request,extra_context=None):
        # Show notifications as Django admin messages
        notifications = Notification.objects.filter(recipient=request.user,is_read=False)
        if notifications.exists():
            for note in notifications:
                '''display green or red box if the file is approve/rejected'''
                if "rejected" in note.message:
                    messages.error(request,note.message)
                else:
                    messages.info(request,note.message)
                
                note.is_read = True
                note.save()
        return super().changelist_view(request,extra_context)


class MediaFileAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    #actions = ['approve_files','reject_files']

    def get_list_display(self, request):
        default_fields = ('title','user','status','uploaded_at',)
        group_specific_fields = ('show_document',)

        if request.user.groups.filter(name="admin_group").exists():
            return default_fields + group_specific_fields
        return default_fields


    def approve_files(self,request,queryset):
        queryset.update(status='approved')
        for media in queryset:
            messages.success(request,f"Approved: {media.file.name}")

    def reject_files(self,request,queryset):
        queryset.update(status='rejected')
        for media in queryset:
            messages.error(request,f"Rejected: {media.file.name}")

    def get_readonly_fields(self,request,obj=None):
        if not request.user.groups.filter(name="admin_group").exists() or not request.user.is_superuser:
        #if not request.user.is_superuser:
            return ["status","remarks","user",]
        return []
 
    def get_exclude(self,request,obj=...):
        '''Hide for non-superusers'''
        if not request.user.groups.filter(name="admin_group").exists() or not request.user.is_superuser:
        #if not request.user.is_superuser:
            return ('user',)
        return super().get_exclude(request,obj)
    
    
    def save_model(self,request:HttpRequest,obj,form,change):
        '''Automatically set the logged-in users username/foreighnkey before saving'''
        if not request.user.groups.filter(name="admin_group").exists() or not request.user.is_superuser:
            if obj.status != 'pending':
                obj.status = 'pending'
        if not obj.user:
            obj.user = request.user
        super().save_model(request,obj,form,change)

    def get_queryset(self,request):
        '''Show records for respective user only except admin'''
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="admin_group").exists() or request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def show_document(self,obj):
        '''show a detail of the media that is picked'''
        return format_html('''<a href="#" onClick="window.open('http://localhost:8000/mediaapp/{0}/detail','_blank')">DISPLAY DOCUMENT</a>'''.format(obj.id))

    approve_files.short_description = "Approve selected media files"
    reject_files.short_description = "Reject selected media files"

#admin.site.site_header = "My Custom Admin Header"
#admin.site.site_header = "My Custom Admin Header"
#admin.site.index_title = "Welcome to my Custom Admin"

admin.site.register(Notification,NotificationAdmin)
admin.site.register(MediaFile,MediaFileAdmin)


