from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets,permissions,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied,ValidationError
from apps.marketplace.models import ArtisanProfile
from .models import ServiceRequest,Quote,Review,Payment,PaymentMilestone,Disbursement,ArtisanPayoutAccount
from .serializers import RequestSerializer,QuoteSerializer,ReviewSerializer
class RequestPermission(permissions.BasePermission):
 def has_object_permission(self,request,view,obj):
  if request.user.is_staff or obj.customer_id == request.user.id:
   return True
  if request.user.role == 'artisan' and hasattr(request.user, 'artisan_profile'):
   return obj.artisan_id == request.user.artisan_profile.id or (obj.artisan_id is None and obj.status == 'open')
  return False
class ServiceRequestViewSet(viewsets.ModelViewSet):
 serializer_class=RequestSerializer; permission_classes=[permissions.IsAuthenticated,RequestPermission]
 def get_queryset(self):
  u=self.request.user
  if u.is_staff:return ServiceRequest.objects.all()
  if u.role=='artisan': return ServiceRequest.objects.filter(Q(artisan__user=u)|Q(artisan__isnull=True,status='open'))
  return ServiceRequest.objects.filter(customer=u)
 def perform_create(self,serializer): serializer.save(customer=self.request.user)
 @action(detail=True,methods=['post'])
 def accept(self,request,pk=None):
  obj=self.get_object()
  if request.user.role!='artisan': raise PermissionDenied()
  artisan=ArtisanProfile.objects.get(user=request.user)
  with transaction.atomic():
   locked=ServiceRequest.objects.select_for_update().get(pk=obj.pk)
   if locked.status!='open' or locked.artisan_id: raise ValidationError('This request is no longer available.')
   locked.artisan=artisan; locked.status='accepted'; locked.save(update_fields=['artisan','status','updated_at'])
  return Response(self.get_serializer(locked).data)
 @action(detail=True,methods=['post'])
 def complete(self,request,pk=None):
  obj=self.get_object()
  if request.user.role!='artisan' or not obj.payments.filter(status__in=['successful','partially_disbursed']).exists(): raise PermissionDenied('A verified payment is required before completion.')
  obj.status='completion_review'; obj.save(update_fields=['status','updated_at']); return Response(self.get_serializer(obj).data)
 @action(detail=True,methods=['get'])
 def payment(self,request,pk=None):
  obj=self.get_object()
  payment=obj.payments.prefetch_related('milestones').order_by('-created_at').first()
  if not payment: return Response({'detail':'No payment has been created for this request.'},status=404)
  return Response({'id':payment.id,'status':payment.status,'amount':str(payment.amount),'reference':payment.reference,'milestones':[{'id':m.id,'name':m.name,'percentage':m.percentage,'amount_kobo':m.amount_kobo,'status':m.status,'release_condition':m.release_condition} for m in payment.milestones.all()]})
 @action(detail=True,methods=['post'])
 def confirm_completion(self,request,pk=None):
  obj=self.get_object()
  if obj.customer_id!=request.user.id or obj.status!='completion_review': raise PermissionDenied()
  with transaction.atomic():
   obj.status='completed'; obj.save(update_fields=['status','updated_at'])
   payment=Payment.objects.filter(service_request=obj,status__in=['successful','partially_disbursed']).order_by('-created_at').first()
   if payment:
    final=payment.milestones.order_by('-sequence').first()
    if final and final.status!='paid' and not payment.status=='disputed':
     previous=payment.milestones.filter(sequence__lt=final.sequence).exclude(status='paid').exists()
     account=ArtisanPayoutAccount.objects.filter(artisan=payment.quote.artisan,verified=True,recipient_code__gt='').first()
     if not previous and account:
      final.status='ready'; final.approved_at=timezone.now(); final.save(update_fields=['status','approved_at'])
      Disbursement.objects.get_or_create(milestone=final,defaults={'artisan':payment.quote.artisan,'amount_kobo':final.amount_kobo,'reference':f'{payment.reference}-PAYOUT-{final.sequence}','status':'queued'})
  return Response(self.get_serializer(obj).data)
class QuoteViewSet(viewsets.ModelViewSet):
 serializer_class=QuoteSerializer; permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):
  u=self.request.user
  if u.is_staff:return Quote.objects.all()
  return Quote.objects.filter(Q(service_request__customer=u)|Q(artisan__user=u))
 def perform_create(self,serializer):
  if self.request.user.role!='artisan': raise PermissionDenied()
  artisan=ArtisanProfile.objects.get(user=self.request.user); req=serializer.validated_data['service_request']
  if req.artisan_id!=artisan.id or req.status not in ('accepted','quoted'): raise PermissionDenied('You cannot quote this request.')
  quote=serializer.save(artisan=artisan,version=req.quotes.count()+1)
  req.status='quoted'; req.save(update_fields=['status','updated_at'])
 @action(detail=True,methods=['post'],permission_classes=[permissions.IsAdminUser])
 def approve_schedule(self,request,pk=None):
  quote=self.get_object()
  schedule=quote.payment_schedule or []
  if sum(int(x.get('percentage',0)) for x in schedule)!=100: raise ValidationError('Milestones must total 100%.')
  quote.schedule_approved=True; quote.schedule_review_reason=request.data.get('reason','Approved by WarriWorks operations.'); quote.save(update_fields=['schedule_approved','schedule_review_reason'])
  return Response(self.get_serializer(quote).data)
 @action(detail=True,methods=['post'])
 def accept(self,request,pk=None):
  quote=self.get_object()
  if quote.service_request.customer_id!=request.user.id or quote.status!='pending': raise PermissionDenied()
  schedule=quote.payment_schedule or [{'percentage':70},{'percentage':20},{'percentage':10}]
  if sum(int(x.get('percentage',0)) for x in schedule)!=100: raise ValidationError('Payment schedule must total 100%.')
  if int(schedule[0].get('percentage',0))>70 and not quote.schedule_approved: raise ValidationError('This higher initial allocation has not been approved by WarriWorks.')
  with transaction.atomic():
   quote.status='accepted'; quote.save(update_fields=['status'])
   req=ServiceRequest.objects.select_for_update().get(pk=quote.service_request_id); req.status='payment_pending'; req.save(update_fields=['status','updated_at'])
  return Response(self.get_serializer(quote).data)
class ReviewViewSet(viewsets.ModelViewSet):
 serializer_class=ReviewSerializer; permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self): return Review.objects.filter(artisan__user=self.request.user) if self.request.user.role=='artisan' else Review.objects.filter(customer=self.request.user)
 def perform_create(self,serializer):
  req=serializer.validated_data['service_request']
  if req.customer_id!=self.request.user.id or req.status!='completed' or not req.artisan_id: raise PermissionDenied('Only completed jobs can be reviewed.')
  serializer.save(customer=self.request.user,artisan=req.artisan)
