from datetime import date
import re
from django import forms
from .utils.form_helpers import create_inline_formset
from .validators import validate_period
from .models import CharacterReference, ChecklistEvaluationSheet, EducationalAttainment, EmployeeBackground, InspectionValidationReport, OrderOfPayment, ProductCovered, SalesPromotionPermitApplication, PersonalDataSheet, Service, ServiceCategory, ServiceRepairAccreditationApplication, TrainingsAttended
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, LayoutObject, TEMPLATE_PACK, Fieldset, HTML, Div, Row, Column, Submit
from django.template.loader import render_to_string
from django.forms.widgets import SelectMultiple

class SortForm(forms.Form):
    SORT_CHOICES = [
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)')
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='sort_by')

class BaseCustomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user if passed
        super().__init__(*args, **kwargs)

        # --- Field formatting ---
        if hasattr(self, 'fields'):
            for name, field in self.fields.items():
                label_text = field.label if field.label else name.replace('_', ' ').title()
                if field.required:
                    field.label = f"{label_text} <span class='required-label'>*</span>"
                    field.widget.attrs['placeholder'] = f"Enter {label_text}"
                else:
                    field.label = label_text

                # Date fields
                if isinstance(field, forms.DateField):
                    field.widget = forms.DateInput(attrs={'type': 'date'})

                # Textarea rows
                if isinstance(field.widget, forms.Textarea):
                    field.widget.attrs['rows'] = 4

                # Add common class
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} form-group".strip()

                # Numeric fields
                numerical_fields = [
                    'tax_identification_number',
                    'contact_number',
                    'mobile_number',
                    'fax_number',
                    'telephone_number',
                ]
                if name in numerical_fields:
                    field.widget.attrs.update({
                        'inputmode': 'numeric',
                        'pattern': r'\d*',
                        'oninput': "this.value=this.value.replace(/[^0-9]/g,'')",
                    })

                if name in ['contact_number', 'mobile_number']:
                    field.validators.append(self.validate_contact_number)
                    field.widget.attrs['maxlength'] = 11

                if name == 'date_of_birth':
                    field.validators.append(self.validate_date_of_birth)
                    field.widget.attrs['max'] = date.today().isoformat()

        # --- Auto-fill user fields ---
        if user:
            # Check if extra fields exist on a profile
            profile = getattr(user, 'profile', None)

            user_field_map = {
                'full_name': 'get_full_name',  # method 
                'first_name': 'first_name',
                'last_name': 'last_name',
                'email': 'email',
                'email_address': 'email',               # alias
                'mobile_number': 'default_phone',     # profile field
                'contact_number': 'default_phone',    # alias
                'current_address': 'default_address',         # profile field
                'address': 'default_address',                 # alias
            }

            for field_name, attr_name in user_field_map.items():
                if field_name in self.fields and not self.initial.get(field_name):
                    # First try profile, fallback to user
                    value = ''
                    if profile and hasattr(profile, attr_name):
                        value = getattr(profile, attr_name, '')
                    elif hasattr(user, attr_name):
                        value = getattr(user, attr_name, '')
                    self.fields[field_name].initial = value

    def validate_contact_number(self, value):
        if not re.fullmatch(r'\d{11}', str(value)):
            raise forms.ValidationError("Contact/Mobile number must be exactly 11 digits.")
        
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise forms.ValidationError('Date of birth cannot be in the future.')




