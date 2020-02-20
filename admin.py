import os
import uuid
from lib2to3.pgen2.grammar import op
from pathlib import Path

from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField

from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError

from models import db, Specie, Submission, Image, Score

ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif', 'jpeg'}


def thumb_name(filename):
    name, _ = op.splitext(filename)
    return secure_filename('%s-thumb.jpg' % name)


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
    list_template = 'custom_list.html'
    column_list = ['name', ]
    form_columns = ['name', ]

    form_overrides = dict(image=FileUploadField)
    form_args = dict(image=dict(validators=[picture_validation]))

    def delete_model(self, form):
        super().delete_model(form)
        angler = int(form.uid)
        submissions = Submission.query.filter_by(angler_uid=angler).all()
        if submissions:
            for submission in submissions:
                db.session.delete(submission)
                db.session.commit()
        images = Image.query.filter_by(angler_uid=angler).all()
        if images:
            for image in images:
                db.session.delete(image)
                db.session.commit()
                os.remove(path=f'./images/{image.image}')
        scores = Score.query.filter_by(angler_uid=angler).all()
        if scores:
            for score in scores:
                db.session.delete(score)
                db.session.commit()


class SpeciesModelView(MyModeView):
    column_list = ['specie', 'score']
    form_columns = ['specie', 'score', 'style_1', 'style_2']


class CompetitionModelView(MyModeView):
    column_list = ['name', 'detail', 'end_date', 'style', 'image']
    form_columns = ['name', 'detail', 'end_date', 'enabled', 'style', 'image']
    can_edit = True
    form_args = {
        'enabled': {
            'label': 'Leader Board Enabled',
        },
        'image': {
            'label': 'image',
            'validators': [picture_validation]
        }
    }
    form_choices = {
        'style': [
            ('1', '1'),
            ('2', '2')
        ],
    }

    form_overrides = dict(image=FileUploadField)

    def create_model(self, form):
        model = super().create_model(form)
        model.image = form.data['image']
        db.session.add(model)
        db.session.commit()
        return model

    def delete_model(self, form):
        super().delete_model(form)
        os.remove(path=f'./images/{form.image}')

    def update_model(self, form, model):
        old_file = model.image
        updated = super().update_model(form, model)
        if updated:
            model.image = form.data['image']
            db.session.commit()
            Path(os.path.join("images", old_file)).unlink()
        return updated


class ScoreModelView(MyModeView):
    can_create = False
    can_edit = False
    can_delete = True

    column_default_sort = ('score', True)
    column_list = ['angler', 'competition', 'score', ]


class SponerModelView(MyModeView):
    form_overrides = dict(sponser=FileUploadField)
    form_args = dict(sponser=dict(validators=[picture_validation]))

    def create_model(self, form):
        model = super().create_model(form)
        model.sponser = form.data['sponser']
        db.session.add(model)
        db.session.commit()
        return model

    def delete_model(self, form):
        super().delete_model(form)
        os.remove(path=f'./images/{form.sponser}')

    def update_model(self, form, model):
        old_file = model.image
        updated = super().update_model(form, model)
        if updated:
            model.sponser = form.data['sponser']
            db.session.commit()
            Path(os.path.join("images", old_file)).unlink()
        return updated
