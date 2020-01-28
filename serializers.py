from flask_marshmallow import Marshmallow

from models import Angler, Species, Competition, Submission, Score

ma = Marshmallow()


class AnglerSchema(ma.Schema):
    class Meta:
        model = Angler
        fields = ('name',)


class SpeciesSchema(ma.Schema):
    class Meta:
        model = Species
        fields = ('species',)


class CompetitionSchema(ma.Schema):
    class Meta:
        model = Competition
        fields = ('name', 'detail', 'style',)


class SubmissionSchema(ma.Schema):
    class Meta:
        model = Submission
        fields = ('style', 'length', 'angler_uid', 'species_uid',
                  'comp_uid', 'for_self', 'image', 'friend', 'date',)


class ScoreSchema(ma.Schema):
    class Meta:
        model = Score
        fields = ('score', 'angler_uid', 'species_uid', 'comp_uid')
