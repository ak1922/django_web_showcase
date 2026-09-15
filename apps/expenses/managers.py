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
        """
        Locks down record visibilities based strictly on the request user's corporate profile.
        """

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
        # Keeps your N+1 optimization active uniformly across all chains
        return super().get_queryset().select_related('employee', 'assigned_manager')
