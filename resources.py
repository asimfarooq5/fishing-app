import os
import os.path as op

import werkzeug

from flask_restful import reqparse, Resource
from flask_restful.inputs import boolean

from models import Angler, Specie, Competition, Submission, db, Score, Image
from serializers import AnglerSchema, SpeciesSchema, CompetitionSchema, SubmissionSchema, ScoreSchema, ImageSchema

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
            style = Specie.query.filter_by(style_1=True).all()
            schema = SpeciesSchema(many=True)
            return schema.dump(style), 200

        if args['style'] == '2':
            style = Specie.query.filter_by(style_2=True).all()
            schema = SpeciesSchema(many=True)
            return schema.dump(style), 200

        schema = SpeciesSchema(many=True)
        return schema.dump(Specie.query.all())


class CompetitionResource(Resource):
    def get(self):
        schema = CompetitionSchema(many=True)
        # result = []
        # submissions = Submission.query.all()
        # for sub in submissions:
        #     comp = Competition.query.filter_by(uid=sub.comp_uid).all()
        #     root = CompetitionSchema(many=True).dump(comp)
        #     child = SubmissionSchema(many=True).dump(sub)
        #     root['submission'] = child
        #     result.append(root)
        # return result, 200
        return schema.dump(Competition.query.all())


class SubmissionResource(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('device_id', type=str, help='Device ID', required=True)
        parser.add_argument('style', type=str, help='Competition Style', required=True)
        parser.add_argument('length', type=str, help='Fish length in CM', required=True)
        parser.add_argument('angler_uid', type=str, help='angler_id', required=True)
        parser.add_argument('specie_uid', type=str, help='specie_id', required=True)
        parser.add_argument('comp_uid', type=str, help='competition_uid', required=True)
        parser.add_argument('friend', type=boolean, help='True/False', required=False)
        parser.add_argument('image', help='Captured Fish Image', type=werkzeug.datastructures.FileStorage,
                            location='files', required=False, action='append')
        args = parser.parse_args(strict=True)

        submission = Submission.query.filter(Submission.angler_uid == args['angler_uid']).first()
        angler = Angler.query.filter((Angler.uid == args['angler_uid'])).first()
        competition = Competition.query.filter((Competition.uid == args['comp_uid'])).first()

        count = 1
        image1 = Image()
        if args['image']:
            if args['style'] == '1' and len(args['image']) > 2:
                return "more then 2 images not allowed in selected style", 400
            images = args['image']
            filename = ''
            specie = Specie.query.filter(Specie.uid == args['specie_uid']).first()
            for image in images:
                filename = str(count) + "-" + args['device_id'] + "-" + specie.specie + "-" + args[
                    "length"] + "." + image.filename.split('.')[-1]
                count += 1
                image.save(os.path.abspath(os.path.join(image_path, filename)))
                image1.device_id = args['device_id']
                image1.angler = angler.name
                image1.angler_uid = args['angler_uid']
                image1.competition = competition.name
                image1.comp_uid = args['comp_uid']
                image1.specie = specie.specie
                image1.specie_uid = args['specie_uid']
                image1.image = filename
                db.session.add(image1)
                db.session.commit()
        post = Submission()
        post.device_id = args['device_id']
        post.style = args['style']
        post.score = int(specie.score) * int(args['length'])
        post.length = args['length']
        post.angler_uid = args['angler_uid']
        post.comp_uid = args['comp_uid']
        post.specie_uid = args['specie_uid']
        post.competition_name = competition.name
        post.specie_name = specie.specie
        post.angler_name = angler.name
        if args['friend']:
            post.friend = True
        post.image = filename

        db.session.add(post)
        db.session.commit()

        schema = SubmissionSchema()
        return schema.dump(post), 201


class ImageResource(Resource):
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('device_uid', type=str, help='Device id', required=False)
        args = parser.parse_args(strict=True)

        images = ImageSchema(many=True).dump(Image.query.filter_by(
            device_id=args['device_uid']).all())

        return images, 200

    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('image_uid', type=str, help='Image_uid', required=False)
        args = parser.parse_args(strict=True)

        image = Image.query.filter((Image.uid == args['image_uid'])).first()
        if not image:
            return "", 404
        db.session.delete(image)
        db.session.commit()

        return "", 204


class ScoreResource(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('angler_uid', type=str, help='angler_id', required=True)
        parser.add_argument('specie_uid', type=str, help='specie_id', required=True)
        parser.add_argument('comp_uid', type=str, help='competetion_uid', required=True)
        parser.add_argument('score', type=str, help='Angler Score', required=False)
        args = parser.parse_args(strict=True)

        angler = Angler.query.filter((Angler.uid == args['angler_uid'])).first()
        if not angler:
            return "Not found", 404
        specie = Specie.query.filter((Specie.uid == args['specie_uid'])).first()
        if not specie:
            return "Not found", 404
        competition = Competition.query.filter((Competition.uid == args['comp_uid'])).first()
        if not competition:
            return "Not found", 404
        score = Score(**args)
        score.angler = angler.name
        score.specie = specie.specie
        score.competition = competition.name

        db.session.add(score)
        db.session.commit()

        schema = ScoreSchema()
        return schema.dump(score), 201

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('comp_uid', type=str, help='competetion_uid', required=True)
        args = parser.parse_args(strict=True)
        result = []
        score = Submission.query.order_by(Submission.score.desc())
        schema = ScoreSchema(many=True)
        scores = schema.dump(score)
        for curr_score in scores:
            if str(curr_score['comp_uid']) == args['comp_uid']:
                result.append(curr_score)
        return result, 200
