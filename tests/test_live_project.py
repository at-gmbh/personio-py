from personio_py import Project
from tests.connection import get_skipif, personio

skip_if_no_auth = get_skipif()


@skip_if_no_auth
def test_get_projects():
    create_test_project(name="test project")
    projects = personio.get_projects()

    assert len(projects) > 0
    assert projects[-1].name == "test project"
    assert projects[-1].active is False
    personio.delete_project(projects[-1])


@skip_if_no_auth
def test_update_project():
    """
    Test the update of project records on the server.
    """
    project = create_test_project(name="initial project", active=True)
    project.name = "updated project"
    updated_project = project.update()

    assert updated_project.name == "updated project"

    project.active = False
    updated_project = project.update()

    assert updated_project.active is False

    project.delete()


@skip_if_no_auth
def test_update_project_from_client():
    """
    Test the update of project records on the server.
    """
    project = create_test_project(name="initial project", active=True)
    project.name = "updated project"
    updated_project = personio.update_project(project)

    assert updated_project.name == "updated project"

    project.active = False
    updated_project = personio.update_project(project)

    assert updated_project.active is False

    personio.delete_project(project)


@skip_if_no_auth
def test_delete_project_by_id():
    project = create_test_project(name="delete project by id", active=True)
    response = personio.delete_project(project.id)

    assert response.status_code == 204


@skip_if_no_auth
def test_delete_project_by_project_object():
    project = create_test_project(name="delete project by object", active=True)
    response = personio.delete_project(project)

    assert response.status_code == 204


def create_test_project(name: str = 'project name', active: str = False):
    p = Project(name=name, active=active)
    project = personio.create_project(p)

    return project
