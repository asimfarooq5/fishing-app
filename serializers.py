from flask_marshmallow import Marshmallow

from models import Angler, Specie, Competition, Submission, Score

ma = Marshmallow()


class AnglerSchema(ma.Schema):
    class Meta:
        model = Angler
        fields = ('uid', 'name',)


class SpeciesSchema(ma.Schema):
    class Meta:
        model = Specie
        fields = ('uid', 'specie',)


class CompetitionSchema(ma.Schema):
    class Meta:
        model = Competition
        fields = ('uid', 'name', 'detail', 'style', 'start_date', 'end_date', 'image', 'enabled')


class SubmissionSchema(ma.Schema):
    class Meta:
        model = Submission
        fields = ('uid', 'style', 'length', 'angler_uid', 'species_uid',
                  'comp_uid', 'for_self', 'image', 'friend', 'date', 'score')


class ScoreSchema(ma.Schema):
    class Meta:
        model = Score
        fields = ('comp_uid', 'score', 'angler', 'specie', 'competition')


class ImageSchema(ma.Schema):
    class Meta:
        model = Score
        fields = ('uid', 'image', 'angler', 'specie', 'length', 'competition')


class SponserSchema(ma.Schema):
    class Meta:
        model = Score
        fields = ('sponser', )
