from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Angler(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(50), nullable=True)
    ang_rel = db.relationship('Submission', backref='angler')
    scr_rel = db.relationship('Score', backref='anglers')


class Specie(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    style_1 = db.Column(db.Boolean, default=False)
    style_2 = db.Column(db.Boolean, default=False)
    specie = db.Column(db.String(50), nullable=True)
    score = db.Column(db.String(50), nullable=True)
    spe_rel = db.relationship('Submission', backref='specie')


class Competition(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(50), nullable=True)
    detail = db.Column(db.String(50), nullable=True)
    score = db.Column(db.String(50), nullable=True)
    enabled = db.Column(db.Boolean, default=False)
    image = db.Column(db.String(50), nullable=True)
    cut_off_time = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.String(255), default=lambda: date.today())
    comp_rel = db.relationship('Submission', backref='competition')


class Submission(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(250), nullable=True)
    style = db.Column(db.Integer, nullable=True)
    length = db.Column(db.Integer, nullable=True)
    friend = db.Column(db.Boolean, nullable=True)
    image = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(255), default=lambda: date.today())
    angler_uid = db.Column(db.Integer, db.ForeignKey("angler.uid"))
    specie_uid = db.Column(db.Integer, db.ForeignKey("specie.uid"))
    comp_uid = db.Column(db.Integer, db.ForeignKey("competition.uid"))


class Image(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    angler_uid = db.Column(db.Integer, db.ForeignKey("angler.uid"))
    specie_uid = db.Column(db.Integer, db.ForeignKey("specie.uid"))
    comp_uid = db.Column(db.Integer, db.ForeignKey("competition.uid"))
    angler = db.Column(db.String(50), nullable=True)
    specie = db.Column(db.String(50), nullable=True)
    competition = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(50), nullable=True)


class Score(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50), nullable=True)
    angler_uid = db.Column(db.Integer, db.ForeignKey("angler.uid"))
    specie_uid = db.Column(db.Integer, db.ForeignKey("specie.uid"))
    comp_uid = db.Column(db.Integer, db.ForeignKey("competition.uid"))
    angler = db.Column(db.String(50), nullable=True)
    specie = db.Column(db.String(50), nullable=True)
    competition = db.Column(db.String(50), nullable=True)
