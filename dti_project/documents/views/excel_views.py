import datetime
from itertools import chain
from urllib.parse import quote
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.apps import apps
from ..models.base_models import DraftModel
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
from django.shortcuts import render
from django.db import transaction
import pandas as pd
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)

MODEL_MAP = {
    model._meta.model_name: model
    for model in apps.get_models()
    if issubclass(model, DraftModel) and not model._meta.abstract
}

EXPORT_MODEL_MAP = {
    "salespromotionpermitapplication": SalesPromotionPermitApplication,
    "personaldatasheet": PersonalDataSheet,
    "servicerepairaccreditationapplication": ServiceRepairAccreditationApplication,
    "inspectionvalidationreport": InspectionValidationReport,
    "orderofpayment": OrderOfPayment,
    "checklistevaluationsheet": ChecklistEvaluationSheet,
}

class ExportDocumentsExcelView(LoginRequiredMixin, View):
    """
    Export selected documents (via checkboxes) or all filtered documents to Excel.
    Preserves grouped formatting, headers, styling, and filename date ranges.
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        selected_docs = request.POST.getlist("documents")

        # --- Collect documents by model ---
        grouped = {}
        if selected_docs:
            # Use checkbox selection
            grouped_ids = {}
            for doc in selected_docs:
                try:
                    model_name, pk = doc.split(":")
                    grouped_ids.setdefault(model_name.lower(), []).append(pk)
                except ValueError:
                    continue

            for model_name, ids in grouped_ids.items():
                model = EXPORT_MODEL_MAP.get(model_name)
                if not model:
                    continue
                qs = UserRoleMixin.get_queryset_or_all(model, user).filter(pk__in=ids)
                if qs.exists():
                    grouped[model._meta.verbose_name_plural.title()] = list(qs)
        else:
            # If no checkboxes, export all (apply UserRoleMixin)
            for model in EXPORT_MODEL_MAP.values():
                qs = UserRoleMixin.get_queryset_or_all(model, user)
                if qs.exists():
                    grouped[model._meta.verbose_name_plural.title()] = list(qs)

        # --- Create workbook ---
        wb = Workbook()
        wb.remove(wb.active)

        for model_name, objs in grouped.items():
            if not objs:
                continue
            ws = wb.create_sheet(title=model_name[:31])
            fields = objs[0]._meta.fields
            headers = [f.verbose_name.title() for f in fields]
            ws.append(headers)

            # Style headers
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

            # Rows
            for obj in objs:
                row = []
                for f in fields:
                    val = getattr(obj, f.name, "")
                    if isinstance(val, datetime.datetime):
                        val = val.date()
                    if val is None:
                        val = ""
                    row.append(to_title(str(val)))
                ws.append(row)

            # Auto-size columns
            for col_num, col_cells in enumerate(ws.columns, 1):
                max_length = 0
                column = get_column_letter(col_num)
                for cell in col_cells:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column].width = min(max_length + 2, 50)

            # Freeze header
            ws.freeze_panes = "A2"

        # --- Filename with date range ---
        dates = []
        for objs in grouped.values():
            for doc in objs:
                d = getattr(doc, "date_filed", None) or getattr(doc, "date", None)
                if d:
                    if isinstance(d, datetime.datetime):
                        d = d.date()
                    dates.append(d)
        min_date, max_date = (min(dates), max(dates)) if dates else (None, None)
        date_part = f"{min_date}_{max_date}" if min_date and max_date else ""

        filename = f"Documents_{date_part}.xlsx" if date_part else "Documents.xlsx"

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        safe_filename = quote(filename)
        response["Content-Disposition"] = f"attachment; filename={safe_filename}; filename*=UTF-8''{safe_filename}"
        wb.save(response)
        return response

def to_title(value):
    """Normalize strings: remove underscores, title-case, handle non-strings gracefully."""
    if not isinstance(value, str):
        return value
    return value.replace("_", " ").title()

class UploadExcelView(LoginRequiredMixin, View):
    """
    Upload an Excel file and import rows into a model.
    """
    template_name = "documents/excel_templates/excel_upload.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return render(request, self.template_name, {"error": "Please choose a file."})

        try:
            df = pd.read_excel(excel_file)  # or pd.read_csv for CSV
        except Exception as e:
            return render(request, self.template_name, {"error": f"Could not read file: {e}"})

        # Example: import into ChecklistEvaluationSheet model
        imported = 0
        from ..models import ChecklistEvaluationSheet  # import your model here

        # Wrap in transaction for speed and rollback safety
        with transaction.atomic():
            for _, row in df.iterrows():
                # Map Excel columns to model fields. Example:
                ChecklistEvaluationSheet.objects.create(
                    # field_name_in_model = row['ColumnNameInExcel'],
                    # fill out according to your sheet’s columns:
                    name=row.get("Name", ""),
                    description=row.get("Description", ""),
                    # … other fields …
                )
                imported += 1

        return render(
            request,
            self.template_name,
            {"success": f"Successfully imported {imported} records."},
        )
