from flask import url_for, jsonify

from an_app import elastic_client


def test_indice_create(app_with_db):
    response = app_with_db.get(
        url_for('create_indice'),
        json={}
    )
    assert response.status_code == 201
    response = app_with_db.get(
        url_for('create_indice'),
        json={}
    )
    assert response.status_code == 400


def test_indeice_delete(app_with_db):
    app_with_db.get(
        url_for('create_indice'),
        json={}
    )
    response = app_with_db.get(
        url_for('delete_indice'),
        json={}
    )
    assert response.status_code == 204
    response = app_with_db.get(
        url_for('delete_indice'),
        json={}
    )
    assert response.status_code == 404
    app_with_db.get(
        url_for('create_indice'),
        json={}
    )


def test_indice_fill_without_data(app_with_db):
    response = app_with_db.get(
        url_for('fill_indice'),
        json={}
    )
    assert response.status_code == 400
    assert response.json == {'message': 'База данных пуста'}


def test_indice_fill(app_with_data):
    assert elastic_client.indices.exists(index="files") == True
    response = app_with_data.get(
        url_for('fill_indice'),
        json={}
    )
    assert response.status_code == 201
    elastic_client.indices.refresh(index="files")
    r = elastic_client.search(index="files", query={"match_all":{}})
    assert len(r['hits']['hits']) == 2


def test_search(app_with_data):
    response = app_with_data.post(
        url_for('search'),
        json={}
    )
    assert response.status_code == 400 and response.json == {'message': 'Отсутствует тело запроса'}
    response = app_with_data.post(
        url_for('search'),
        json={'id': 1}
    )
    assert response.status_code == 400 and response.json == {'message': '"text" является обязательным полем'}
    response = app_with_data.post(
        url_for('search'),
        json={'text': 'gibberish'}
    )
    assert response.status_code == 404 and response.json == {'message': 'Ничего не найдено'}
    app_with_data.get(
        url_for('fill_indice'),
        json={}
    )
    elastic_client.indices.refresh(index="files")
    response = app_with_data.post(
        url_for('search'),
        json={'text': 'test1'}
    )
    assert response.status_code == 200 and len(response.json['result']) == 1 and response.json['result'][0]['id'] == 1
    response = app_with_data.post(
        url_for('search'),
        json={'text': 'test2'}
    )
    assert response.status_code == 200 and len(response.json['result']) == 1 and response.json['result'][0]['id'] == 2


def test_delete(app_with_data):
    response = app_with_data.delete(
        url_for('file_del', pk=1),
        json={}
    )
    assert response.status_code == 204
    elastic_client.indices.refresh(index="files")
    response = app_with_data.delete(
        url_for('file_del', pk=1),
        json={}
    )
    assert response.status_code == 404 and response.json == {'message': 'Такого id в базе нет'}