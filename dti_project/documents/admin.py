from django.contrib import admin
from .utils.admin_helpers import get_full_name_from_personal_data
from .models import CollectionReport, CollectionReportItem, CharacterReference, ChecklistEvaluationSheet, EducationalAttainment, EmployeeBackground, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, ProductCovered, SalesPromotionPermitApplication, Service, ServiceCategory, ServiceRepairAccreditationApplication, TrainingsAttended, ChangeRequest


# Register your models here.
# 🔹 Base admin for models inheriting DraftModel
class StatusModelAdmin(admin.ModelAdmin):
    """Base admin that adds status to list_display and list_filter dynamically."""

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if "status" not in list_display:
            return list_display + ("status",)
        return list_display

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if "status" not in list_filter:
            return list_filter + ("status",)
        return list_filter


# 🔹 Admin registrations
@admin.register(CollectionReport)
class CollectionReportAdmin(admin.ModelAdmin):
    list_display = ('date_range_display',)

    def date_range_display(self, obj):
        dates = obj.report_items.values_list('date', flat=True)
        if not dates:
            return "No dates"

        first_date = min(dates)
        last_date = max(dates)

        if first_date == last_date:
            return first_date.strftime("%b %d, %Y")
        else:
            return f"{first_date.strftime('%b %d, %Y')} - {last_date.strftime('%b %d, %Y')}"

    date_range_display.short_description = "Date Range"

    # Override delete for single object
    def delete_model(self, request, obj):
        # Delete all related report items first
        obj.report_items.all().delete()
        super().delete_model(request, obj)

    # Override delete for bulk delete (queryset)
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.report_items.all().delete()
        super().delete_queryset(request, queryset)


@admin.register(CollectionReportItem)
class CollectionReportItemAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "number",
        "payor",
        "particulars",
        "amount",
        "stamp_tax",
    )
    search_fields = (
        "number",
        "payor",
        "rc_code",
        "particulars",
    )
    list_filter = ("date", "particulars")
    ordering = ["-date"]

@admin.register(SalesPromotionPermitApplication)
class SalesPromotionAdmin(StatusModelAdmin):
    list_display = ("promo_title", "payment_status_for_owner")
    search_fields = ("promo_title", "sponsor_name", "advertising_agency_name")
    
    def payment_status_for_owner(self, obj):
        oop = getattr(obj, 'order_of_payment', None)
        if oop and oop.payment_status in ["paid", "verified"]:
            # Show "Paid" to business owner, even if verified
            return "Paid"
        return ""  # Or "Not Paid" if you prefer
    
    payment_status_for_owner.short_description = "Payment Status"

@admin.register(ProductCovered)
class ProductCoveredAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = ("name", "permit_application_title")
    search_fields = ("name", "permit_application__promo_title")

    def permit_application_title(self, obj):
        return obj.permit_application.promo_title
    permit_application_title.short_description = "Promo Title"


@admin.register(PersonalDataSheet)
class PersonalDataSheetAdmin(StatusModelAdmin):
    list_display = ("last_name", "first_name", "email_address", "sex")
    search_fields = ("last_name", "first_name", "email_address")
    list_filter = ("sex", "civil_status")


@admin.register(EmployeeBackground)
class EmployeeBackgroundAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = (
        get_full_name_from_personal_data,
        "employer",
        "position",
        "start_date",
        "end_date",
    )
    search_fields = ("employer", "position")


@admin.register(TrainingsAttended)
class TrainingsAttendedAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = (get_full_name_from_personal_data, "training_course", "conducted_by")
    search_fields = ("training_course", "conducted_by")


@admin.register(EducationalAttainment)
class EducationalAttainmentAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = (get_full_name_from_personal_data, "school", "course")
    search_fields = ("school", "course")


@admin.register(CharacterReference)
class CharacterReferencesAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = ("name", "company", "email", "contact_number")
    search_fields = ("name", "company")


@admin.register(ServiceRepairAccreditationApplication)
class ServiceRepairAccreditationApplicationAdmin(StatusModelAdmin):
    list_display = (
        "name_of_business",
        "full_name",
        "application_type",
        "category",
        "star_rating",
    )
    search_fields = ("name_of_business", "first_name", "last_name")
    list_filter = (
        "application_type",
        "category",
        "star_rating",
        "social_classification",
        "asset_size",
        "form_of_organization",
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()

    full_name.short_description = "Full Name"


@admin.register(OrderOfPayment)
class OrderOfPaymentAdmin(StatusModelAdmin):
    list_display = (
        "id",
        "sales_promotion_permit_application",
        "total_amount",
        "payment_status",
        "status",
        "date",
    )
    list_filter = ("payment_status", "status", "date")
    search_fields = ("sales_promotion_permit_application__sponsor_name",)
    ordering = ("-date",)

    # Makes Save buttons appear both at top and bottom
    save_on_top = True


@admin.register(InspectionValidationReport)
class InspectionValidationReportAdmin(StatusModelAdmin):
    list_display = ("name_of_business", "type_of_application_activity", "date")
    search_fields = ("name_of_business", "address")
    list_filter = ("type_of_application_activity", "date")
    date_hierarchy = "date"
    ordering = ["-date"]


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = ("key", "name")
    search_fields = ("key", "name")
    ordering = ["key"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):  # Not DraftModel
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ["category", "name"]


@admin.register(ChecklistEvaluationSheet)
class ChecklistEvaluationSheetAdmin(StatusModelAdmin):
    list_display = ("name_of_business", "type_of_application", "renewal_due_date", "star_rating")
    list_filter = ("type_of_application", "star_rating")
    search_fields = ("name_of_business",)

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'approved_by', 'date')
    list_filter = ('is_approved', )
    search_fields = ('user', 'approved_by')