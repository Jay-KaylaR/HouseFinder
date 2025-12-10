from django.shortcuts import render,redirect
from django.contrib.auth import login , logout , authenticate  # django inbuilt operation that return true or false 
from django.contrib.auth.decorators import login_required # returns true or false -> gives permission to usage of view actions based
# off user login activies  # decorators : functions return other functions 
from django.contrib import messages
from django.contrib.auth.views  import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm,UserLoginForm,UserProfileForm


# Create your views here.
def register_view(request):
    # validate if the user is already authenticated 
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method  == 'POST': # user wants to register 
        form  = UserRegistrationForm(request.POST)
        # if user has filled in all required inputs 
        if form.is_valid():
            user = form.save()  ## submits our user to our db
            login(request,user)  ## calls the login action 
            messages.success(request, f'Welcome {user.username}! Your account has been successfully created!')
            return redirect('main:home')
    else:
        form = UserRegistrationForm() # default http method here is GET 
        
    return render(request, 'register.html' , {'form' : form})


def login_view(request):
    # validate if the user is already authenticated 
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method  == 'POST': # user wants to register 
        form  = UserLoginForm(request, data=request.POST)
        # if user has filled in all required inputs 
        if form.is_valid():
            # pick up entries for username and password 
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # djangomethod authenticate to authenticate and login my user 
            user = authenticate(request, username=username, password=password) # queries db looking for the user with metnioned credntiials 
            # is the user found not in db 
            if user is not None:
                login(request,user)
                messages.success(request, f'Welcome back {username}')
                return redirect('main:home')
    else:
        form = UserLoginForm(request) # default http method here is GET 
        
    return render(request, 'login.html' , {'form': form})




## logout -> check if our user is logged in - @Login_required
# if user is logged in then allow this action to run for the user 
@login_required
def logout_view(request):
    # use django inbuilt call 
    logout(request)
    messages.info(request, f"You have logged out!!")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile saved successfully")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'profile.html' , {'form' : form})


class CustomPasswordResetView(PasswordResetView):
    # interface change 
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done') # this will launch the confirm view


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    # interface change 
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete') # this will launch when password is update
