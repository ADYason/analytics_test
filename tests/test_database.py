from sqlalchemy import inspect

from an_app.models import FileModel


def test_fields(app_with_db):
    inspector = inspect(FileModel)
    fields = [column.name for column in inspector.columns]
    assert all(field in fields for field in ['id', 'rubrics', 'text', 'created_date']), (
        'В модели не найдены все необходимые поля. '
        'Проверьте модель: в ней должны быть поля id, rubrics, text и created_date.'
    )
