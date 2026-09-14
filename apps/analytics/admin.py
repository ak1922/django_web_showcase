from django.contrib import admin
from django.core.management import call_command
from django.contrib import messages

from .models import SubscriptionEvent, HistoricalMetricsSnapshot


@admin.register(SubscriptionEvent)
class SubscriptionEventAdmin(admin.ModelAdmin):
    """
    Ledger view tracking the raw entry stream of incoming subscription changes.
    """

    list_display = (
        'user',
        'event_type',
        'get_mrr_impact',
        'timestamp'
    )

    list_filter = (
        'event_type',
        'timestamp'
    )

    search_fields = (
        'user__username',
        'event_type'
    )

    ordering = ('-timestamp',)

    @admin.display(description='MRR Impact')
    def get_mrr_impact(self, obj):
        if obj.mrr_impact >= 0:
            return f'+${obj.mrr_impact}'
        return f'-${abs(obj.mrr_impact)}'


@admin.register(HistoricalMetricsSnapshot)
class HistoricalMetricsSnapshotAdmin(admin.ModelAdmin):
    """
    Time-series display showing cached business aggregates calculated by cron routines.
    """

    list_display = (
        'get_date',
        'get_mrr',
        'get_arr',
        'get_churn_rate',
        'active_subscriptions_count'
    )

    ordering = ('-recorded_at',)

    actions = ['trigger_manual_metrics_calculation']

    @admin.display(description='Snapshot Date')
    def get_date(self, obj):
        return obj.recorded_at.strftime('%Y-%m-%d %H:%M')

    @admin.display(description='MRR')
    def get_mrr(self, obj):
        return f'${obj.mrr:,}'

    @admin.display(description='ARR')
    def get_arr(self, obj):
        return f'${obj.arr:,}'

    @admin.display(description='Churn Rate')
    def get_churn_rate(self, obj):
        return f'{obj.churn_rate}%'

    @admin.action(description='Force execute background cron logic to compile fresh snapshot')
    def trigger_manual_metrics_calculation(self, request, queryset):
        try:
            call_command('calculate_metrics')
            self.message_user(
                request,
                'Metrics engine executed. Fresh historical snapshot generated successfully.',
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(request, f'Engine Failure: {e}', messages.ERROR)
