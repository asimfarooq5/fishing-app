from flask_marshmallow import Marshmallow

from models import Angler, Species, Competition, Submission, Score

ma = Marshmallow()


class AnglerSchema(ma.Schema):
    class Meta:
        model = Angler
        fields = ('uid', 'name',)


class SpeciesSchema(ma.Schema):
    class Meta:
        model = Species
        fields = ('uid', 'species',)


class CompetitionSchema(ma.Schema):
    class Meta:
        model = Competition
        fields = ('uid', 'name', 'detail', 'style',)


class SubmissionSchema(ma.Schema):
    class Meta:
        model = Submission
        fields = ('uid', 'style', 'length', 'angler_uid', 'species_uid',
                  'comp_uid', 'for_self', 'image', 'friend', 'date',)


class ScoreSchema(ma.Schema):
    class Meta:
        model = Score
        fields = ('uid', 'score', 'angler_uid', 'species_uid', 'comp_uid')
