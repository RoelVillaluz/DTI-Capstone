from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView, LogoutView
from users.mixins import FormSubmissionMixin
from .models import User
from .forms import CustomLoginForm, CustomUserCreationForm
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging
from django.views.generic import TemplateView, View, DetailView, UpdateView
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from users.models import User
from django.views.generic import ListView

from documents.models import (
    # Base models
    BaseApplication,
    DraftModel,
    YesNoField,
    PeriodModel,
    
    # Checklist evaluation
    ChecklistEvaluationSheet,
    
    # Inspection validation
    InspectionValidationReport,
    
    # Order of payment
    OrderOfPayment,
    
    # Personal data sheet models
    PersonalDataSheet,
    EmployeeBackground,
    TrainingsAttended,
    EducationalAttainment,
    CharacterReference,
    
    # Sales promotion models
    SalesPromotionPermitApplication,
    ProductCovered,
    
    # Service repair accreditation models
    ServiceRepairAccreditationApplication,
    Service,
    ServiceCategory,
)

logger = logging.getLogger(__name__)

# Create your views here.

#Settings View
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"

#Profile Detail and Edit Views
class ProfileDetailView(DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Document queries
        sales_promos = SalesPromotionPermitApplication.objects.filter(user=profile)
        personal_data_sheets = PersonalDataSheet.objects.filter(user=profile)
        service_accreditations = ServiceRepairAccreditationApplication.objects.filter(user=profile)
        inspection_reports = InspectionValidationReport.objects.filter(user=profile)
        orders_of_payment = OrderOfPayment.objects.filter(user=profile)
        checklist_evaluation_sheets = ChecklistEvaluationSheet.objects.filter(user=profile)

        # Total count
        total_documents = (
            sales_promos.count()
            + personal_data_sheets.count()
            + service_accreditations.count()
            + inspection_reports.count()
            + orders_of_payment.count()
            + checklist_evaluation_sheets.count()
        )

        # Add to context
        context.update({
            "sales_promos": sales_promos,
            "personal_data_sheets": personal_data_sheets,
            "service_accreditations": service_accreditations,
            "inspection_reports": inspection_reports,
            "orders_of_payment": orders_of_payment,
            "checklist_evaluation_sheets": checklist_evaluation_sheets,
            "total_documents": total_documents,
        })
        return context

class StaffListView(ListView):
    model = User
    template_name = 'users/staff_accounts.html'
    
    def get_queryset(self):
        qs = User.objects.filter(role='collection_agent')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': self.get_queryset(),
            'user_type': 'staff'
        })
        return context
    
class BusinessOwnerListView(ListView):
    model = User
    template_name = 'users/bo_accounts.html'
    
    def get_queryset(self):
        qs = User.objects.filter(role='business_owner')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': self.get_queryset(),
            'user_type': 'business_owner'
        })
        return context

class ProfileEditView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', 'profile_picture', 'default_address', 'default_phone']
    template_name = "users/profile_edit.html"
    context_object_name = "profile"

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})


class CustomLoginView(FormSubmissionMixin, LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomLoginForm
    
    def get_success_url(self) -> str:
        return reverse_lazy('dashboard')
    
class CustomRegisterView(FormSubmissionMixin, CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        print("=== POST METHOD CALLED ===")
        print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
        print(f"POST data: {dict(request.POST)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("=== FORM_VALID CALLED ===")
        user = form.save(commit=False)
        user.is_verified = False
        user.save()

        user.generate_secure_otp_code()
        print(f"[DEBUG] Verification code for {user.username}: {user.verification_code}")

        self.request.session['pending_verification_user'] = user.id

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Please enter the verification code.',
                'show_verification': True,
                'masked_email': self.mask_email(user.email),
            })

        return super().form_valid(form)

    @staticmethod
    def mask_email(email):
        if '@' not in email:
            return email
        username, domain = email.split('@', 1)
        masked_username = username[:2] + '*' * (len(username) - 2) if len(username) > 2 else '*' * len(username)
        return f"{masked_username}@{domain}"

    

class VerifyUserView(View):
    """Handles OTP verification separately"""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)

        # Get code from request
        code = request.POST.get('verification_code') or request.POST.get('code', '')

        if not code:
            digits = [request.POST.get(f'digit_{i}', '') for i in range(1, 7)]
            code = ''.join(digits)

        if not code or len(code) != 6:
            return JsonResponse({'success': False, 'error': 'Please enter a valid 6-digit code'}, status=400)

        # Verify
        if user.is_verification_code_valid(code):
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expiration_date = None
            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            del request.session['pending_verification_user']

            return JsonResponse({
                'success': True,
                'message': 'Verification successful!',
                'redirect': reverse('dashboard')
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid or expired verification code'}, status=400)

class ResendCodeView(View):
    """Handles resending OTP"""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)
        user.generate_secure_otp_code()

        # ✅ log it to terminal
        print(f"[DEBUG] Resent verification code for {user.username}: {user.verification_code}")

        return JsonResponse({
            'success': True,
            'message': 'Verification code resent!'
        })

# ---------------------- FUNCTION BASED VIEWS --------------------------- #    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")

def check_email_exists(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if get_user_model().objects.filter(email=email).exists():
                return HttpResponse('<span style="color: red;">This email already exists</span>')
            else:
                return HttpResponse('<span style="color: green;">Email is available</span>')
    return HttpResponse("")

def check_password_strength(request):
    password = request.POST.get('password1', "")
    try:
        validate_password(password)
        html = '<span id="message-success" style="color: green;">Strong password</span>'
        response = HttpResponse(html)
        response['HX-Trigger'] = 'passwordValid'
        return response
    except ValidationError as e:
        error_spans = "".join(
            f'<span id="message-error" style="color:red; display:block;">{msg}</span>'
            for msg in e.messages
        )
        response = HttpResponse(error_spans)
        response['HX-Trigger'] = 'passwordInvalid'
        return response
    
def check_passwords_match(request):
    pass