from django.contrib import admin
from .models import CustomUser, LabsActive, Collaboration

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(LabsActive)
class LabsActiveAdmin(admin.ModelAdmin):
    list_display = ('lab_id', 'lab_name', 'started_by', 'start_time', 'allow_collab', 'verification_token') 
    list_filter = ('allow_collab',)
    search_fields = ('lab_name', 'lab_id', 'started_by__email', 'verification_token') 

@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('lab', 'collab_email', 'permission', 'accepted')  
    search_fields = ('collab_email', 'lab__lab_name')
    list_filter = ('permission', 'accepted') 
