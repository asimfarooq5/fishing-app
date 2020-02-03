import os
import uuid

from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField
from wtforms.validators import ValidationError

from models import db, Score

ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif', 'jpeg'}


def picture_validation(form, field):
    if field.data:
        filename = field.data.filename
        extension = filename.split('.')[-1]

        if extension.lower() not in ALLOWED_EXTENSIONS:
            raise ValidationError("Must be Image")
        filename = str(uuid.uuid4()) + "." + extension
        field.data.save(os.path.join('./images', filename))
        field.data = filename
        return True


class MyModeView(ModelView):
    can_edit = True
    can_create = True

    def is_accessible(self):
        if session.get('logged_out'):
            return False
        if session.get('logged_in'):
            return True

    def is_admin(self):
        return 'user' not in session


class AnglerModelView(MyModeView):
    column_list = ['name', 'image', ]
    form_columns = ['name', 'image', ]

    form_overrides = dict(image=FileUploadField)
    form_args = dict(image=dict(validators=[picture_validation]))

    def create_model(self, form):
        model = super().create_model(form)
        model.image = form.data['image']
        db.session.add(model)
        db.session.commit()
        return model

    def delete_model(self, form):
        super().delete_model(form)
        os.remove(path=f'./images/{form.image}')


class SpeciesModelView(MyModeView):
    column_list = ['specie', 'score']
    form_columns = ['specie', 'score', 'style_1', 'style_2']


class CompetitionModelView(MyModeView):
    column_list = ['name', 'detail', 'style', 'end_date', 'enabled', 'image']
    form_columns = ['name', 'detail', 'style', 'end_date', 'enabled', 'image']

    form_choices = {
        'style': [
            ('1', '1'),
            ('2', '2')
        ]
    }

    form_overrides = dict(image=FileUploadField)
    form_args = dict(image=dict(validators=[picture_validation]))

    def create_model(self, form):
        model = super().create_model(form)
        model.image = form.data['image']
        db.session.add(model)
        db.session.commit()
        return model

    def delete_model(self, form):
        super().delete_model(form)
        os.remove(path=f'./images/{form.image}')


class ScoreModelView(MyModeView):
    can_create = False
    # column_sortable_list = (Score.score, )
    column_default_sort = ('score', True)
    column_list = ['angler', 'competition', 'score', ]
