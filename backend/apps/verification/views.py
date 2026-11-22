from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ArtisanVerification, VerificationAuditLog
from .permissions import IsArtisanOwner, IsWarriWorksAdmin
from .serializers import ArtisanVerificationSubmitSerializer, ArtisanVerificationStatusSerializer, AdminVerificationSerializer, VerificationAuditSerializer


def artisan_profile_for(user):
    try:
        return user.artisan_profile
    except Exception:
        raise ValidationError('An artisan profile is required before applying for verification.')

class ArtisanVerificationView(APIView):
    permission_classes = [IsArtisanOwner]

    def get(self, request):
        profile = artisan_profile_for(request.user)
        item = profile.verification_applications.first()
        if not item:
            return Response({'status': 'not_submitted'})
        return Response(ArtisanVerificationStatusSerializer(item).data)

    def post(self, request):
        profile = artisan_profile_for(request.user)
        previous = profile.verification_applications.first()
        if previous:
            if previous.status in [ArtisanVerification.Status.REJECTED, ArtisanVerification.Status.MORE_INFO]:
                raise ValidationError('A previous application exists. Use the resubmission endpoint instead.')
            raise ValidationError('You already have a verification application. Check its status before submitting another.')
        serializer = ArtisanVerificationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(artisan=profile, resubmission_count=(previous.resubmission_count + 1 if previous else 0))
        VerificationAuditLog.objects.create(verification=item, actor=request.user, action='application_submitted', new_status=item.status)
        profile.verification_status = item.status
        profile.verified = False
        profile.save(update_fields=['verification_status', 'verified'])
        return Response(ArtisanVerificationStatusSerializer(item).data, status=status.HTTP_201_CREATED)

class ArtisanVerificationResubmitView(APIView):
    permission_classes = [IsArtisanOwner]
    def post(self, request):
        profile = artisan_profile_for(request.user)
        previous = profile.verification_applications.first()
        if not previous or previous.status not in [ArtisanVerification.Status.REJECTED, ArtisanVerification.Status.MORE_INFO]:
            raise ValidationError('There is no application eligible for resubmission.')
        serializer = ArtisanVerificationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(artisan=profile, resubmission_count=previous.resubmission_count + 1)
        VerificationAuditLog.objects.create(verification=item, actor=request.user, action='application_resubmitted', previous_status=previous.status, new_status=item.status)
        profile.verification_status = item.status
        profile.verified = False
        profile.save(update_fields=['verification_status', 'verified'])
        return Response(ArtisanVerificationStatusSerializer(item).data, status=status.HTTP_201_CREATED)

class AdminVerificationListView(generics.ListAPIView):
    permission_classes = [IsWarriWorksAdmin]
    serializer_class = AdminVerificationSerializer
    queryset = ArtisanVerification.objects.select_related('artisan', 'artisan__user', 'reviewed_by').all()
    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get('status')
        return qs.filter(status=state) if state else qs

class AdminVerificationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsWarriWorksAdmin]
    serializer_class = AdminVerificationSerializer
    queryset = ArtisanVerification.objects.select_related('artisan', 'artisan__user').all()

class AdminVerificationReviewView(APIView):
    permission_classes = [IsWarriWorksAdmin]

    @transaction.atomic
    def post(self, request, pk):
        try:
            item = ArtisanVerification.objects.select_for_update().select_related('artisan').get(pk=pk)
        except ArtisanVerification.DoesNotExist:
            return Response({'detail': 'Verification application not found.'}, status=404)
        previous = item.status
        allowed = ['phone_confirmed', 'identity_document_reviewed', 'live_person_id_match_confirmed', 'professional_profile_reviewed', 'location_reviewed', 'reference_checked']
        for field in allowed:
            if field in request.data:
                if not isinstance(request.data[field], bool):
                    raise ValidationError({field: 'This field must be true or false.'})
                setattr(item, field, request.data[field])
        for field in ['admin_notes', 'artisan_message']:
            if field in request.data:
                setattr(item, field, str(request.data[field])[:5000])
        if item.status == ArtisanVerification.Status.PENDING:
            item.status = ArtisanVerification.Status.UNDER_REVIEW
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save()
        VerificationAuditLog.objects.create(verification=item, actor=request.user, action='review_updated', previous_status=previous, new_status=item.status, reason=item.admin_notes)
        item.artisan.verification_status = item.status
        item.artisan.save(update_fields=['verification_status'])
        return Response(AdminVerificationSerializer(item).data)

class AdminVerificationDecisionView(APIView):
    permission_classes = [IsWarriWorksAdmin]

    @transaction.atomic
    def post(self, request, pk, decision):
        try:
            item = ArtisanVerification.objects.select_for_update().select_related('artisan').get(pk=pk)
        except ArtisanVerification.DoesNotExist:
            return Response({'detail': 'Verification application not found.'}, status=404)
        previous = item.status
        reason = str(request.data.get('reason', '')).strip()[:5000]
        if decision == 'approve':
            if not item.all_required_checks_complete:
                raise ValidationError('Approval blocked: complete all six manual verification checks first.')
            item.status = ArtisanVerification.Status.APPROVED
            item.rejection_reason = ''
            item.artisan.verified = True
        elif decision == 'reject':
            if not reason:
                raise ValidationError({'reason': 'A rejection reason is required.'})
            item.status = ArtisanVerification.Status.REJECTED
            item.rejection_reason = reason
            item.artisan.verified = False
        elif decision == 'request-info':
            if not reason:
                raise ValidationError({'reason': 'Explain what additional information is required.'})
            item.status = ArtisanVerification.Status.MORE_INFO
            item.artisan_message = reason
            item.artisan.verified = False
        elif decision == 'suspend':
            if not reason:
                raise ValidationError({'reason': 'A suspension reason is required.'})
            item.status = ArtisanVerification.Status.SUSPENDED
            item.rejection_reason = reason
            item.artisan.verified = False
        else:
            raise ValidationError('Unsupported decision.')
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        if reason:
            item.admin_notes = reason
        item.save()
        item.artisan.verification_status = item.status
        item.artisan.save(update_fields=['verified', 'verification_status'])
        VerificationAuditLog.objects.create(verification=item, actor=request.user, action=decision, previous_status=previous, new_status=item.status, reason=reason)
        return Response(AdminVerificationSerializer(item).data)

class AdminVerificationAuditView(generics.ListAPIView):
    permission_classes = [IsWarriWorksAdmin]
    serializer_class = VerificationAuditSerializer
    def get_queryset(self):
        return VerificationAuditLog.objects.filter(verification_id=self.kwargs['pk']).select_related('actor')
