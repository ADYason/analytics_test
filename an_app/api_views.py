from flask import jsonify, request
from http import HTTPStatus

from . import app, elastic_client, db
from .models import FileModel
from .error_handlers import InvalidAPIUsage
from .mapping import MAPPING_FOR_INDEX
from .utils import test_es
from elasticsearch.exceptions import (NotFoundError,
                                      RequestError)


ec = elastic_client


@app.route('/api/create_indice', methods=['GET'])
def create_indice():
    if not test_es():
        raise InvalidAPIUsage('API эластика не подключено')
    try:
        ec.indices.create(index='files', mappings=MAPPING_FOR_INDEX)
    except RequestError:
        raise InvalidAPIUsage('Индекс уже создан')
    return jsonify({
        'status': 'success'
    }), HTTPStatus.CREATED


@app.route('/api/delete_indice', methods=['GET'])
def delete_indice():
    if not test_es():
        raise InvalidAPIUsage('API эластика не подключено')
    try:
        ec.indices.delete(index='files')
    except NotFoundError:
        raise InvalidAPIUsage('Индекса не существует', HTTPStatus.NOT_FOUND)
    return jsonify({
        'status': 'success'
    }), HTTPStatus.NO_CONTENT


@app.route('/api/fill_indice', methods=['GET'])
def fill_indice():
    if not test_es():
        raise InvalidAPIUsage('API эластика не подключено')
    if not ec.indices.exists(index="files"):
        raise InvalidAPIUsage('Такого индекса не существует')
    files = FileModel.query.all()
    if not files:
        raise InvalidAPIUsage('База данных пуста')
    for file in files:
        new_file = {
            'id': file.id,
            'text': file.text
        }
        ec.index(index='files', document=new_file)
    return jsonify({
        'status': 'success'
    }), HTTPStatus.CREATED


@app.route('/api/search', methods=['POST'])
def search():
    if not test_es():
        raise InvalidAPIUsage('API эластика не подключено')
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'text' not in data:
        raise InvalidAPIUsage('"text" является обязательным полем')
    query = {"match": {"text": data['text']}}
    src = ec.search(index='files', query=query, size=20)
    hits = src['hits']['hits']
    if hits == []:
        return jsonify({
            'message': 'Ничего не найдено'
        }), HTTPStatus.NOT_FOUND
    pks = []
    for hit in hits:
        pks.append(hit['_source']['id'])
    query = FileModel.query.filter(
        FileModel.id.in_(pks)).order_by(
            FileModel.created_date).all()
    result = []
    if query is not None:
        for file in query:
            result.append(file.to_dict())
    return jsonify({
        'result': result
    }), HTTPStatus.OK


@app.route('/api/file/<int:pk>', methods=['DELETE'])  # type: ignore
def file_del(pk):
    if not test_es():
        raise InvalidAPIUsage('API эластика не подключено')
    query = {"match": {"id": pk}}
    src = ec.search(index='files', query=query)
    hits = src['hits']['hits']
    if hits == []:
        raise InvalidAPIUsage('Такого id в эластике нет', HTTPStatus.NOT_FOUND)
    del_id = hits[0]['_id']
    ec.delete(index='files', id=del_id)
    file = FileModel.query.filter(FileModel.id == pk).first()
    if file is None:
        raise InvalidAPIUsage('Такого id в базе нет', HTTPStatus.NOT_FOUND)
    db.session.delete(file)
    db.session.commit()
    return {}, HTTPStatus.NO_CONTENT
