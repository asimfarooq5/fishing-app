from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Angler(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(50), nullable=True)
    ang_rel = db.relationship('Submission', backref='angler')
    scr_rel = db.relationship('Score', backref='angler')

    def __str__(self):
        return self.name


class Species(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    style_1 = db.Column(db.Boolean, default=False)
    style_2 = db.Column(db.Boolean, default=False)
    species = db.Column(db.String(50), nullable=True)
    spe_rel = db.relationship('Submission', backref='species')

    def __str__(self):
        return self.species


class Competition(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(50), nullable=True)
    detail = db.Column(db.String(50), nullable=True)
    comp_rel = db.relationship('Submission', backref='competition')

    def __str__(self):
        return self.name


class Submission(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.Integer, nullable=True)
    length = db.Column(db.Integer, nullable=True)
    for_self = db.Column(db.String(50), nullable=True)
    friend = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(255), default=lambda: date.today())
    angler_uid = db.Column(db.Integer, db.ForeignKey("angler.uid"))
    species_uid = db.Column(db.Integer, db.ForeignKey("species.uid"))
    comp_uid = db.Column(db.Integer, db.ForeignKey("competition.uid"))


class Score(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50), nullable=True)
    angler_uid = db.Column(db.Integer, db.ForeignKey("angler.uid"))
    species_uid = db.Column(db.Integer, db.ForeignKey("species.uid"))
    comp_uid = db.Column(db.Integer, db.ForeignKey("competition.uid"))

    def __str__(self):
        return self.score
