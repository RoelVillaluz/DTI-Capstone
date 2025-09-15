from django.http import HttpResponseForbidden
from django.contrib import messages
from django.apps import apps
from django.shortcuts import redirect
from notifications.models import Notification
from ..models.base_models import DraftModel
from ..mixins.filter_mixins import FilterableDocumentMixin
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

MODEL_MAP = {
    model._meta.model_name: model
    for model in apps.get_models()
    if issubclass(model, DraftModel) and not model._meta.abstract
}

class ApproveDocumentsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.role == "business_owner":
            return HttpResponseForbidden("You are not allowed to approve documents.")

        document_ids = request.POST.getlist("documents")
        if not document_ids:
            messages.error(request, "No documents selected.")
            return redirect(request.META.get("HTTP_REFERER", "documents:all-documents"))

        updated_count = 0
        for doc in document_ids:
            try:
                model_name, pk = doc.split(":")
                model = MODEL_MAP.get(model_name.lower())
                if not model:
                    continue

                document = model.objects.filter(pk=pk).first()
                if document:
                    # Approve document
                    document.status = "approved"
                    document.save(update_fields=["status"])
                    updated_count += 1

                    # Create notification for document owner
                    notification = Notification.objects.create(
                        user=document.user, 
                        sender=request.user,
                        message=f"Your document '{document}' has been approved.",
                        type="approved",
                        content_type=ContentType.objects.get_for_model(document),
                        object_id=document.pk
                    )

                    # Send it to the web socket group
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"notifications_{document.user.id}",  # each user has their own group
                        {
                            'type': 'send_notification',
                            'message': notification.message,
                            'id': notification.id,
                            'type_name': notification.type
                        }
                    )

            except Exception as e:
                print("Error approving:", e)

        messages.success(request, f"{updated_count} document(s) approved successfully.")
        return redirect(request.META.get("HTTP_REFERER", "documents:all-documents"))