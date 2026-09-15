from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ExpenseReport, ExpenseProfile
from .forms import ExpenseReportForm


# Main dashboard
@login_required
def expense_dashboard(request):

    profile, created = ExpenseProfile.objects.get_or_create(user=request.user)
    reports = ExpenseReport.objects.for_user(request.user)
    pending_count = reports.pending().count()

    return render(request, 'expenses/dashboard.html', {
        'reports': reports,
        'profile': profile,
        'pending_count': pending_count
    })


# Create
@login_required
def create_expense(request):

    if request.method == 'POST':
        form = ExpenseReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.employee = request.user
            report.status = 'SUBMITTED'
            report.save()
            messages.success(request, f"Expense report '{report.title}' successfully submitted.")
            return redirect('expenses:dashboard')

    else:
        form = ExpenseReportForm()

    return render(request, 'expenses/expense_form.html', {
        'form': form
    })


# Process reports
@login_required
def process_approval(request, pk, action):

    accessible_reports = ExpenseReport.objects.for_user(request.user)
    report = get_object_or_404(accessible_reports, pk=pk)

    profile = getattr(request.user, 'expense_profile', None)
    is_assigned_manager = report.assigned_manager == request.user
    is_auditor = profile and profile.role == 'FINANCE_ADMIN'

    # Security Validation Gate
    if not (is_assigned_manager or is_auditor):
        raise PermissionDenied(_('You are not authorized to alter the workflow state of this record.'))

    if report.status != 'SUBMITTED':
        messages.warning(request, _('This transaction file has already been finalized.'))
        return redirect('expenses:dashboard')

    if action == 'approve':
        report.status = 'APPROVED'
        try:
            report.full_clean()
            report.save()
            messages.success(request, _(f'Successfully approved report: {report.title}'))
        except ValidationError as e:
            messages.error(request, _(f"Approval Denied: {e.messages[0] if isinstance(e.messages, list) else e}"))
    elif action == 'reject':
        report.status = 'REJECTED'
        report.save()
        messages.warning(request, _(f"Report '{report.title}' has been rejected and returned to draft status."))

    return redirect('expenses:dashboard')
