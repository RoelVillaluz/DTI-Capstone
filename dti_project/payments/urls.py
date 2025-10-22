from django.urls import path
from . import views

urlpatterns = [
    path("payment-page/<int:oop_id>/", views.payment_page, name="payment-page"),
    path("success/<int:oop_id>/", views.payment_success, name="payment-success"),
    path("failed/<int:oop_id>/", views.payment_failed, name="payment-failed"),
    path("download-receipt/<int:oop_id>/", views.download_receipt, name="download-receipt"),
]