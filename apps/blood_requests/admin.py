from django import forms
from django.contrib import admin
from apps.notifications.services import notify
from .models import BloodRequest, DonorResponse, RequestAttachment
class RequestAdminForm(forms.ModelForm):
    verification_status = forms.ChoiceField(choices=[('pending','Pending'),('verified','Verified'),('rejected','Rejected')])
    status = forms.ChoiceField(choices=[('open','Open'),('in_progress','In progress'),('fulfilled','Fulfilled'),('cancelled','Cancelled')])
    class Meta:
        model = BloodRequest
        fields = '__all__'
    def clean_status(self):
        status = self.cleaned_data['status']
        old = BloodRequest.objects.filter(pk=self.instance.pk).first()
        if old and old.status in ('fulfilled','cancelled') and old.status != status:
            raise forms.ValidationError('Closed requests cannot be reopened.')
        return status
@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    list_display = ('id','patient_name','required_blood_type','requester','urgency','verification_status','status')
    list_filter = ('verification_status','status','urgency')
    search_fields = ('patient_name','requester__username','location')
    readonly_fields = ('requester','facility','required_blood_type','patient_name','units_needed','urgency','needed_date','location','location_display','created_at')
    fields=('requester','facility','required_blood_type','patient_name','units_needed','urgency','needed_date','location_display','verification_status','status','created_at')
    def location_display(self,obj):
        from apps.shared.locations import display_location
        return display_location(obj.location)
    def has_add_permission(self,request):
        return False
    def save_model(self,request,obj,form,change):
        super().save_model(request,obj,form,change)
        if change and any(x in form.changed_data for x in ('status','verification_status')):
            notify(obj.requester,obj,'request_review','Request review updated',f'Request #{obj.pk}: verification {obj.verification_status}; status {obj.status}.')
            for response in obj.donor_responses.select_related('donor_user'):
                notify(response.donor_user,obj,'request_status','Blood request updated',f'Request #{obj.pk}: verification {obj.verification_status}; status {obj.status}.')
class AttachmentAdminForm(forms.ModelForm):
    verification_status = forms.ChoiceField(choices=[('pending','Pending'),('verified','Verified'),('rejected','Rejected')])
    class Meta:
        model = RequestAttachment
        fields = '__all__'
@admin.register(RequestAttachment)
class AttachmentAdmin(admin.ModelAdmin):
    form = AttachmentAdminForm
    list_display = ('id','blood_request','document_type','verification_status','created_at')
    list_filter = ('verification_status','document_type')
    readonly_fields = ('blood_request','uploaded_by_user','document_type','file_url','created_at','download_document')
    def download_document(self,obj):
        from django.urls import reverse
        from django.utils.html import format_html
        return format_html('<a href="{}">Download private document</a>',reverse('blood_requests:download',args=[obj.pk]))
    def has_add_permission(self,request):
        return False
@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display = ('blood_request','donor_user','response_status','responded_at')
    list_filter = ('response_status',)
    def has_add_permission(self,request):
        return False
    def has_change_permission(self,request,obj=None):
        return False
