
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import ServiceRequest, Quote, Review
from apps.marketplace.models import ArtisanProfile

DEFAULT_SCHEDULE = [
    {
        'name': 'Initial mobilisation',
        'percentage': 70,
        'release_condition': 'Successful payment verification and verified artisan payout account.'
    },
    {
        'name': 'Verified progress',
        'percentage': 20,
        'release_condition': 'Agreed progress evidence reviewed and approved.'
    },
    {
        'name': 'Completion retention',
        'percentage': 10,
        'release_condition': 'Customer completion approval and dispute checks.'
    }
]


class RequestSerializer(serializers.ModelSerializer):
    artisan = serializers.PrimaryKeyRelatedField(
        queryset=ArtisanProfile.objects.filter(
            verified=True,
            is_available=True
        ),
        required=False,
        allow_null=True
    )

    customer_email = serializers.EmailField(
        source='customer.email',
        read_only=True
    )

    artisan_name = serializers.CharField(
        source='artisan.display_name',
        read_only=True,
        default=None
    )

    class Meta:
        model = ServiceRequest
        fields = [
            'id',
            'customer_email',
            'artisan',
            'artisan_name',
            'category',
            'service_name',
            'description',
            'location',
            'customer_phone',
            'preferred_date',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'customer_email',
            'artisan_name',
            'status',
            'created_at',
        ]


class QuoteSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )

    payment_schedule = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

    cost_breakdown = serializers.DictField(required=True)

    schedule_request_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )

    class Meta:
        model = Quote
        fields = [
            'id',
            'service_request',
            'artisan',
            'amount',
            'notes',
            'cost_breakdown',
            'payment_schedule',
            'schedule_request_reason',
            'schedule_approved',
            'schedule_review_reason',
            'status',
            'version',
            'created_at'
        ]
        read_only_fields = [
            'artisan',
            'schedule_approved',
            'schedule_review_reason',
            'status',
            'version',
            'created_at'
        ]

    def validate(self, attrs):
        schedule = attrs.get('payment_schedule') or DEFAULT_SCHEDULE

        try:
            percentages = [
                int(x['percentage']) for x in schedule
            ]

            if (
                not schedule
                or sum(percentages) != 100
                or any(x <= 0 or x > 100 for x in percentages)
                or percentages[0] > 80
                or percentages[-1] < 10
            ):
                raise ValueError()

            for item in schedule:
                if (
                    not item.get('name')
                    or not item.get('release_condition')
                ):
                    raise ValueError()

        except (KeyError, TypeError, ValueError):
            raise serializers.ValidationError({
                'payment_schedule': (
                    'Provide named milestones with positive whole-number '
                    'percentages totalling exactly 100 and a release '
                    'condition for each.'
                )
            })

        if (
            percentages[0] > 70
            and not attrs.get('schedule_request_reason', '').strip()
        ):
            raise serializers.ValidationError({
                'schedule_request_reason': (
                    'Explain why the project requires higher initial mobilisation.'
                )
            })

        breakdown = attrs.get('cost_breakdown') or {}

        required_keys = {
            'materials',
            'labour',
            'logistics',
            'other'
        }

        if not required_keys.issubset(breakdown):
            raise serializers.ValidationError({
                'cost_breakdown': (
                    'Provide materials, labour, logistics and other cost values.'
                )
            })

        try:
            costs = [
                Decimal(str(breakdown[key]))
                for key in required_keys
            ]

            if (
                any(value < 0 for value in costs)
                or sum(costs) != attrs.get('amount')
            ):
                raise ValueError()

        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError({
                'cost_breakdown': (
                    'Cost components must be non-negative and add up '
                    'exactly to the quotation amount.'
                )
            })

        attrs['payment_schedule'] = schedule
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id',
            'service_request',
            'customer',
            'artisan',
            'rating',
            'comment',
            'created_at'
        ]
        read_only_fields = [
            'customer',
            'artisan',
            'created_at'
        ]
