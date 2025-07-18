from django.db import transaction
from django.contrib import messages
from itertools import chain

class FormsetMixin:
    formset_classes = {}  # Example: {'employee': EmployeeBackgroundFormset, 'training': TrainingsAttendedFormset}

    def get_formsets(self, instance=None):
        """
        Get all formsets for the view.
        Override this method to customize formset creation.
        """
        formsets = {}
        
        if self.request.method == 'POST':
            for key, formset_class in self.formset_classes.items():
                prefix = key.replace('-', '_')
                formsets[key] = formset_class(
                    self.request.POST,
                    instance=instance,
                    prefix=prefix
                )
        else:
            for key, formset_class in self.formset_classes.items():
                prefix = key.replace('-', '_')
                formsets[key] = formset_class(
                    instance=instance,
                    prefix=prefix
                )
        
        return formsets
    
    def get_context_data(self, **kwargs):
        """
        Add formsets to the context.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the instance if it exists
        instance = getattr(self, 'object', None)
        
        # Get formsets using the proper method
        formsets = self.get_formsets(instance=instance)
        
        # Add formsets to context
        context['formsets'] = {}
        for key, formset in formsets.items():
            context[f'{key}_formset'] = formset  # Keep individual formset context variables
            context['formsets'][key] = formset   # Add to formsets dict
        
        return context
    
    def formsets_valid(self, formsets):
        """
        Check if all formsets are valid.
        """
        return all(formset.is_valid() for formset in formsets.values())
    
    def save_formsets(self, formsets):
        """
        Save all valid formsets.
        """
        for formset in formsets.values():
            formset.save()

    def form_valid(self, form):
        print("=== DEBUG: form_valid called ===")
        print(f"POST data keys: {list(self.request.POST.keys())}")
        
        # Check for formset data in POST
        for key in self.formset_classes.keys():
            total_forms_key = f"{key}-TOTAL_FORMS"
            print(f"Looking for {total_forms_key}: {self.request.POST.get(total_forms_key)}")
        
        context = self.get_context_data()
        instance = form.instance

        with transaction.atomic():
            instance.user = self.request.user
            self.object = form.save()

            # Get formsets with the saved instance
            formsets = self.get_formsets(instance=self.object)
            
            print(f"Formsets created: {list(formsets.keys())}")
            
            # Debug each formset
            for key, formset in formsets.items():
                print(f"Formset {key}:")
                print(f"  - Is valid: {formset.is_valid()}")
                print(f"  - Total forms: {formset.total_form_count()}")
                print(f"  - Errors: {formset.errors}")
                print(f"  - Non-form errors: {formset.non_form_errors()}")

            # Validate all formsets
            all_valid = True
            for key, formset in formsets.items():
                if not formset.is_valid():
                    all_valid = False

            if all_valid:
                # Save them if valid
                self.save_formsets(formsets)
                messages.success(self.request, f"{self.model._meta.verbose_name} created successfully!")
                return super().form_valid(form)
            else:
                # Collect formset errors
                for key, formset in formsets.items():
                    for i, form_errors in enumerate(formset.errors):
                        for field, errors in form_errors.items():
                            message = f"{key.capitalize()} Form {i+1} - {field}: " + "; ".join(errors)
                            messages.error(self.request, message)
                    non_form_errors = formset.non_form_errors()
                    if non_form_errors:
                        messages.error(self.request, f"{key.capitalize()} Formset error: " + "; ".join(non_form_errors))
                return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            message = f"{field}: " + "; ".join(errors)
            messages.error(self.request, message)

        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class FormStepsMixin:
    form_steps = []  # Default empty list
    
    def get_form_steps(self):
        """
        Automatically generate form_steps from FIELD_GROUPS and formset_classes
        """
        steps = []
        
        # Add fieldsets from FIELD_GROUPS
        if hasattr(self, 'FIELD_GROUPS'):
            for group in self.FIELD_GROUPS:
                steps.append(('fieldset', group))
        
        # Add formsets from formset_classes
        if hasattr(self, 'formset_classes'):
            for formset_key in self.formset_classes.keys():
                steps.append(('formset', formset_key))
        
        # Add any additional sections (like coverage)
        if hasattr(self, 'additional_sections'):
            for section in self.additional_sections:
                steps.append(('section', section))
        
        return steps
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get form steps (either manually defined or auto-generated)
        if hasattr(self, 'form_steps') and self.form_steps:
            form_steps = self.form_steps
        else:
            form_steps = self.get_form_steps()
        
        if form_steps:
            # Total parts calculation
            context['total_parts'] = len(form_steps)
            
            # Create enumerated steps with proper counter
            context['enumerated_steps'] = []
            for i, step in enumerate(form_steps, 1):
                step_type, step_data = step[0], step[1]
                
                if step_type == 'fieldset':
                    context['enumerated_steps'].append((i, 'fieldset', step_data))
                elif step_type == 'formset':
                    formset_key = step_data
                    formset = context['formsets'][formset_key]
                    context['enumerated_steps'].append((i, 'formset', formset_key, formset))
                elif step_type == 'section':
                    context['enumerated_steps'].append((i, 'section', step_data))
        
        return context
