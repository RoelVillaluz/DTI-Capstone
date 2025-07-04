import re
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from .forms import PersonalDataSheetForm, ProductCoveredFormSet, SalesPromotionPermitApplicationForm
from .models import PersonalDataSheet, ProductCovered, SalesPromotionPermitApplication
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CreateSalesPromotionView(LoginRequiredMixin, CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['product_formset'] = ProductCoveredFormSet(
                self.request.POST, 
                instance=self.object if hasattr(self, 'object') else None
            )
        else:
            context['product_formset'] = ProductCoveredFormSet(
                instance=self.object if hasattr(self, 'object') else None
            )

        # For dynamic reusable progress indicator partial template
        context['form_steps'] = [
            {'target': 'promo-title-fieldset', 'label': 'Promotion Details'},
            {'target': 'sponsors-fieldset', 'label': 'Sponsor'},
            {'target': 'advertising-fieldset', 'label': 'Advertising Agency'},
            {'target': 'promo-period-fieldset', 'label': 'Promo Period'},
            {'target': 'products-fieldset', 'label': 'Products Covered'},
            {'target': 'coverage-fieldset', 'label': 'Coverage'},
        ]
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        product_formset = context['product_formset']

        # Use transaction to ensure data integrity
        with transaction.atomic():
            # Set the user before saving the main form
            form.instance.user = self.request.user
            self.object = form.save()

            if product_formset.is_valid():
                # Set the instance for the formset
                product_formset.instance = self.object
                # Save the formset
                product_formset.save()

                messages.success(
                    self.request,
                    'Sales Promotion Permit Application created successfully!'
                )
                return super().form_valid(form)
            else:
                # Add formset errors to messages for debugging
                for form_errors in product_formset.errors:
                    for field, errors in form_errors.items():
                        for error in errors:
                            messages.error(self.request, f"Product {field}: {error}")
                
                # Also check non-form errors
                if product_formset.non_form_errors():
                    for error in product_formset.non_form_errors():
                        messages.error(self.request, f"Formset error: {error}")
                
                return self.form_invalid(form)
            
    def form_invalid(self, form):
        # Add main form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})

class SalesPromotionDetailView(DetailView):
    model = SalesPromotionPermitApplication
    template_name = 'documents/sales_promotion_detail.html'
    context_object_name = 'sales_promo'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        sales_promo = self.get_object()

        def split_locations(value):
            if value:
                return [item.strip() for item in re.split(r',|\n', value) if item.strip()]
            return []

        covered_locations = []
        coverage_type = None
        coverage_area_name = None  # for region_location_of_sponsor / single_region / single_province

        if sales_promo.coverage == 'NCR':
            coverage_type = 'NCR or several regions including Metro Manila'
            coverage_area_name = sales_promo.region_location_of_sponsor

        elif sales_promo.coverage == '2_REGIONS':
            coverage_type = '2 regions or more outside NCR'
            coverage_area_name = sales_promo.region_location_of_sponsor
            covered_locations = sales_promo.regions_covered

        elif sales_promo.coverage == '1_REGION_2_PROVINCES':
            coverage_type = 'Single region covering 2 provinces or more'
            coverage_area_name = sales_promo.single_region
            covered_locations = sales_promo.provinces_covered

        elif sales_promo.coverage == '1_PROVINCE':
            coverage_type = 'Single province'
            coverage_area_name = sales_promo.single_province
            covered_locations = sales_promo.cities_or_municipalities_covered

        context.update({
            'covered_locations': covered_locations,
            'location_count': len(split_locations(covered_locations)),
            'coverage_type': coverage_type,
            'coverage_area_name': coverage_area_name,
        })

        return context
    
class CreatePersonalDataSheetView(LoginRequiredMixin, CreateView):
    template_name = 'documents/create_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    context_object_name = 'personal_data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form_steps'] = [
            {'target': 'personal-background-fieldset', 'label': 'Personal Background'},
        ]
    
        return context