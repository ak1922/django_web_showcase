from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import ExpenseProfile

AppUser = get_user_model()


@receiver(post_save, sender=AppUser)
def create_user_expense_profile(sender, instance, created, **kwargs):
    """
    Automatically creates an Expense Profile whenever a new AppUser is registered.
    """

    if created:
        ExpenseProfile.objects.create(user=instance)
