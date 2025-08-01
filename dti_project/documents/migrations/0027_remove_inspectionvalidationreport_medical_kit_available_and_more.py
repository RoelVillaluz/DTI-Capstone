# Generated by Django 5.2 on 2025-07-29 00:26

import documents.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0026_inspectionvalidationreport_tesda_certification_coc_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspectionvalidationreport',
            name='medical_kit_available',
        ),
        migrations.RemoveField(
            model_name='inspectionvalidationreport',
            name='record_keeping_suitable',
        ),
        migrations.AddField(
            model_name='inspectionvalidationreport',
            name='available_medical_kit',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Medical Kit', max_length=255),
        ),
        migrations.AddField(
            model_name='inspectionvalidationreport',
            name='customers_reception_waiting_area_suitable',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Suitable?', max_length=3),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='available_personal_protective_equipment',
            field=models.CharField(blank=True, help_text='Available person protective equipment', max_length=255),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='customers_reception_waiting_area_adequate',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=3, verbose_name='Adequate?'),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='customers_reception_waiting_area_existing',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Customers reception and waiting area exists?', max_length=3),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='existing_record_keeping_system',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Existing Record keeping system', max_length=3),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='fire_extinguishers_count',
            field=models.PositiveIntegerField(blank=True, help_text='No. of applicable and unexpired fire extinguishers?', null=True),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='office_work_area_sqm',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Size of shop/work area? (sq.m)', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='security_personnel_count',
            field=models.PositiveIntegerField(blank=True, help_text='No. of security Personnel', null=True),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='tool_equipment_storage_adequate',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Adequate', max_length=3),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='tool_equipment_storage_existing',
            field=documents.models.YesNoField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text='Tool and equipment storage existing?', max_length=3),
        ),
        migrations.AlterField(
            model_name='inspectionvalidationreport',
            name='working_stalls_count',
            field=models.PositiveIntegerField(blank=True, help_text='No. of working stalls/bays', null=True),
        ),
    ]
