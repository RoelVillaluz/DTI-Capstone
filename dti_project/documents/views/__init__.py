from .create_views import (
    CreateSalesPromotionView,
    CreatePersonalDataSheetView,
    CreateServiceRepairAccreditationApplicationView,
    CreateInspectionValidationReportView,
    CreateOrderOfPaymentView,
    CreateChecklistEvaluationSheetView
)
from .detail_views import (
    SalesPromotionDetailView,
    PersonalDataSheetDetailView,
    ServiceRepairAccreditationApplicationDetailView,
    InspectionValidationReportDetailView,
    OrderOfPaymentDetailView,
    ChecklistEvaluationSheetDetailView
)

from .update_views import (
    UpdateSalesPromotionView,
    UpdatePersonalDataSheetView,
    UpdateServiceRepairAccreditationApplicationView,
    UpdateInspectionValidationReportView,
    UpdateOrderOfPaymentView,
    UpdateChecklistEvaluationSheetView
)

from .list_views import (
    AllDocumentListView,
    SalesPromotionListView,
    PersonalDataSheetListView,
    ServiceRepairAccreditationApplicationListView,
    InspectionValidationReportListView,
    OrderOfPaymentListView,
    ChecklistEvaluationSheetListView,
)

from .excel_views import (
    UploadExcelView,
    ExportDocumentsExcelView
)

from .action_views import (
    ApproveDocumentsView
)