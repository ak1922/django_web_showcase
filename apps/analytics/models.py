from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SubscriptionEvent(models.Model):
    class EventTypes(models.TextChoices):
        NEW = 'NEW', _('New Subscription')
        UPGRADE = 'UPGRADE', _('Plan Upgrade')
        DOWNGRADE = 'DOWNGRADE', _('Plan Downgrade')
        CHURN = 'CHURN', _('Cancellation')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription_history'
    )
    event_type = models.CharField(
        max_length=15,
        choices=EventTypes.choices,
    )
    mrr_impact = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Monthly value variance (+/-)')
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f'{self.user.username} - {self.event_type} (${self.mrr_impact})'


class HistoricalMetricsSnapshot(models.Model):

    recorded_at = models.DateTimeField(
        unique=True,
        auto_now_add=True
    )
    mrr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Monthly Recurring Revenue')
    )
    arr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Annual Recurring Revenue')
    )
    churn_rate = models.FloatField(
        default=0.0,
        help_text=_('Percentage churn value')
    )
    active_subscriptions_count = models.IntegerField(default=0)

    class Meta:
        ordering = ('recorded_at',)

    def __str__(self):
        return f'Snapshot {self.recorded_at.strftime('%Y-%m-%d')} - MRR: ${self.mrr}'
