"""
Fixtures compartidas para los tests de regresión de IDOR.
"""
import itertools

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User
from apps.projects.models import Assignment, Project

_counter = itertools.count(1)


@pytest.fixture
def make_user(db):
    """Crea un usuario válido, opcionalmente con un rol organizacional."""

    def _make(role_name=None, **kwargs):
        n = next(_counter)
        email = kwargs.pop('email', f'user{n}@example.com')
        password = kwargs.pop('password', 'RegressionTest!123')
        first_name = kwargs.pop('first_name', 'User')
        last_name = kwargs.pop('last_name', str(n))
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **kwargs,
        )
        if role_name:
            role, _ = Role.objects.get_or_create(name=role_name)
            user.roles.add(role)
        return user

    return _make


@pytest.fixture
def auth_client():
    """Devuelve un APIClient autenticado vía JWT para el usuario dado."""

    def _client(user):
        client = APIClient()
        token = RefreshToken.for_user(user).access_token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return client

    return _client


@pytest.fixture
def two_projects(make_user):
    """
    Dos proyectos totalmente independientes, cada uno con su propio dueño/miembro.
    `owner_a` / `owner_b` NO tienen ninguna relación con el proyecto del otro:
    son el par "víctima / atacante" que usan los tests de IDOR.
    """
    owner_a = make_user()
    owner_b = make_user()
    project_a = Project.objects.create(name='Project A', owner=owner_a)
    project_b = Project.objects.create(name='Project B', owner=owner_b)
    Assignment.objects.create(user=owner_a, project=project_a)
    Assignment.objects.create(user=owner_b, project=project_b)
    return project_a, project_b, owner_a, owner_b
