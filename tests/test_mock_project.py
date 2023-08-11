import re
from datetime import datetime

import responses

from personio_py import Project
from tests.test_mock import load_mock_data, mock_personio


@responses.activate
def test_create_project():
    mock_personio()
    mock_create_project()
    project = Project(name="project one",
                      active=True,
                      created_at=datetime.strptime("2023-03-28T16:24:36", "%Y-%m-%dT%H:%M:%S"),
                      updated_at=datetime.strptime("2023-03-28T16:24:36", "%Y-%m-%dT%H:%M:%S"))
    project.create()
    assert project.id


@responses.activate
def test_get_project():
    mock_projects()
    # configure personio & get absences for alan
    personio = mock_personio()
    projects = personio.get_projects()
    # validate
    assert len(projects) == 3
    selection = [a for a in projects if "conwik" in a.name.lower()]
    assert len(selection) == 1
    release = selection[0]  # an instance of Project
    assert release.active
    assert release.created_at == datetime(2019, 3, 1, 16, 0, 0)
    assert release.updated_at == datetime(2020, 3, 2, 16, 11, 35)
    assert release.id == 238751


@responses.activate
def test_update_projects():
    mock_projects()
    mock_update_project()
    personio = mock_personio()
    projects = personio.get_projects()
    projects_to_update = projects[0]
    projects_to_update.active = False
    updated_project = personio.update_project(projects_to_update)
    assert updated_project.active is False


@responses.activate
def test_delete_attendances():
    mock_projects()
    mock_delete_project()
    personio = mock_personio()
    projects = personio.get_projects()
    project_to_delete = projects[0]
    personio.delete_project(project_to_delete)


def mock_projects():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/attendances/projects?.*'),
        status=200,
        json=load_mock_data("get-project.json"),
        adding_headers={'Authorization': 'Bearer foo'})


def mock_create_project():
    responses.add(
        responses.POST,
        'https://api.personio.de/v1/company/attendances/projects',
        status=200,
        json=load_mock_data("create-project.json"),
        adding_headers={'Authorization': 'Bearer bar'})


def mock_update_project():
    responses.add(
        responses.PATCH,
        'https://api.personio.de/v1/company/attendances/projects/238751',
        status=200,
        json=load_mock_data("update-project.json"),
        adding_headers={'Authorization': 'Bearer bar'})


def mock_delete_project():
    responses.add(
        responses.DELETE,
        'https://api.personio.de/v1/company/attendances/projects/238751',
        status=200,
        json=load_mock_data("delete-project.json"),
        adding_headers={'Authorization': 'Bearer bar'})
