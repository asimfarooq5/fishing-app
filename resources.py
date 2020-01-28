import os
import uuid
import os.path as op
from datetime import date

import werkzeug

from flask_restful import reqparse, Resource

from models import Angler, Species, Competition, Submission, db, Score
from serializers import AnglerSchema, SpeciesSchema, CompetitionSchema, SubmissionSchema, ScoreSchema

image_path = op.join(op.dirname(__file__), "images")
try:
    os.mkdir(image_path)
except OSError:
    pass
UPLOAD_FOLDER = image_path


class AnglerResource(Resource):
    def get(self):
        schema = AnglerSchema(many=True)
        return schema.dump(Angler.query.all())


class SpeciesResource(Resource):
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('style', type=str, help='Species Style', required=False)
        args = parser.parse_args()

        if args['style'] == '1':
            style = Species.query.filter_by(style_1=True).all()
            schema = SpeciesSchema(many=True)
            return schema.dump(style), 200

        if args['style'] == '2':
            style = Species.query.filter_by(style_2=True).all()
            schema = SpeciesSchema(many=True)
            return schema.dump(style), 200

        schema = SpeciesSchema(many=True)
        return schema.dump(Species.query.all())


class CompetitionResource(Resource):
    def get(self):
        result = []
        submissions = Submission.query.all()
        for sub in submissions:
            comp = Competition.query.filter_by(uid=sub.comp_uid).all()
            root = CompetitionSchema(many=True).dump(comp)
            child = SubmissionSchema(many=True).dump(sub)
            root['submission'] = child
            result.append(root)
        return result, 200


class SubmissionResource(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('style', type=str, help='Competition Style', required=True)
        parser.add_argument('length', type=str, help='Fish lenght in CM', required=True)
        parser.add_argument('angler_uid', type=str, help='angler_id', required=True)
        parser.add_argument('species_uid', type=str, help='species_id', required=True)
        parser.add_argument('comp_uid', type=str, help='competetion_uid', required=True)
        parser.add_argument('for_self', type=str, help='Posting for self (True/False)', required=False)
        parser.add_argument('friend', type=str, help='Friend name', required=False)
        parser.add_argument('image', help='Captured Fish Image', type=werkzeug.datastructures.FileStorage,
                            location='files', required=False, action='append')
        args = parser.parse_args(strict=True)

        if args['image']:
            images = args['image']
            for image in images:
                file = args.pop(image)
                filename = str(uuid.uuid4()) + "." + image.filename.split('.')[-1]
                image.save(os.path.abspath(os.path.join(image_path, filename + date.today())))
        else:
            filename = ''
        post = Submission(**args)
        if args['style'].lower() == 'true':
            post.for_self = True
        post.image = filename
        db.session.add(post)
        db.session.commit()

        schema = SubmissionSchema()
        return schema.dump(post), 201


class ScoreResource(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('angler_uid', type=str, help='angler_id', required=True)
        parser.add_argument('species_uid', type=str, help='species_id', required=True)
        parser.add_argument('comp_uid', type=str, help='competetion_uid', required=True)
        parser.add_argument('score', type=str, help='Angler Score', required=False)
        args = parser.parse_args(strict=True)

        score = Score(**args)

        db.session.add(score)
        db.session.commit()

        schema = ScoreSchema()
        return schema.dump(score), 201

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('angler_uid', type=str, help='Angler id', required=False)
        args = parser.parse_args(strict=True)

        scores = Score.query.filter_by(angler_uid=args['angler_uid']).all()

        schema = ScoreSchema(many=True)
        return schema.dump(scores), 200
