from django.db import models


# Custom queryset
class ExpenseReportQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='SUBMITTED')

    def approved(self):
        return self.filter(status='APPROVED')

    def rejected(self):
        return self.filter(status='REJECTED')

    def for_user(self, user):
        profile = getattr(user, 'expense_profile', None)
        if not profile:
            return self.none()

        if profile.role == 'FINANCE_ADMIN':
            return self.all()

        if profile.role == 'MANAGER':
            return self.filter(models.Q(assigned_manager=user) | models.Q(employee=user))

        return self.filter(employee=user)


# Custom manager
class ExpenseReportManager(models.Manager.from_queryset(ExpenseReportQuerySet)):
    def get_queryset(self):
        return super().get_queryset().select_related('employee', 'assigned_manager')
