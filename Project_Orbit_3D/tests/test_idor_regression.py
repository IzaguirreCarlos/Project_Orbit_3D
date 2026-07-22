"""
Tests de regresión para las vulnerabilidades IDOR / broken access control
detectadas y corregidas en:
  - apps/tasks/views.py      (TaskListCreateView, AttachmentCreateView, TaskHistoryView)
  - apps/projects/views.py   (SprintListCreateView, SprintDetailView,
                               AssignmentDeleteView, project_stats)
  - apps/messaging/views.py  (MessageListCreateView)
  - apps/projects/web_views.py (ProjectDetailView, KanbanView, TimelineView)

Cada caso comprueba que un usuario ajeno al proyecto NO puede leer/crear/
modificar el recurso (fallo original), y que el usuario legítimo SÍ puede
seguir haciéndolo (para detectar sobre-restricciones futuras).
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from rest_framework import status

from apps.messaging.models import Message
from apps.projects.models import Assignment, Sprint
from apps.tasks.models import Attachment, Task, TaskHistory

pytestmark = pytest.mark.django_db


# ─── TaskListCreateView.perform_create ────────────────────────────────────

class TestTaskCreationScoping:
    def test_non_member_cannot_create_task_in_foreign_project(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        client = auth_client(owner_a)  # owner_a NO pertenece a project_b

        response = client.post(
            reverse('task-list'),
            {'project': str(project_b.id), 'title': 'Tarea intrusa'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Task.objects.filter(project=project_b).exists()

    def test_member_can_create_task_in_own_project(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        client = auth_client(owner_a)

        response = client.post(
            reverse('task-list'),
            {'project': str(project_a.id), 'title': 'Tarea legítima'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(project=project_a, title='Tarea legítima').exists()


# ─── AttachmentCreateView.perform_create ──────────────────────────────────

class TestAttachmentUploadScoping:
    def test_non_member_cannot_attach_file_to_foreign_task(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        task_b = Task.objects.create(project=project_b, creator=owner_b, title='Tarea B')
        client = auth_client(owner_a)

        upload = SimpleUploadedFile('evil.txt', b'contenido', content_type='text/plain')
        response = client.post(
            reverse('attachment-create', kwargs={'task_pk': task_b.id}),
            {'file': upload, 'original_name': 'evil.txt'},
            format='multipart',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Attachment.objects.filter(task=task_b).exists()

    def test_member_can_attach_file_to_own_task(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        task_a = Task.objects.create(project=project_a, creator=owner_a, title='Tarea A')
        client = auth_client(owner_a)

        upload = SimpleUploadedFile('doc.txt', b'contenido', content_type='text/plain')
        response = client.post(
            reverse('attachment-create', kwargs={'task_pk': task_a.id}),
            {'file': upload, 'original_name': 'doc.txt'},
            format='multipart',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Attachment.objects.filter(task=task_a).exists()


# ─── TaskHistoryView.get_queryset ──────────────────────────────────────────

class TestTaskHistoryScoping:
    def test_non_member_sees_no_history_for_foreign_task(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        task_b = Task.objects.create(project=project_b, creator=owner_b, title='Tarea B')
        TaskHistory.objects.create(
            task=task_b, user=owner_b, field_name='status',
            old_value='todo', new_value='in_progress',
        )
        client = auth_client(owner_a)

        response = client.get(reverse('task-history', kwargs={'task_pk': task_b.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_member_sees_history_for_own_task(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        task_a = Task.objects.create(project=project_a, creator=owner_a, title='Tarea A')
        TaskHistory.objects.create(
            task=task_a, user=owner_a, field_name='status',
            old_value='todo', new_value='in_progress',
        )
        client = auth_client(owner_a)

        response = client.get(reverse('task-history', kwargs={'task_pk': task_a.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


# ─── SprintListCreateView / SprintDetailView ──────────────────────────────

class TestSprintScoping:
    def test_non_member_cannot_list_sprints_of_foreign_project(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        Sprint.objects.create(
            project=project_b, name='Sprint B', start_date='2026-01-01', end_date='2026-01-14',
        )
        client = auth_client(owner_a)

        response = client.get(reverse('sprint-list', kwargs={'project_pk': project_b.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_non_member_cannot_create_sprint_in_foreign_project(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        client = auth_client(owner_a)

        response = client.post(
            reverse('sprint-list', kwargs={'project_pk': project_b.id}),
            {
                'project': str(project_b.id),
                'name': 'Sprint intruso',
                'start_date': '2026-01-01',
                'end_date': '2026-01-14',
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Sprint.objects.filter(project=project_b).exists()

    def test_non_member_cannot_view_or_delete_foreign_sprint(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        sprint_b = Sprint.objects.create(
            project=project_b, name='Sprint B', start_date='2026-01-01', end_date='2026-01-14',
        )
        client = auth_client(owner_a)
        url = reverse('sprint-detail', kwargs={'project_pk': project_b.id, 'pk': sprint_b.id})

        get_response = client.get(url)
        delete_response = client.delete(url)

        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND
        assert Sprint.objects.filter(pk=sprint_b.id).exists()

    def test_member_can_view_own_sprint(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        sprint_a = Sprint.objects.create(
            project=project_a, name='Sprint A', start_date='2026-01-01', end_date='2026-01-14',
        )
        client = auth_client(owner_a)
        url = reverse('sprint-detail', kwargs={'project_pk': project_a.id, 'pk': sprint_a.id})

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK


# ─── AssignmentDeleteView.get_queryset ─────────────────────────────────────

class TestAssignmentDeleteScoping:
    def test_pm_cannot_delete_assignment_via_mismatched_project_url(
        self, two_projects, make_user, auth_client
    ):
        """
        Antes del fix, el queryset era Assignment.objects.all() y solo se
        validaba el rol global de 'Project Manager', ignorando el project_pk
        de la URL: bastaba con conocer el UUID del assignment de OTRO
        proyecto para borrarlo.
        """
        project_a, project_b, owner_a, owner_b = two_projects
        pm = make_user(role_name='Project Manager')
        assignment_b = Assignment.objects.get(user=owner_b, project=project_b)
        client = auth_client(pm)

        # El PM intenta borrar el assignment de project_b usando la URL de project_a
        url = reverse(
            'assignment-delete',
            kwargs={'project_pk': project_a.id, 'pk': assignment_b.id},
        )
        response = client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Assignment.objects.filter(pk=assignment_b.id).exists()

    def test_pm_can_delete_assignment_with_matching_project_url(
        self, two_projects, make_user, auth_client
    ):
        project_a, project_b, owner_a, owner_b = two_projects
        pm = make_user(role_name='Project Manager')
        assignment_b = Assignment.objects.get(user=owner_b, project=project_b)
        client = auth_client(pm)

        url = reverse(
            'assignment-delete',
            kwargs={'project_pk': project_b.id, 'pk': assignment_b.id},
        )
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Assignment.objects.filter(pk=assignment_b.id).exists()


# ─── project_stats ──────────────────────────────────────────────────────

class TestProjectStatsScoping:
    def test_non_member_cannot_view_foreign_project_stats(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        client = auth_client(owner_a)

        response = client.get(reverse('project-stats', kwargs={'pk': project_b.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_member_can_view_own_project_stats(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        client = auth_client(owner_a)

        response = client.get(reverse('project-stats', kwargs={'pk': project_a.id}))

        assert response.status_code == status.HTTP_200_OK


# ─── MessageListCreateView.get_queryset (filtro por project_id) ───────────

class TestProjectMessagesScoping:
    def test_non_member_cannot_read_foreign_project_messages(self, two_projects, auth_client):
        project_a, project_b, owner_a, owner_b = two_projects
        Message.objects.create(sender=owner_b, project=project_b, content='Secreto de equipo B')
        client = auth_client(owner_a)

        response = client.get(reverse('message-list'), {'project_id': str(project_b.id)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_member_can_read_own_project_messages(self, two_projects, auth_client):
        project_a, _, owner_a, _ = two_projects
        Message.objects.create(sender=owner_a, project=project_a, content='Mensaje del equipo A')
        client = auth_client(owner_a)

        response = client.get(reverse('message-list'), {'project_id': str(project_a.id)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


# ─── Vistas web (HTML): ProjectDetailView / KanbanView / TimelineView ─────

class TestProjectWebViewsScoping:
    @pytest.mark.parametrize('url_name', ['projects:detail', 'projects:kanban', 'projects:timeline'])
    def test_non_member_gets_404_on_foreign_project_pages(self, two_projects, url_name):
        project_a, project_b, owner_a, owner_b = two_projects
        client = Client()
        client.force_login(owner_a)

        response = client.get(reverse(url_name, kwargs={'pk': project_b.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('url_name', ['projects:detail', 'projects:kanban', 'projects:timeline'])
    def test_member_gets_200_on_own_project_pages(self, two_projects, url_name):
        project_a, _, owner_a, _ = two_projects
        client = Client()
        client.force_login(owner_a)

        response = client.get(reverse(url_name, kwargs={'pk': project_a.id}))

        assert response.status_code == status.HTTP_200_OK
