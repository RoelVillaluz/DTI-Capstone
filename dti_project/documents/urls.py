from django.urls import path
from documents import views 

urlpatterns = [
    # CREATE VIEWS
    path("create/sales-promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
    path("create/personal-data-sheet", views.CreatePersonalDataSheetView.as_view(), name="create-personal-data-sheet"),
    path("create/service-repair-accreditation", views.CreateServiceRepairAccreditationApplicationView.as_view(), name="create-service-repair-accreditation"),
    path("create/inspection-validation-report", views.CreateInspectionValidationReportView.as_view(), name="create-inspection-validation-report"),
    path('create/order-of-payment', views.CreateOrderOfPaymentView.as_view(), name="create-order-of-payment"),
    path('create/checklist-evaluation', views.CreateChecklistEvaluationSheetView.as_view(), name='create-checklist-evaluation-sheet'),

    # DETAIL VIEWS
    path("sales-promotion-applications/<int:pk>", views.SalesPromotionDetailView.as_view(), name="sales-promotion-application"),
    path("personal-data-sheets/<int:pk>", views.PersonalDataSheetDetailView.as_view(), name="personal-data-sheet"),
    path('service-repair-accreditations/<int:pk>', views.ServiceRepairAccreditationApplicationDetailView.as_view(), name='service-repair-accreditation'),
    path("inspection-validation-reports/<int:pk>", views.InspectionValidationReportDetailView.as_view(), name="inspection-validation-report"),
    path("order-of-payments/<int:pk>", views.OrderOfPaymentDetailView.as_view(), name="order-of-payment"),
    path("checklist-evaluation-sheets/<int:pk>", views.ChecklistEvaluationSheetDetailView.as_view(), name='checklist-evaluation-sheet'),

    # UPDATE VIEWS
    path("sales-promotion-applications/<int:pk>/update", views.UpdateSalesPromotionView.as_view(), name='update-sales-promotion'),
    path("personal-data-sheets/<int:pk>/update", views.UpdatePersonalDataSheetView.as_view(), name='update-personal-data-sheet'),
    path("service-repair-accreditations/<int:pk>/update", views.UpdateServiceRepairAccreditationApplicationView.as_view(), name='update-service-repair-accreditation'),
    path("inspection-validation-reports/<int:pk>/update", views.UpdateInspectionValidationReportView.as_view(), name="update-inspection-validation-report"),
    path("orders-of-payment/<int:pk>/update", views.UpdateOrderOfPaymentView.as_view(), name="update-order-of-payment"),
    path("checklist-evaluation-sheets/<int:pk>/update", views.UpdateChecklistEvaluationSheetView.as_view(), name='update-checklist-evaluation-sheet'),

    # LIST VIEWS
    path("all-documents", views.AllDocumentListView.as_view(), name='all-documents'),
    path("sales-promotion-permit-applications", views.SalesPromotionListView.as_view(), name='sales-promotion-list'),
    path("personal-data-sheets", views.PersonalDataSheetListView.as_view(), name='personal-data-sheet-list'),
    path("service-repair-accreditations/", views.ServiceRepairAccreditationApplicationListView.as_view(), name="service-repair-list"),
    path("inspection-validation-reports/", views.InspectionValidationReportListView.as_view(), name="inspection-validation-list"),
    path("orders-of-payment/", views.OrderOfPaymentListView.as_view(), name="order-of-payment-list"),
    path("checklist-evaluation-sheets/", views.ChecklistEvaluationSheetListView.as_view(), name="checklist-list"),

    # EXCEL VIEWS
    path("export-to-excel", views.ExportDocumentsExcelView.as_view(), name='export-to-excel'), 
    path('upload-excel', views.UploadExcelView.as_view(), name='upload-excel'),

    # ACTION VIEWS
    path('approve-documents', views.ApproveDocumentsView.as_view(), name='approve-documents')
]