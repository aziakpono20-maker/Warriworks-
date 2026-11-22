import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.accounts.models import User
from apps.marketplace.models import ArtisanProfile,ServiceCategory
from apps.workflow.models import ServiceRequest
class Command(BaseCommand):
 help='Idempotently import legacy WarriWorks JSON records from the project root.'
 def add_arguments(self,parser): parser.add_argument('--source',default='.')
 def read(self,root,name):
  p=Path(root)/name
  if not p.exists() or not p.stat().st_size:return []
  try:
   data=json.loads(p.read_text(encoding='utf-8')); return data if isinstance(data,list) else []
  except (json.JSONDecodeError,OSError) as e:
   self.stderr.write(self.style.WARNING(f'Skipping {name}: {e}')); return []
 def handle(self,*args,**opts):
  root=opts['source']; artisans=self.read(root,'artisans.json'); accts=self.read(root,'artisan_accounts.json'); customers=self.read(root,'customer_accounts.json'); requests=self.read(root,'requests.json')
  self.stdout.write(f'Found {len(artisans)} artisans, {len(accts)} artisan accounts, {len(customers)} customers, {len(requests)} requests.')
  artisan_map={}
  for row in artisans:
   aid=row.get('ID') or row.get('id')
   if not aid: continue
   artisan_map[str(aid)]=row
  users_by_legacy={}
  for role,rows in [('customer',customers),('artisan',accts)]:
   for row in rows:
    email=(row.get('email') or '').strip().lower()
    if not email: continue
    existing=User.objects.filter(email=email).first()
    if existing:
     user=existing
     if role=='artisan' and user.role=='customer':
      self.stderr.write(self.style.WARNING(f'{email} exists as customer; artisan account not merged automatically.'))
    else:
     username=(row.get('username') or email.split('@')[0] or f'legacy{row.get("account_id",row.get("customer_id",0))}')[:150]
     if User.objects.filter(username=username).exists(): username=f'{username}-{row.get("account_id",row.get("customer_id",1))}'
     user=User(username=username,email=email,first_name=(row.get('name') or '').split(' ')[0],last_name=' '.join((row.get('name') or '').split(' ')[1:]),phone=row.get('phone',''),role=role,is_active=True)
     legacy=row.get('password_hash','')
     if legacy.startswith('scrypt:'):
      try:
       spec,salt,digest=legacy.split('$'); _,n,r,p=spec.split(':'); user.password=f'werkzeug_scrypt${n}${r}${p}${salt}${digest}'
      except ValueError: user.set_unusable_password()
     else: user.set_unusable_password()
     user.save()
    users_by_legacy[(role,str(row.get('account_id',row.get('customer_id',''))))]=user
  artisan_users={}
  for row in accts:
   aid=row.get('artisan_id'); email=(row.get('email') or '').lower(); user=User.objects.filter(email=email).first()
   if aid and user: artisan_users[str(aid)]=user
   if not user or user.role!='artisan': continue
   legacy=artisan_map.get(str(aid),{})
   ArtisanProfile.objects.update_or_create(user=user,defaults={'display_name':row.get('name') or legacy.get('name') or user.get_full_name() or user.email,'skill':legacy.get('skill','General artisan'),'location':legacy.get('location','Warri'),'verified':bool(legacy.get('verified',False)),'verification_status':'approved' if legacy.get('verified') else row.get('status','pending').lower()})
  for row in artisans:
   aid=row.get('ID') or row.get('id'); email=(row.get('email') or '').lower()
   if email and User.objects.filter(email=email,role='artisan').exists(): continue
   # Directory-only artisan records remain discoverable only after a matching account is created.
  for row in requests:
   rid=row.get('request_id')
   if not rid or ServiceRequest.objects.filter(id=rid).exists(): continue
   customer=users_by_legacy.get(('customer',str(row.get('customer_id',''))))
   artisan_user=artisan_users.get(str(row.get('artisan_id','')))
   artisan=ArtisanProfile.objects.filter(user=artisan_user).first() if artisan_user else None
   if not customer:
    self.stderr.write(self.style.WARNING(f'Request {rid} has no reliable customer account link; skipped for manual reconciliation.')); continue
   raw_status=(row.get('status') or 'pending').strip().lower().replace(' ','_')
   status_map={'pending':'open','accepted':'accepted','declined':'cancelled','in_progress':'in_progress','completed':'completed','quote_submitted':'quoted','quote_accepted':'payment_pending'}
   req=ServiceRequest.objects.create(id=rid,customer=customer,artisan=artisan,service_name=row.get('service') or row.get('skill') or 'General service',description=row.get('description') or row.get('job_description') or 'Legacy request details unavailable.',location=row.get('location') or 'Warri',customer_phone=row.get('phone') or row.get('customer_phone',''),status=status_map.get(raw_status,'open'))
   amount=row.get('quote_amount')
   if amount and artisan:
    try:
     from apps.workflow.models import Quote
     Quote.objects.create(service_request=req,artisan=artisan,amount=amount,notes=row.get('quote_note') or row.get('qoute_note') or '',status='accepted' if str(row.get('quote_status','')).lower() in ('accepted','approved') else 'pending')
    except Exception as exc:
     self.stderr.write(self.style.WARNING(f'Request {rid}: quote not imported ({exc}).'))
  from django.db import connection
  from django.core.management.color import no_style
  reset_sql=connection.ops.sequence_reset_sql(no_style(), [ServiceRequest])
  with connection.cursor() as cursor:
   for statement in reset_sql: cursor.execute(statement)
  self.stdout.write(self.style.SUCCESS('Import finished. Review skipped records and legacy account mappings before launch.'))
