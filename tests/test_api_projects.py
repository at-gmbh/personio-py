from .apitest_shared import *
from personio_py import Project


@skip_if_no_auth
def test_get_projects():
    create_test_project()
    projects = personio.get_projects()
    
    assert len(projects)>0

@skip_if_no_auth
def test_create_project(name: str = 'A project name', active: bool = False):
    """
    Test the creation of project records on the server.
    """
    project = create_test_project(name=name, active=active)
    
    assert project
    assert project.name == 'A project name'
    assert project.active == False
    
@skip_if_no_auth    
def test_delete_project_by_id():
    project = create_test_project(name="delete project by id", active=True)
    response = personio.delete_project(project.id_)
    
    assert response == True

@skip_if_no_auth
def test_delete_project_by_project_object():
    project = create_test_project(name="delete project by object", active=True)
    response = personio.delete_project(project)
    
    assert response == True


@skip_if_no_auth
def test_update_project():
    project = create_test_project(name="initial project", active=True)
    project.name = "updated project"
    updated_project = personio.update_project(project)

    assert updated_project.name == "updated project"

    project.active = False
    updated_project = personio.update_project(project)

    assert updated_project.active == False

# @skip_if_no_auth
# def test_update_project_no_exist():
#     # should raise an error
#     pass


def create_test_project(name: str = 'A project name', active: bool = False):
    p = Project(name=name, active=active)
    project = personio.create_project(p)
    
    return project