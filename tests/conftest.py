import datetime as dt
import pytest
from sqlalchemy import delete
from an_app import app, db, elastic_client
from an_app.models import FileModel

@pytest.fixture(scope='session')
def flask_app():
    client = app.test_client()
    ctx = app.test_request_context()
    ctx.push()
    ec = elastic_client
    yield client
    ctx.pop()
    ec.indices.delete(index='files')


@pytest.fixture(scope='session')
def app_with_db(flask_app):
    db.create_all()
    yield flask_app
    db.session.commit()
    db.drop_all()


@pytest.fixture
def app_with_data(app_with_db):
    file1 = FileModel()
    file1.created_date = dt.datetime.now()
    file1.text = 'test1'
    file1.rubrics = 'test1'
    file2 = FileModel()
    file2.created_date = dt.datetime.now()
    file2.text = 'test2'
    file2.rubrics = 'test2'
    db.session.add(file1)
    db.session.add(file2)
    db.session.commit()
    yield app_with_db
    db.session.delete(file1)
    db.session.delete(file2)
    db.session.commit()
