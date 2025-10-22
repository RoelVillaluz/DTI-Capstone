from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.utils import send_user_notification
import requests
import base64
import datetime
from io import BytesIO
from users.models import User
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from documents.models import SalesPromotionPermitApplication, OrderOfPayment

def payment_page(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    sppa = oop.sales_promotion_permit_application

    total_amount = oop.total_amount or oop.calculate_total()
    
    # Display data
    context = {
        "oop": oop,
        "business_name": sppa.sponsor_name,
        "scope": sppa.coverage,
        "registration_type": "Sales Promotion Permit",
        "transaction_type": "Application",
        "applicant_name": sppa.sponsor_authorized_rep,
        "citizenship": "Filipino",
        "processing_fee": total_amount - oop.doc_stamp_amount,
        "doc_stamp_fee": oop.doc_stamp_amount,
        "total_amount": total_amount,
    }

    # When user proceeds to pay via GCash
    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")

    # Payment handling
    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")

        if payment_method == "gcash":
            key = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {key}",
            }

            data = {
                "data": {
                    "attributes": {
                        "amount": int(total_amount * 100),  # centavos
                        "currency": "PHP",
                        "type": "gcash",
                        "redirect": {
                            "success": request.build_absolute_uri(f"/payments/success/{oop.id}/"),
                            "failed": request.build_absolute_uri(f"/payments/failed/{oop.id}/"),
                        }
                    }
                }
            }

            response = requests.post("https://api.paymongo.com/v1/sources", headers=headers, json=data)
            result = response.json()

            if "data" in result:
                checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
                return redirect(checkout_url)
            else:
                messages.error(request, "Failed to initialize GCash payment. Please try again.")

    return render(request, "payments/payment-page.html", context)

def payment_success(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
        oop.payment_status = OrderOfPayment.PaymentStatus.PAID
        oop.save()
    # Notify admin/collection agent
    from users.models import User
    admins = User.objects.filter(role__in=["admin", "collection_agent"])

    for admin in admins:
        notification = Notification.objects.create(
            user=admin,
            sender=request.user,
            message=f"{request.user.get_full_name()} has successfully paid for OOP #{oop.pk}.",
            type="info",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(admin.id, notification)

    # Notify business owner
        notification = Notification.objects.create(
            user=oop.sales_promotion_permit_application.user,
            sender=request.user,
            message=f"Your payment for OOP #{oop.pk} was successful and is now pending verification.",
            type="info",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(oop.sales_promotion_permit_application.user.id, notification)

    return render(request, "payments/payment_success.html", {"oop": oop})


def payment_failed(request):
    messages.error(request, "Payment failed or was canceled. Please try again.")
    return render(request, "payments/payment_failed.html")

@login_required
def verify_payment(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    if request.user.role not in ["admin", "collection_agent"]:
        messages.error(request, "You do not have permission to verify payments.")
        return redirect('documents-list')

    if oop.payment_status == OrderOfPayment.PaymentStatus.PAID:
        # Just update status
        oop.payment_status = OrderOfPayment.PaymentStatus.VERIFIED
        oop.save()

        # Notify business owner
        notification = Notification.objects.create(
            user=oop.sales_promotion_permit_application.user,
            sender=request.user,
            message=f"Your payment for OOP #{oop.pk} has been verified! You can now download your official receipt.",
            type="approved",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(oop.sales_promotion_permit_application.user.id, notification)

    else:
        messages.warning(request, "Payment must be marked as 'Paid' before verifying.")
        return redirect('documents-list')

@login_required
def download_receipt(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    # Only allow download if already verified
    if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
        messages.warning(request, "Receipt is only available after verification.")
        return redirect('documents-list')

    # Generate PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 800, "DTI Official Receipt")
    p.setFont("Helvetica", 10)
    p.drawString(50, 780, f"Reference Code: {oop.pk:06d}")
    p.drawString(50, 765, f"Issue Date: {datetime.datetime.now().strftime('%d %b %Y %I:%M %p')}")
    p.drawString(50, 750, f"Application Name: {oop.sales_promotion_permit_application.sponsor_name}")
    p.drawString(50, 735, f"Particulars: Sales Promotion Permit Application")
    p.drawString(50, 720, f"Total Amount: Php {oop.total_amount or 0:,.2f}")
    p.drawString(50, 705, f"Application Fee: Php {(oop.total_amount or 0) - (oop.doc_stamp_amount or 0):,.2f}")
    p.drawString(50, 690, f"Documentary Stamp Tax: Php {oop.doc_stamp_amount or 0:,.2f}")
    p.drawString(50, 670, f"Verified By: {request.user.get_full_name()}")

    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 640, "This is your official DTI receipt.")
    p.drawString(50, 625, "Your transaction has been verified successfully.")

    p.showPage()
    p.save()
    buffer.seek(0)
    
    admins = User.objects.filter(role__in=["admin", "collection_agent"])
    for admin in admins:
        notification = Notification.objects.create(
            user=admin,
            sender=request.user,
            message=f"{request.user.get_full_name()} downloaded the receipt for OOP #{oop.pk}.",
            type="info",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(admin.id, notification)


    return FileResponse(buffer, as_attachment=True, filename=f"DTI_Receipt_{oop.pk}.pdf")

