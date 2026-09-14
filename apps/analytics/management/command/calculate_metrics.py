from django.core.management.base import BaseCommand
from django.db.models import Sum, Q

from apps.analytics.models import SubscriptionEvent, HistoricalMetricsSnapshot


# Aggregate command
class Command(BaseCommand):
    help = 'Aggregates subscription lifecycle logs into time-series data snapshots'

    def handle(self, *args, **options):
        self.stdout.write("Running background SaaS metrics calculation engine...")

        mrr_aggregation = SubscriptionEvent.objects.aggregate(total_mrr=Sum('mrr_impact'))
        current_mrr = mrr_aggregation['total_mrr'] or 0.00

        current_arr = current_mrr * 12

        active_count = SubscriptionEvent.objects.filter(
            ~Q(event_type=SubscriptionEvent.EventTypes.CHURN)
        ).values('user').distinct().count()

        total_events = SubscriptionEvent.objects.count()
        churn_events = SubscriptionEvent.objects.filter(
            event_type=SubscriptionEvent.EventTypes.CHURN
        ).count()

        current_churn_rate = 0.0
        if total_events > 0:
            current_churn_rate = round((churn_events / total_events) * 100, 2)

        snapshot = HistoricalMetricsSnapshot.objects.create(
            mrr=current_mrr,
            arr=current_arr,
            churn_rate=current_churn_rate,
            active_subscriptions_count=active_count
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated financial snapshot ID: {snapshot.id} "
                f"(MRR: ${current_mrr} | ARR: ${current_arr} | Churn: {current_churn_rate}%)"
            )
        )
