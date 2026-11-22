import hashlib, hmac, json, os, uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Payment, PaymentMilestone, LedgerEntry, PaymentWebhookEvent, Disbursement, ServiceRequest, ArtisanPayoutAccount
from .paystack import paystack_request

class PaymentInitializeView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        quote_id=request.data.get('quote_id')
        from .models import Quote
        try: quote=Quote.objects.select_related('service_request','artisan__user').get(pk=quote_id)
        except Quote.DoesNotExist: return Response({'detail':'Quotation not found.'},status=404)
        if quote.service_request.customer_id != request.user.id or quote.status != 'accepted':
            raise PermissionDenied('Only the customer who accepted this quotation can pay for it.')
        if quote.amount <= 0: raise ValidationError('Invalid quotation amount.')
        if not ArtisanPayoutAccount.objects.filter(artisan=quote.artisan,verified=True,recipient_code__gt='').exists():
            raise ValidationError('This artisan has not completed payout verification. Payment cannot be collected until a verified Paystack recipient is configured.')
        schedule=quote.payment_schedule or [
            {'name':'Initial mobilisation','percentage':70,'release_condition':'Successful payment verification and verified artisan payout account.'},
            {'name':'Verified progress','percentage':20,'release_condition':'Agreed progress evidence reviewed and approved.'},
            {'name':'Completion retention','percentage':10,'release_condition':'Customer completion approval and dispute checks.'}
        ]
        if sum(int(x.get('percentage',0)) for x in schedule)!=100: raise ValidationError('Payment schedule must total 100%.')
        if not quote.schedule_approved and int(schedule[0]['percentage'])>70:
            raise ValidationError('A higher initial allocation requires WarriWorks approval before checkout.')
        amount_kobo=int((Decimal(quote.amount)*100).quantize(Decimal('1')))
        with transaction.atomic():
            from .models import Quote
            locked_quote=Quote.objects.select_for_update().get(pk=quote.pk)
            existing=Payment.objects.filter(quote=locked_quote,status__in=['pending','successful','partially_disbursed','completed']).order_by('-created_at').first()
            if existing:
                if existing.status=='pending' and existing.checkout_url:
                    return Response({'payment_id':existing.id,'reference':existing.reference,'checkout_url':existing.checkout_url,'amount_kobo':existing.amount_kobo})
                return Response({'detail':'A payment is already pending or has been completed for this quotation.','payment_id':existing.id,'status':existing.status},status=409)
            reference='WW-'+uuid.uuid4().hex.upper()
            payment=Payment.objects.create(service_request=quote.service_request,quote=locked_quote,reference=reference,amount=quote.amount,amount_kobo=amount_kobo,status='pending')
        try:
            data=paystack_request('/transaction/initialize',{'email':request.user.email,'amount':amount_kobo,'currency':'NGN','reference':reference,'metadata':{'payment_id':payment.id,'quote_id':quote.id,'service_request_id':quote.service_request_id},'callback_url':os.getenv('PAYSTACK_CALLBACK_URL','http://localhost:3000/payment/return')})
        except Exception as exc:
            payment.status='failed'; payment.save(update_fields=['status'])
            return Response({'detail':str(exc)},status=502)
        payment.checkout_url=data.get('authorization_url',''); payment.save(update_fields=['checkout_url'])
        return Response({'payment_id':payment.id,'reference':reference,'checkout_url':payment.checkout_url,'amount_kobo':amount_kobo},status=201)

class PaymentDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,pk):
        try: p=Payment.objects.prefetch_related('milestones').get(pk=pk)
        except Payment.DoesNotExist:return Response({'detail':'Payment not found.'},status=404)
        if not (request.user.is_staff or p.service_request.customer_id==request.user.id or p.quote.artisan.user_id==request.user.id): raise PermissionDenied()
        return Response({'id':p.id,'status':p.status,'amount':str(p.amount),'amount_kobo':p.amount_kobo,'reference':p.reference,'verified_at':p.verified_at,'milestones':[{'id':m.id,'sequence':m.sequence,'name':m.name,'percentage':m.percentage,'amount_kobo':m.amount_kobo,'status':m.status,'release_condition':m.release_condition} for m in p.milestones.all()]})

