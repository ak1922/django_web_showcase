from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import ExpenseProfile, ExpenseReport


AppUser = get_user_model()


class ExpenseProfileInline(admin.TabularInline):

    model = ExpenseProfile
    can_delete = False
    verbose_name = _('Expense Application Personality')
    verbose_name_plural = _('Expense Application Personalities')
    fk_name = 'user'

try:
    admin.site.unregister(AppUser)
except admin.sites.NotRegistered:
    pass


@admin.register(AppUser)
class EnhancedAppUserAdmin(UserAdmin):

    inlines = [ExpenseProfileInline]
    list_display = (
        'username',
        'email',
        'get_corporate_role',
        'get_approval_limit',
        'is_staff'
    )

    @admin.display(description=_('Corporate Role'))
    def get_corporate_role(self, obj):
        return obj.expense_profile.get_role_display() if hasattr(obj, 'expense_profile') else None

    @admin.display(description=_('Approval Limit'))
    def get_approval_limit(self, obj):
        return f"${obj.expense_profile.approval_limit}" if hasattr(obj, 'expense_profile') else '$0.00'


@admin.register(ExpenseReport)
class ExpenseReportAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'employee',
        'amount',
        'status',
        'assigned_manager',
        'created_at'
    )
    list_filter = (
        'status',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'title',
        'description',
        'employee__username',
        'assigned_manager__username'
    )

    actions = ['bult_approve_reports']

    @admin.action(description=_('Bulk approve selected pending expense reports'))
    def bulk_approve_reports(self, request, queryset):
        updated_count = 0

        for report in queryset:
            if report.status == 'SUBMITTED':
                report.status = 'APPROVED'

                try:
                    report.full_clean()
                    report.save()
                    updated_count += 1
                except ValidationError as e:
                    self.message_user(
                        request,
                        f"Skipped '{report.title}': {e.messages[0]}",
                        messages.ERROR
                    )

        if updated_count:
            self.message_user(
                request,
                f"Successfully approved {updated_count} corporate expense reports.",
                messages.SUCCESS
            )
