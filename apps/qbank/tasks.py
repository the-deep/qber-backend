import logging

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from main.celery import CeleryQueue
from apps.qbank.models import QuestionBank
from apps.qbank.importer.xlsxform import XlsFormImport, XlsFormValidationError

logger = logging.getLogger(__name__)


@shared_task(queue=CeleryQueue.DEFAULT)
def import_task(qbank_id, force=False):
    try:
        qbank = QuestionBank.objects.get(pk=qbank_id)
        # Skip if qbank is already started
        if not force and qbank.status != QuestionBank.Status.PENDING:
            logger.warning(f'qbank status is {qbank.get_status_display()}')
            return 'SKIPPED'

        # Update status to STARTED
        qbank.status = QuestionBank.Status.STARTED
        qbank.started_at = timezone.now()
        with transaction.atomic():
            qbank.save(update_fields=('status', 'started_at',))
        # Process
        importer = XlsFormImport(qbank)
        with transaction.atomic():  # Revert back if there are any error
            importer.process()
        qbank.status = QuestionBank.Status.SUCCESS
        qbank.ended_at = timezone.now()
        with transaction.atomic():
            qbank.save()
        return True

    except Exception as e:
        qbank = QuestionBank.objects.filter(id=qbank_id).first()
        # Update status to FAILURE
        if qbank:
            qbank.status = QuestionBank.Status.FAILURE
            if qbank.started_at:
                qbank.ended_at = timezone.now()
            if isinstance(e, XlsFormValidationError):
                qbank.errors = e.errors
            with transaction.atomic():
                qbank.save(update_fields=('status', 'errors', 'ended_at',))
        logger.error(
            'QuestionBank import Failed!!',
            exc_info=True,
            extra={
                'data': {
                    'qbank_id': qbank_id,
                },
            },
        )
        return False
