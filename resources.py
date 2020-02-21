import os
import os.path as op
from pathlib import Path
from datetime import datetime

import werkzeug

from flask_restful import reqparse, Resource
from flask_restful.inputs import boolean

from models import Angler, Specie, Competition, Submission, db, Score, Image, Sponser
from serializers import AnglerSchema, SpeciesSchema, CompetitionSchema, \
    SubmissionSchema, ScoreSchema, ImageSchema, SponserSchema

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

        angler = Angler.query.filter((Angler.uid == args['angler_uid'])).first()
        if not angler:
            return 'no angler', 404
        specie = Specie.query.filter(Specie.uid == args['specie_uid']).first()
        if not specie:
            return 'no specie', 404
        competition = Competition.query.filter((Competition.uid == args['comp_uid'])).first()
        if not competition:
            return 'no competetion', 404

        image1 = Image()
        if args['image']:
            imagess = ImageSchema(many=True).dump(Image.query.filter(
                (Image.angler_uid == args['angler_uid']) &
                (Image.specie_uid == args['specie_uid'])).all())
            if len(imagess) >= 2:
                return "Max[2] Limit Exceeded for this specie ", 400
            if args['style'] == '1' and len(args['image']) > 2:
                return "more then 2 images not allowed in selected style", 400
            filename = ''
            images = args['image']
            for image in images:
                filename = "" + args['device_id'] + "-" + specie.specie + "-" + \
                           args["length"] + "-" + "".join(str(datetime.now()).split('.')[0]).replace(" ", "") \
                           + '.' + image.filename.split('.')[-1]
                image.save(os.path.abspath(os.path.join(image_path, filename)))
                image1.device_id = args['device_id']
                image1.angler = angler.name
                image1.angler_uid = args['angler_uid']
                image1.competition = competition.name
                image1.comp_uid = args['comp_uid']
                image1.specie = specie.specie
                image1.specie_uid = args['specie_uid']
                image1.length = args['length']
                image1.image = filename
                db.session.add(image1)
                db.session.commit()

        post = Submission()
        post.device_id = args['device_id']
        post.style = args['style']
        post.score = float(specie.score) * float(args['length'])
        post.length = args['length']
        post.angler_uid = args['angler_uid']
        post.comp_uid = args['comp_uid']
        post.specie_uid = args['specie_uid']
        post.competition_name = competition.name
        post.specie_name = specie.specie
        post.angler_name = angler.name
        post.image = filename

        db.session.add(post)
        db.session.commit()
        score = Score.query.filter(
            (Score.angler_uid == float(args['angler_uid'])) & (Score.comp_uid == float(args['comp_uid']))).first()
        if not score:
            new_score = Score()
            new_score.angler_uid = args['angler_uid']
            new_score.angler = angler.name
            new_score.comp_uid = args['comp_uid']
            new_score.competition = competition.name
            new_score.specie_uid = args['specie_uid']
            new_score.specie = specie.specie
            new_score.score = 0
            new_score.score = float(post.score) + new_score.score
            db.session.add(new_score)
            db.session.commit()

        if score:
            score.angler_uid = args['angler_uid']
            score.angler = angler.name
            score.comp_uid = args['comp_uid']
            score.competition = competition.name
            score.specie_uid = args['specie_uid']
            score.specie = specie.specie
            score.score = float(post.score) + float(score.score)
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
        specie = Specie.query.filter((Specie.uid == image.specie_uid)).first()
        submisson = Submission.query.filter((Submission.angler_uid == image.angler_uid) &
                                            (Submission.length == image.length) &
                                            (Submission.device_id == image.device_id) &
                                            (Submission.image == image.image)).first()
        db.session.delete(submisson)
        db.session.commit()
        scores = Score.query.filter(
            (Score.angler_uid == image.angler_uid) &
            (Score.specie_uid == image.specie_uid)).all()
        for score in scores:
            total = float(image.length) * float(specie.score)
            score.score = score.score - total
            db.session.commit()
        db.session.delete(image)
        db.session.commit()
        Path(os.path.join("images", image.image)).unlink()

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
        score.angler_uid = args['angler_uid']
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

        competitions = Competition.query.all()

        score = Score.query.order_by(Score.score.desc())
        schema = ScoreSchema(many=True)
        scores = schema.dump(score)
        for curr_score in scores:
            if str(curr_score['comp_uid']) == args['comp_uid']:
                print(type(curr_score['score']))
                result.append(curr_score)
        return result, 200


class SponerResource(Resource):
    def get(self):
        schema = SponserSchema(many=True)
        return schema.dump(Sponser.query.all())
