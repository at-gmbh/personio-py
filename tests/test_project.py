from datetime import datetime

from personio_py import Project

project_dict = {
    'id': 1,
    'type': 'Project',
    'attributes': {
        'name': 'Project name',
        'active': True,
        'created_at': '1835-12-01T13:15:00+00:00',
        'updated_at': '1836-12-01T13:15:00+00:00',
    }
}


def test_parse_project():
    project = Project.from_dict(project_dict)
    assert project
    assert project.name == 'Project name'
    assert project.active == True

def test_serialize_project():
    project = Project.from_dict(project_dict)
    d = project.to_dict()
    assert d == project_dict
