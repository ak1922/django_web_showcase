from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import UserRegistrationForm


# Welcome page
def welcome(request):
    """
    PUBLIC LANDING PAGE: No login required.
    Introduces the portfolio, architecture, and technology stack.
    If already logged in, seamlessly forward them to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'dashboard/welcome.html')


# Main index view
@login_required
def index(request):
    """
    Renders the core ecosystem landing page from the root templates folder.
    """
    return render(request, 'index.html')


# Registration
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            new_user = form.save()
            messages.success(
                request,
                f'Account successfully provisioned!. Welcome {new_user.username}'
            )

            # Login the user to the main dashboard
            login(request, new_user)
            return redirect('dashboard:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'dashboard/register.html', {
        'form': form
    })
