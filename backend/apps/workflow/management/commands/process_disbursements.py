from django.core.management.base import BaseCommand
from django.db import transaction
from apps.workflow.models import Disbursement, ArtisanPayoutAccount
from apps.workflow.paystack import paystack_request

class Command(BaseCommand):
    help='Submit queued WarriWorks artisan transfers to Paystack. Run from a protected worker/scheduler.'
    def handle(self,*args,**options):
        ids=list(Disbursement.objects.filter(status='queued').values_list('id',flat=True)[:50])
        for item_id in ids:
            try:
                with transaction.atomic():
                    d=Disbursement.objects.select_for_update().select_related('artisan').get(pk=item_id)
                    if d.status!='queued': continue
                    account=ArtisanPayoutAccount.objects.get(artisan=d.artisan,verified=True)
                    if not account.recipient_code: raise RuntimeError('Artisan has no verified Paystack recipient code.')
                    d.status='processing'; d.save(update_fields=['status','updated_at'])
                result=paystack_request('/transfer',{'source':'balance','amount':d.amount_kobo,'recipient':account.recipient_code,'reason':f'WarriWorks milestone {d.milestone.sequence}','reference':d.reference})
                d.transfer_code=str(result.get('transfer_code','')); d.provider_message=str(result.get('status','pending')); d.save(update_fields=['transfer_code','provider_message','updated_at'])
                self.stdout.write(self.style.SUCCESS(f'Submitted {d.reference}; awaiting transfer webhook.'))
            except Exception as exc:
                Disbursement.objects.filter(pk=item_id,status__in=['queued','processing']).update(status='failed',provider_message=str(exc)[:1000])
                self.stderr.write(f'Disbursement {item_id}: {exc}')
