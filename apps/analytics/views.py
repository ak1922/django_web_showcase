from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.management import call_command

from .forms import QuickSubscriptionEventForm
from .models import HistoricalMetricsSnapshot, SubscriptionEvent


# Main dash
@login_required
def analytics_dashboard(request):
    """
    Renders the SaaS Analytics Panel and handles async dashboard updates.
    """

    if not HistoricalMetricsSnapshot.objects.exists():
        call_command('calculate_metrics')

    latest_snapshot = HistoricalMetricsSnapshot.objects.order_by('-recorded_at').first()
    recent_events = SubscriptionEvent.objects.order_by('-timestamp')[:5]

    context = {
        'snapshot': latest_snapshot,
        'recent_events': recent_events,
        'form': QuickSubscriptionEventForm(),
    }

    if request.htmx:
        return render(request, 'analytics/partials/metrics_grid.html', context)

    return render(request, 'analytics/dashboard.html', context)


# Processing
@login_required
def trigger_recalculation(request):
    """
    HTMX Endpoint: Processes form submissions or forces recalculation,
    then returns the fresh template snapshot grid and recent event logs.
    """
    if request.method == 'POST':
        form = QuickSubscriptionEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()

        call_command('calculate_metrics')

    latest_snapshot = HistoricalMetricsSnapshot.objects.order_by('-recorded_at').first()
    recent_events = SubscriptionEvent.objects.order_by('-timestamp')[:5]

    return render(request, 'analytics/partials/metrics_grid.html', {
        'snapshot': latest_snapshot,
        'recent_events': recent_events,
        'form': QuickSubscriptionEventForm(),
    })
