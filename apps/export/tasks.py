import logging

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile

from main.celery import CeleryQueue
from apps.export.models import QuestionnaireExport
from apps.export.exporter import xlsform

logger = logging.getLogger(__name__)


@shared_task(queue=CeleryQueue.DEFAULT)
def export_task(export_id, force=False):
    try:
        export = QuestionnaireExport.objects.get(pk=export_id)
        # Skip if export is already started
        if not force and export.status != QuestionnaireExport.Status.PENDING:
            logger.warning(f'Export status is {export.get_status_display()}')
            return 'SKIPPED'

        # Update status to STARTED
        export.status = QuestionnaireExport.Status.STARTED
        export.started_at = timezone.now()
        with transaction.atomic():
            export.save(update_fields=('status', 'started_at',))

        with (
            NamedTemporaryFile(dir='/tmp/', delete=True, suffix='.xlsx') as temp_xlsx_file,
            NamedTemporaryFile(dir=settings.TEMP_FILE_DIR, delete=True, suffix='.xml') as temp_xml_file,
        ):
            xlsform.export(export, temp_xlsx_file, temp_xml_file)
            temp_xlsx_file.seek(0)
            temp_xml_file.seek(0)
            # Upload file to storage
            export.xlsx_file.save(
                f'{export.questionnaire.title}.xlsx',
                temp_xlsx_file,
            )
            export.xml_file.save(
                f'{export.questionnaire.title}.xml',
                temp_xml_file,
            )
        # Update status to SUCCESS
        export.status = QuestionnaireExport.Status.SUCCESS
        export.ended_at = timezone.now()
        with transaction.atomic():
            export.save()
        return True

    except Exception:
        export = QuestionnaireExport.objects.filter(id=export_id).first()
        # Update status to FAILURE
        if export:
            export.status = QuestionnaireExport.Status.FAILURE
            if export.started_at:
                export.ended_at = timezone.now()
            with transaction.atomic():
                export.save(update_fields=('status', 'ended_at',))
        logger.error(
            'QuestionnaireExport Failed!!',
            exc_info=True,
            extra={
                'data': {
                    'export_id': export_id,
                },
            },
        )
        return False
