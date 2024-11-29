import re
from datetime import datetime

import responses

from personio_py import Project
from tests.mock_data import (
    json_dict_project_rms, json_dict_project_update, json_dict_project_delete,
    json_dict_project_create
)
from tests.test_mock_api import compare_labeled_attributes, mock_personio


@responses.activate
def test_create_project():
    mock_create_project()
    personio = mock_personio()

    project = Project(
        client=personio,
        name="project one",
        active=True,
        created_at=datetime.strptime("2023-03-28T16:24:36", "%Y-%m-%dT%H:%M:%S"),
        updated_at=datetime.strptime("2023-03-28T16:24:36", "%Y-%m-%dT%H:%M:%S")
        )
    project.create()
    assert project.id_

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
    release = selection[0] # an instance of Project
    assert release.active == True
    assert release.created_at == datetime(2019,3,1,16,0,0)
    assert release.updated_at == datetime(2020,3,2,16,11,35)
    assert release.id_ == 238751
    # validate serialization
    source_dict = json_dict_project_rms['data'][0]
    target_dict = release.to_dict()
    compare_labeled_attributes(source_dict, target_dict)

@responses.activate
def test_update_projects():
    mock_projects()
    mock_update_project()
    personio = mock_personio()
    projects = personio.get_projects()
    projects_to_update = projects[0]
    projects_to_update.active = False
    updated_project = personio.update_project(projects_to_update)
    assert updated_project.active == False


@responses.activate
def test_delete_attendances():
    mock_projects()
    mock_delete_project()
    personio = mock_personio()
    projects = personio.get_projects()
    project_to_delete = projects[0]
    response = personio.delete_project(project_to_delete)
    assert response.status_code == 204

def mock_projects():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances/projects?.*'),
        status=200, json=json_dict_project_rms, adding_headers={'Authorization': 'Bearer foo'})

def mock_create_project():
    responses.add(
        responses.POST,  'https://api.personio.de/v1/company/attendances/projects',
        status=200, json=json_dict_project_create, adding_headers={'Authorization': 'Bearer bar'})

def mock_update_project():
    responses.add(
        responses.PATCH,  'https://api.personio.de/v1/company/attendances/projects/238751',
        status=200, json=json_dict_project_update, adding_headers={'Authorization': 'Bearer bar'})

def mock_delete_project():
    responses.add(
        responses.DELETE,  'https://api.personio.de/v1/company/attendances/projects/238751',
        status=204, adding_headers={'Authorization': 'Bearer bar'})