def verify_and_activate(reference):
    payment=Payment.objects.select_related('quote','service_request','quote__artisan').get(reference=reference)
    data=paystack_request('/transaction/verify/'+reference)
    expected=payment.amount_kobo
    if data.get('status')!='success' or int(data.get('amount',-1))!=expected or data.get('currency')!='NGN' or data.get('reference')!=reference:
        raise ValueError('Paystack transaction verification did not match the expected payment.')
    with transaction.atomic():
        p=Payment.objects.select_for_update().get(pk=payment.pk)
        if p.status in ('successful','partially_disbursed','completed'): return p
        p.status='successful'; p.verified_at=timezone.now(); p.provider_transaction_id=str(data.get('id','')); p.save(update_fields=['status','verified_at','provider_transaction_id'])
        schedule=p.quote.payment_schedule or [
            {'name':'Initial mobilisation','percentage':70,'release_condition':'Successful payment verification and verified artisan payout account.'},
            {'name':'Verified progress','percentage':20,'release_condition':'Agreed progress evidence reviewed and approved.'},
            {'name':'Completion retention','percentage':10,'release_condition':'Customer completion approval and dispute checks.'}
        ]
        if not p.milestones.exists():
            assigned=0
            for index,item in enumerate(schedule,1):
                pct=int(item['percentage']); amount=(expected*pct)//100
                if index==len(schedule): amount=expected-assigned
                assigned+=amount
                milestone=PaymentMilestone.objects.create(payment=p,sequence=index,name=item['name'],percentage=pct,amount_kobo=amount,release_condition=item.get('release_condition',''))
                LedgerEntry.objects.create(payment=p,milestone=milestone,entry_type='milestone_allocated',amount_kobo=amount,reference=f'{reference}-ALLOC-{index}',description=f'{pct}% allocated to {item["name"]}')
            first=p.milestones.order_by('sequence').first()
            if first:
                first.status='ready'; first.save(update_fields=['status'])
                
                if ArtisanPayoutAccount.objects.filter(artisan=p.quote.artisan,verified=True,recipient_code__gt='').exists():
                    Disbursement.objects.get_or_create(milestone=first,defaults={'artisan':p.quote.artisan,'amount_kobo':first.amount_kobo,'reference':f'{reference}-PAYOUT-1','status':'queued'})
        p.service_request.status='in_progress'; p.service_request.save(update_fields=['status','updated_at'])
    return p

class PaymentVerifyView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        reference=request.data.get('reference')
        try: payment=Payment.objects.select_related('service_request').get(reference=reference)
        except Payment.DoesNotExist:return Response({'detail':'Payment reference not found.'},status=404)
        if payment.service_request.customer_id!=request.user.id and not request.user.is_staff: raise PermissionDenied()
        try: p=verify_and_activate(reference)
        except Exception as exc:return Response({'detail':str(exc)},status=400)
        return Response({'payment_id':p.id,'status':p.status,'reference':p.reference})

