import csv
from datetime import datetime

import click

from . import app, db
from .models import FileModel

FORMAT = '%Y-%m-%d %H:%M:%S'


@app.cli.command('load_files')
def load_files_command():
    """Функция загрузки файлов(постов) в базу данных."""
    with open('posts.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        counter = 0
        for row in reader:
            row['created_date'] = datetime.strptime(
                row['created_date'], FORMAT)
            row['text'] = row['text'].rstrip()
            opinion = FileModel(**row)
            db.session.add(opinion)
            db.session.commit()
            counter += 1
    click.echo(f'Загружено файлов: {counter}')
