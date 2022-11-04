from . import db


class FileModel(db.Model):  # type: ignore
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    id = db.Column(db.Integer, primary_key=True)
    rubrics = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            rubrics=self.rubrics,
            text=self.text.rstrip(),
            created_date=self.created_date
        )
