from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.contrib import messages
from .models import User
from .serializers import UserCreateSerializer


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # DEBUG LOGIN
        print("========== LOGIN DEBUG ==========")
        print("USERNAME RECIBIDO:", username)
        print("PASSWORD RECIBIDA:", password)
        print("USER EXISTE:", User.objects.filter(username=username).exists())

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("AUTH RESULT:", user)
        print("=================================")

        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/'))

        messages.error(request, 'Credenciales inválidas.')
        return render(
            request,
            self.template_name,
            {'username': username}
        )


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('core:dashboard')

        return render(
            request,
            self.template_name,
            {
                'errors': serializer.errors,
                'username': request.POST.get('username', ''),
            }
        )


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class TeamView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/team.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['team_members'] = User.objects.filter(
            is_active=True
        ).prefetch_related('roles').order_by('first_name')

        return ctx