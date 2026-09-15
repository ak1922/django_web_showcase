from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .managers import ExpenseReportManager


class ExpenseProfile(models.Model):
    class RoleChoices(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', _('Standard Staff')
        MANAGER = 'MANAGER', _('Team Approver')
        FINANCE_ADMIN = 'FINANCE_ADMIN', _('Treasury Auditor')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_profile'
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.EMPLOYEE
    )
    approval_limit = models.DecimalField(
        default=500.00,
        max_digits=10,
        decimal_places=2
    )
    report_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


class ExpenseReport(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Pending Manager Approval')
        APPROVED = 'APPROVED', _('Approved by Payout')
        REJECTED = 'REJECTED', _('Returned/Rejected')

    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_expenses'
    )
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='previous_reviews'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseReportManager()

    class Meta:
        ordering = ('created_at',)
        permissions = [
            ('can_audit_all_expenses', 'Can view and audit every corporate pipeline'),
        ]

    def __str__(self):
        return f'{self.title} - ${self.amount} ({self.status})'

    def clean(self):
        super().clean()
        if self.amount <= 0:
            raise ValidationError(
                {'amount': _('Expense amount must be greater than zero.')}
            )

        if self.status == 'APPROVED' and self.assigned_manager:
            profile = getattr(self.assigned_manager, 'expense_profile', None)

            if profile and profile.role == 'MANAGER' and self.amount > profile.approval_limit:
                raise ValidationError(
                    f'Selected manager ({self.assigned_manager.username}) lacks '
                    f'clearance to approve amounts over ${profile.approval_limit}.'
                )