class SalesPromotionPermitApplicationForm(BaseCustomForm):
    class Meta:
        model = SalesPromotionPermitApplication
        fields = '__all__'
        exclude = ['status', 'date_filed', 'user']
        widgets = {
            'promo_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
            'promo_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        promo_start_date = cleaned_data.get('promo_period_start')  # Fixed field name
        promo_end_date = cleaned_data.get('promo_period_end')      # Fixed field name

        # Call your dynamic validator
        if promo_start_date and promo_end_date:
            validate_period(promo_start_date, promo_end_date, 'Promo start date', 'Promo end date')

        return cleaned_data

class ProductCoveredForm(BaseCustomForm):
    class Meta:
        model = ProductCovered
        fields = ['name', 'brand', 'specifications']

class PersonalDataSheetForm(BaseCustomForm):
    class Meta:
        model = PersonalDataSheet
        fields = '__all__'
        exclude = ['status', 'user', 'date']
        widgets = {
            'current_address': forms.TextInput(attrs={'class': 'form-group'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
            'image': forms.FileInput(attrs={
                'class': 'hidden-file-input',
                'accept': 'image/*',
                'id': 'id_image'
            })
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Hide the "Currently" label for image field
            self.fields['image'].widget.attrs.update({
                'style': 'display: none;'
            })
            # Remove help text that shows "Currently: filename"
            self.fields['image'].widget.clear_checkbox_label = ''
            self.fields['image'].widget.initial_text = ''
            self.fields['image'].widget.input_text = ''

class EmployeeBackgroundForm(BaseCustomForm):
    class Meta:
        model = EmployeeBackground
        fields = '__all__'
        exclude = ['personal_data_sheet']

class TrainingsAttendedForm(BaseCustomForm):
    class Meta:
        model = TrainingsAttended
        fields = '__all__'
        exclude = ['personal_data_sheet']

class EducationalAttainmentForm(BaseCustomForm):
    class Meta:
        model = EducationalAttainment
        fields = '__all__'
        exclude = ['personal_data_sheet']     

class CharacterReferenceForm(BaseCustomForm):
    class Meta:
        model = CharacterReference
        fields = '__all__'
        exclude = ['personal_data_sheet']     

class ServiceRepairAccreditationApplicationForm(BaseCustomForm):
    class Meta:
        model = ServiceRepairAccreditationApplication
        fields = '__all__'
        exclude = ['status', 'user', 'date']

class InspectionValidationReportForm(BaseCustomForm):
    class Meta:
        model = InspectionValidationReport
        fields = '__all__'
        exclude = ['status', 'date', 'user']
        widgets = {
            'services_offered': forms.CheckboxSelectMultiple()
        }

class ServiceCategoryForm(BaseCustomForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class ServiceForm(BaseCustomForm):
    class Meta:
        model = Service
        fields = '__all__'

class OrderOfPaymentForm(BaseCustomForm):
    class Meta:
        model = OrderOfPayment
        fields = '__all__'
        exclude = ['status', 'date', 'user']

class ChecklistEvaluationSheetForm(BaseCustomForm):
    renewal_year = forms.IntegerField(label="Date Expired: Dec 31, ____", min_value=1900)

    class Meta:
        model = ChecklistEvaluationSheet
        fields = '__all__'
        exclude = ['status', 'user', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        self.fields['renewal_year'].max_value = current_year
        self.fields['renewal_year'].initial = current_year - 1

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('renewal_year')
        if year:
            cleaned_data['renewal_due_date'] = date(year, 12, 31)
        return cleaned_data

# Formset configurations
FORMSET_CONFIGS = {
    # Sales Application Formsets
    'product_covered': {
        'parent_model': SalesPromotionPermitApplication,
        'child_model': ProductCovered,
        'form_class': ProductCoveredForm,
        'fields': ['name', 'brand', 'specifications'],
    },

    # Personal Data Sheet Formsets
    'employee_background': {
        'parent_model': PersonalDataSheet,  
        'child_model': EmployeeBackground,
        'form_class': EmployeeBackgroundForm,
    },
    'trainings_attended': {
        'parent_model': PersonalDataSheet,
        'child_model': TrainingsAttended,
        'form_class': TrainingsAttendedForm
    },
    'educational_attainment': {
        'parent_model': PersonalDataSheet,
        'child_model': EducationalAttainment,
        'form_class': EducationalAttainmentForm
    },
    'character_references': {
        'parent_model': PersonalDataSheet,
        'child_model': CharacterReference,
        'form_class': CharacterReferenceForm
    },
}

FORMSET_CLASSES = {}

for key, config in FORMSET_CONFIGS.items():
    FORMSET_CLASSES[key] = create_inline_formset(**config)
