from django.urls import path
from .views import (ArtisanVerificationView, ArtisanVerificationResubmitView,
    AdminVerificationListView, AdminVerificationDetailView,
    AdminVerificationReviewView, AdminVerificationDecisionView,
    AdminVerificationAuditView)

urlpatterns = [
    path('artisan/', ArtisanVerificationView.as_view(), name='artisan-verification'),
    path('artisan/resubmit/', ArtisanVerificationResubmitView.as_view(), name='artisan-verification-resubmit'),
    path('admin/', AdminVerificationListView.as_view(), name='admin-verification-list'),
    path('admin/<int:pk>/', AdminVerificationDetailView.as_view(), name='admin-verification-detail'),
    path('admin/<int:pk>/review/', AdminVerificationReviewView.as_view(), name='admin-verification-review'),
    path('admin/<int:pk>/<str:decision>/', AdminVerificationDecisionView.as_view(), name='admin-verification-decision'),
    path('admin/<int:pk>/audit/', AdminVerificationAuditView.as_view(), name='admin-verification-audit'),
]
