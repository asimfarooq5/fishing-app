import os
from pathlib import Path

from flask import Flask, render_template, session, flash, redirect, request, make_response, send_from_directory, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_restful import Api, abort
from werkzeug.security import check_password_hash

import flask_admin as admin
from admin import AnglerModelView, SpeciesModelView, CompetitionModelView, ScoreModelView

from models import db, Angler, Specie, Competition, Score, Submission, Image
from serializers import ma
from resources import AnglerResource, SpeciesResource, CompetitionResource, SubmissionResource, ScoreResource, \
    ImageResource

UPLOAD_FOLDER = './upload'
app = Flask(__name__, static_folder='images')
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api = Api(app)
db.init_app(app)
ma.init_app(app)
db.create_all(app=app)


def authenticate():
    token = request.headers.get('Authorization')
    if not token:
        abort(401, description="Unauthorized")
    items = token.split(' ')
    if len(items) != 2:
        abort(401, description="Unauthorized")
    if items[0].lower() != 'token':
        abort(401, description="Unauthorized")
    user = Angler.query.filter_by(token=items[1]).first()
    if not user:
        abort(401, description="Unauthorized")
    return user


def load_user(session):
    if session['logged_in'] == session:
        return True


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'password':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect('/angler')
    return render_template('login.html', error=error)


@app.route('/gallery')
def get_gallery():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        image_names = os.listdir('./images')
        return render_template("gallery.html", image_names=image_names)


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/angler/<angler_uid>', methods=['GET'])
def get_albums(angler_uid):
    error = None
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        images = Image.query.filter_by(angler_uid=int(angler_uid)).all()
        if not images:
            error = 'Empty Directory'
        return render_template("gallery.html", error=error, images=images)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('login.html')


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if session.get('logged_in'):
            if request.cookies.get('username'):
                return redirect('/angler')
        if not session.get('logged_in'):
            return render_template('login.html')
        return redirect('/angler')


api.add_resource(AnglerResource, '/api/angler/')
api.add_resource(SpeciesResource, '/api/species/')
api.add_resource(CompetitionResource, '/api/competition/')
api.add_resource(SubmissionResource, '/api/submission/')
api.add_resource(ScoreResource, '/api/score/')
api.add_resource(ImageResource, '/api/image/')

if __name__ == '__main__':
    admin = admin.Admin(app, name='Home', index_view=MyAdminIndexView(name=' '), url='/angler')
    admin.add_view(AnglerModelView(Angler, db.session, url='/angler'))
    admin.add_view(SpeciesModelView(Specie, db.session, url='/specie'))
    admin.add_view(CompetitionModelView(Competition, db.session, url='/competition'))
    admin.add_view(ScoreModelView(Score, db.session, url='/score', name='Score'))
    admin.add_link(MenuLink(name='Logout', category='', url="/logout"))
    # admin.add_view(FileAdmin(Path(os.path.join("images")), name='All Images'))

    app.run(host='0.0.0.0', port=8000, debug=True)
