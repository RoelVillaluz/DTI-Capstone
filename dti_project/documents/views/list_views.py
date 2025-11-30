import datetime
from django.views.generic import ListView
from ..mixins.filter_mixins import FilterCollectionReportListMixin, FilterableDocumentMixin
from ..mixins.counter_mixins import DocumentCountMixin
from ..mixins.permissions_mixins import RoleFormPageRestrictionMixin, UserRoleMixin
from ..mixins.sort_mixins import SortCollectionReportListMixin, SortMixin  
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
    CollectionReport
)
from itertools import chain

def get_date_field(obj):
    """Return the date field (date_filed or date) for any document."""
    return getattr(obj, "date_filed", None) or getattr(obj, "date", None) or datetime.date.min


class BaseDocumentListView(UserRoleMixin, DocumentCountMixin, FilterableDocumentMixin, SortMixin, ListView):
    """
    Generic list view for document models.
    Just set `model`, `template_name`, `context_object_name`, and `active_doc_type`.
    """
    active_doc_type = None  # override in subclasses

    def get_queryset(self):
        user = self.request.user
        qs = self.get_queryset_or_all(self.model, user)
        qs = self.apply_filters(qs)
        # Apply sorting instead of hardcoded date sort
        return self.apply_sorting(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.get_queryset()
        context["active_doc_type"] = self.active_doc_type
        return context


class AllDocumentListView(UserRoleMixin, DocumentCountMixin, FilterableDocumentMixin, SortMixin, ListView):
    template_name = "documents/list_templates/all_documents_list.html"
    context_object_name = "documents"

    def get_queryset(self):
        user = self.request.user

        sales_promos = self.get_queryset_or_all(SalesPromotionPermitApplication, user)
        personal_data_sheets = self.get_queryset_or_all(PersonalDataSheet, user)
        service_accreditations = self.get_queryset_or_all(ServiceRepairAccreditationApplication, user)
        inspection_reports = self.get_queryset_or_all(InspectionValidationReport, user)
        orders_of_payment = self.get_queryset_or_all(OrderOfPayment, user)
        checklist_evaluation_sheets = self.get_queryset_or_all(ChecklistEvaluationSheet, user)

        # Apply filters per queryset
        combined = chain(
            self.apply_filters(sales_promos),
            self.apply_filters(personal_data_sheets),
            self.apply_filters(service_accreditations),
            self.apply_filters(inspection_reports),
            self.apply_filters(orders_of_payment),
            self.apply_filters(checklist_evaluation_sheets),
        )

        # Apply sorting to the combined documents
        documents = self.apply_sorting(combined)
        return documents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update({
            "sales_promos": self.apply_filters(self.get_queryset_or_all(SalesPromotionPermitApplication, user)),
            "personal_data_sheets": self.apply_filters(self.get_queryset_or_all(PersonalDataSheet, user)),
            "service_accreditations": self.apply_filters(self.get_queryset_or_all(ServiceRepairAccreditationApplication, user)),
            "inspection_reports": self.apply_filters(self.get_queryset_or_all(InspectionValidationReport, user)),
            "orders_of_payment": self.apply_filters(self.get_queryset_or_all(OrderOfPayment, user)),
            "checklist_evaluation_sheets": self.apply_filters(self.get_queryset_or_all(ChecklistEvaluationSheet, user)),
            "documents": self.get_queryset(),
        })

        return context


class SalesPromotionListView(BaseDocumentListView):
    model = SalesPromotionPermitApplication
    template_name = "documents/list_templates/sales_promotion_list.html"
    context_object_name = "sales_promos"
    active_doc_type = "sales_promos"


class PersonalDataSheetListView(BaseDocumentListView):
    model = PersonalDataSheet
    template_name = "documents/list_templates/personal_data_sheet_list.html"
    context_object_name = "personal_data_sheets"
    active_doc_type = "personal_data_sheets"


class ServiceRepairAccreditationApplicationListView(BaseDocumentListView):
    model = ServiceRepairAccreditationApplication
    template_name = "documents/list_templates/service_repair_list.html"
    context_object_name = "service_accreditations"
    active_doc_type = "service_accreditations"


class InspectionValidationReportListView(BaseDocumentListView):
    model = InspectionValidationReport
    template_name = "documents/list_templates/inspection_validation_report_list.html"
    context_object_name = "inspection_reports"
    active_doc_type = "inspection_reports"


class OrderOfPaymentListView(BaseDocumentListView):
    model = OrderOfPayment
    template_name = "documents/list_templates/order_of_payment_list.html"
    context_object_name = "orders_of_payment"
    active_doc_type = "orders_of_payment"


class ChecklistEvaluationSheetListView(BaseDocumentListView):
    model = ChecklistEvaluationSheet
    template_name = "documents/list_templates/checklist_evaluation_list.html"
    context_object_name = "checklist_evaluation_sheets"
    active_doc_type = "checklist_evaluation_sheets"
    
class CollectionReportListView(
    RoleFormPageRestrictionMixin,
    FilterCollectionReportListMixin,
    SortCollectionReportListMixin,
    ListView
):
    model = CollectionReport
    template_name = "documents/collection_reports/collection_report_list.html"
    context_object_name = "collection_reports"
    active_doc_type = "collection_reports"
    allowed_roles = ["collection_agent", "alt_collection_agent", "admin"]

    def get_queryset(self):
        # Start with base queryset (possibly restricted by RoleFormPageRestrictionMixin)
        qs = super().get_queryset()

        # Apply filters from your mixin
        qs = self.apply_filters(qs)

        # Apply sorting from SortCollectionReportListMixin (if defined)
        if hasattr(self, "apply_sorting"):
            qs = self.apply_sorting(qs)

        return qs
