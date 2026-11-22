from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.routers import DefaultRouter
from django.middleware.csrf import get_token
from apps.marketplace.views import ArtisanViewSet, CategoryViewSet, MyArtisanProfileView
from apps.workflow.views import ServiceRequestViewSet, QuoteViewSet, ReviewViewSet
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({
        'detail': 'CSRF cookie set',
        'csrfToken': get_token(request),
    })
router=DefaultRouter(); router.register('artisans',ArtisanViewSet,basename='artisan'); router.register('categories',CategoryViewSet,basename='category'); router.register('requests',ServiceRequestViewSet,basename='request'); router.register('quotes',QuoteViewSet,basename='quote'); router.register('reviews',ReviewViewSet,basename='review')
urlpatterns=[path('admin/',admin.site.urls),path('api/csrf/',csrf),path('api/auth/',include('apps.accounts.urls')),path('api/verification/',include('apps.verification.urls')),path('api/artisans/me/',MyArtisanProfileView.as_view(),name='my-artisan-profile'),path('api/',include(router.urls))]
from apps.workflow.payment_views import PaymentInitializeView, PaymentVerifyView, PaymentDetailView, paystack_webhook
urlpatterns += [
 path('api/payments/initialize/', PaymentInitializeView.as_view(), name='payment-initialize'),
 path('api/payments/verify/', PaymentVerifyView.as_view(), name='payment-verify'),
 path('api/payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
 path('api/webhooks/paystack/', paystack_webhook, name='paystack-webhook'),
]
from apps.workflow.payment_views import MilestoneEvidenceView, MilestoneApproveView
urlpatterns += [
 path('api/milestones/<int:pk>/submit-evidence/', MilestoneEvidenceView.as_view(), name='milestone-evidence'),
 path('api/milestones/<int:pk>/approve/', MilestoneApproveView.as_view(), name='milestone-approve'),
]