@csrf_exempt
def paystack_webhook(request):
    if request.method!='POST': return HttpResponse(status=405)
    secret=os.getenv('PAYSTACK_SECRET_KEY','')
    signature=request.headers.get('x-paystack-signature','')
    expected=hmac.new(secret.encode(),request.body,hashlib.sha512).hexdigest() if secret else ''
    if not secret or not hmac.compare_digest(signature,expected): return HttpResponse(status=401)
    try: payload=json.loads(request.body.decode()); event=payload.get('event',''); data=payload.get('data',{})
    except Exception:return HttpResponse(status=400)
    key=str(data.get('id') or data.get('reference') or hashlib.sha256(request.body).hexdigest())+'-'+event
    with transaction.atomic():
        event_obj,created=PaymentWebhookEvent.objects.get_or_create(provider_event_key=key,defaults={'event_type':event,'payload':payload})
        if not created and event_obj.processed_at:return HttpResponse(status=200)
    try:
        if event=='charge.success':
            verify_and_activate(data.get('reference',''))
        elif event in ('transfer.success','transfer.failed','transfer.reversed'):
            ref=data.get('reference','')
            with transaction.atomic():
                dis=Disbursement.objects.select_for_update().filter(reference=ref).first()
                if dis:
                    status_map={'transfer.success':'successful','transfer.failed':'failed','transfer.reversed':'reversed'}
                    dis.status=status_map[event]; dis.transfer_code=str(data.get('transfer_code') or dis.transfer_code); dis.provider_message=str(data.get('reason',''))
                    dis.save(update_fields=['status','transfer_code','provider_message','updated_at'])
                    milestone=dis.milestone
                    if event=='transfer.success':
                        milestone.status='paid'; milestone.released_at=timezone.now(); milestone.save(update_fields=['status','released_at'])
                        LedgerEntry.objects.get_or_create(reference=f'{dis.reference}-PAID',defaults={'payment':milestone.payment,'milestone':milestone,'entry_type':'artisan_transfer_success','amount_kobo':-dis.amount_kobo,'description':'Paystack confirmed artisan transfer.'})
                        payment=milestone.payment
                        if not payment.milestones.exclude(status='paid').exists(): payment.status='completed'
                        else: payment.status='partially_disbursed'
                        payment.save(update_fields=['status'])
                    elif event in ('transfer.failed','transfer.reversed'):
                        milestone.status='ready'; milestone.save(update_fields=['status'])
        with transaction.atomic():
            PaymentWebhookEvent.objects.filter(pk=event_obj.pk).update(processed_at=timezone.now())
    except Exception:
        # Return non-2xx so Paystack retries; idempotency prevents duplicate processing.
        return HttpResponse(status=500)
    return HttpResponse(status=200)


class MilestoneEvidenceView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,pk):
        try: m=PaymentMilestone.objects.select_related('payment__quote__artisan','payment__service_request').get(pk=pk)
        except PaymentMilestone.DoesNotExist:return Response({'detail':'Milestone not found.'},status=404)
        if m.payment.quote.artisan.user_id!=request.user.id: raise PermissionDenied('Only the assigned artisan can submit evidence.')
        if m.sequence==1: raise ValidationError('The initial mobilisation milestone is activated by verified payment.')
        urls=request.data.get('evidence',[])
        if not isinstance(urls,list) or not urls or any(not isinstance(x,str) or not x.startswith(('https://','http://')) for x in urls): raise ValidationError('Submit one or more valid evidence URLs.')
        m.evidence=urls; m.status='blocked'; m.save(update_fields=['evidence','status'])
        return Response({'id':m.id,'status':m.status,'evidence':m.evidence})

class MilestoneApproveView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,pk):
        if not request.user.is_staff: raise PermissionDenied('WarriWorks operations approval is required.')
        try: m=PaymentMilestone.objects.select_related('payment__quote__artisan').get(pk=pk)
        except PaymentMilestone.DoesNotExist:return Response({'detail':'Milestone not found.'},status=404)
        if m.sequence>1 and not m.evidence: raise ValidationError('Evidence is required before approval.')
        previous=PaymentMilestone.objects.filter(payment=m.payment,sequence__lt=m.sequence).exclude(status='paid').exists()
        if previous: raise ValidationError('The previous milestone must be successfully settled before this milestone can be released.')
        if m.payment.status=='disputed': raise ValidationError('This payment is on dispute hold.')
        account=ArtisanPayoutAccount.objects.filter(artisan=m.payment.quote.artisan,verified=True,recipient_code__gt='').first()
        if not account: raise ValidationError('Artisan must have a verified Paystack payout recipient before release.')
        with transaction.atomic():
            m=PaymentMilestone.objects.select_for_update().get(pk=pk)
            m.status='ready'; m.approved_at=timezone.now(); m.save(update_fields=['status','approved_at'])
            Disbursement.objects.get_or_create(milestone=m,defaults={'artisan':m.payment.quote.artisan,'amount_kobo':m.amount_kobo,'reference':f'{m.payment.reference}-PAYOUT-{m.sequence}','status':'queued'})
        return Response({'id':m.id,'status':m.status,'detail':'Milestone approved and transfer queued.'})
