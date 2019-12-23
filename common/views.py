from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import authenticate
from common.forms import ProfileCreationForm
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from common.models import UserProfile
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django import forms
from django.contrib.auth.models import User


class RegisterView(FormView):

    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        login(self.request, authenticate(
            username=username, password=raw_password))
        return super(RegisterView, self).form_valid(form)


class CreateUserProfile(FormView):

    form_class = ProfileCreationForm
    template_name = 'profile-create.html'
    success_url = reverse_lazy('common:index')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return HttpResponseRedirect(reverse_lazy('common:login'))
        return super(CreateUserProfile, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return super(CreateUserProfile, self).form_valid(form)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')
        
def index(request):
    context = {}

    if request.method == 'POST':

        if 'btnSignIn' in request.POST:
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                # Create a new user object but avoid saving it yet
                new_user = user_form.save(commit=False)
                # Set the chosen password
                new_user.set_password(user_form.cleaned_data['password'])
                # Save the User object
                new_user.save()
                # profile = Profile.objects.create(user=new_user)
                login(request, authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password']))
                return HttpResponseRedirect(reverse_lazy('common:profile-create'))
            else:
                return render(request, 'login_error.html')
                
        else:
            form = AuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                auth.login(request, form.get_user())
            else:
                return render(request, 'login_error.html')
        return HttpResponseRedirect(reverse_lazy('common:index'))
    else:
        context['form'] = AuthenticationForm()

    if request.user.is_authenticated:
        context['username'] = request.user.username
        try:
            context['age'] = UserProfile.objects.get(user=request.user).age
        except:
            context['age'] = 0
        
        context['email'] = request.user.email
        try:
            context['github_url'] = SocialAccount.objects.get(
                provider='github', user=request.user).extra_data['html_url']
        except:
            context['github_url'] = ''
    return render(request, 'index2.html', context)

