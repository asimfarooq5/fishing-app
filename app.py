import os.path as op

from flask import Flask, render_template, session, flash, redirect, request, make_response, send_from_directory, url_for
from flask_admin import AdminIndexView, expose
from flask_restful import Api, abort
from werkzeug.security import check_password_hash

import flask_admin as admin
from admin import AnglerModelView, SpeciesModelView, CompetitionModelView, ScoreModelView

from models import db, Angler, Specie, Competition, Score, Submission
from serializers import ma
from resources import AnglerResource, SpeciesResource, CompetitionResource, SubmissionResource, ScoreResource

UPLOAD_FOLDER = './upload'
app = Flask(__name__, static_folder='images')
path = op.join(op.dirname(__file__), 'statics')
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
    if request.form['username'] == 'admin' and request.form['password'] == 'password':
        session['logged_in'] = True
        if 'user' in session:
            session.pop('user')
        return redirect('/angler')
    user = Angler.query.filter_by(name=request.form['username']).first()
    if user:
        if check_password_hash(request.form['password'], request.form['password']):
            session['logged_in'] = True
            session['user'] = {'id': user.uid}
            resp = make_response(redirect('/content'))
            resp.set_cookie('username', request.form['username'])
            return redirect('/angler')
        flash('Invalid Email or  Password')
        return render_template('login.html')

    session['logged_in'] = False
    flash('Invalid Email or  Password')
    return render_template('login.html')


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
        return super().index()


api.add_resource(AnglerResource, '/api/angler/')
api.add_resource(SpeciesResource, '/api/species/')
api.add_resource(CompetitionResource, '/api/competition/')
api.add_resource(SubmissionResource, '/api/submission/')
api.add_resource(ScoreResource, '/api/score/')

if __name__ == '__main__':
    admin = admin.Admin(app, name='Home', index_view=MyAdminIndexView(name=' '), url='/angler')
    admin.add_view(AnglerModelView(Angler, db.session, url='/angler'))
    admin.add_view(SpeciesModelView(Specie, db.session, url='/specie'))
    admin.add_view(CompetitionModelView(Competition, db.session, url='/competition'))
    admin.add_view(ScoreModelView(Submission, db.session, url='/score', name='Score'))

    app.run(host='0.0.0.0', port=5000, debug=True)
