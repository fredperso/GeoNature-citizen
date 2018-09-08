import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (jwt_optional)
from geoalchemy2.shape import from_shape
from marshmallow import ValidationError
from shapely.geometry import Point
from sqlalchemy.exc import IntegrityError

from gncitizen.utils.utilsjwt import get_id_role_if_exists
from server import db
from .models import SightModel
from .schemas import sight_schema, sights_schema
from gncitizen.utils.utilssqlalchemy import get_geojson_feature, json_resp
from geojson import  FeatureCollection

routes = Blueprint('sights', __name__)


# @routes.route('/sights/', methods=['GET'])
# @jwt_optional
# def get_sights():
#     sights = SightModel.query.all()
#     result = sights_schema.dump(sights)
#     return jsonify({'sights': result})


@routes.route('/sights/<int:pk>')
# @jwt_optional
def get_sight(pk):
    try:
        sight = SightModel.query.get(pk)
    except IntegrityError:
        return jsonify({'message': 'Sight could not be found.'}), 400
    result = sight_schema.dump(sight)
    return jsonify({'sight': result})


@routes.route('/sights/', methods=['POST'])
@jwt_optional
def sights():
    """Gestion des observations
    If method is POST, add a sight to database else, return all sights
        ---
        parameters:
          - name: cd_nom
            type: string
            required: true
            default: none
          - name : obs_txt
            type : string
            default :  none
            required : false
          - name : count
            type : integer
            default :  none
          - name : date
            type : date
            required: false
            default :  none
          - name : geom
            type : geojson
            required : true
        definitions:
          cd_nom:
            type:int
          obs_txt:
            type: string
          name:
            type: string
          geom:
            type: geometry (geojson)
        responses:
          200:
            description: Adding a sight
        """
    # try:
    #     file = request.files['file']
    #     # if user does not select file, browser also
    #     # submit an empty part without filename
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         return redirect(url_for('uploaded_file',
    #                                 filename=filename))
    if request.method == 'POST':
        json_data = request.get_json()
        medias = request.files
        print('jsondata: ', json_data)
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        # Validate and deserialize input
        # info: manque la date
        try:
            data, errors = sight_schema.load(json_data)
            print("datas: ", data)
        except ValidationError as err:
            return jsonify(err.messages), 422
        try:
            cd_nom = data['cd_nom']
            try:
                geom = from_shape(Point(data['geom'][0]), srid=4326)
            except ValidationError as err:
                return jsonify(err.messages), 422
            if data['count']:
                count = data['count']
            else:
                count = 1
        except:
            return jsonify('Données incomplètes'), 422

        id_role = get_id_role_if_exists()
        if id_role is None:
            obs_txt = data['obs_txt']
        else:
            obs_txt = None

        # Create new sight
        sight = SightModel(
            # date=data['dateobs'],
            cd_nom=cd_nom,
            count=count,
            timestamp_create=datetime.utcnow(),
            uuid_sinp=uuid.uuid4(),
            date=datetime.utcnow(),
            id_role=id_role,
            obs_txt=obs_txt,
            geom=geom
        )
        db.session.add(sight)
        db.session.commit()
        result = sight_schema.dump(SightModel.query.get(sight.id_sight))
        return jsonify({
            'message': 'Created new sight.',
            'sight': result,
        })
    else:
        sights = SightModel.query.all()
        features = []
        for d in sights:
            print(d)
            feature = get_geojson_feature(d[1])
            feature['properties'] = d[0].as_dict(True)
            features.append(feature)
        return FeatureCollection(features)
        # result = sights_schema.dump(sights)
        # return jsonify({'sights': sights})


@routes.route('/sights/', methods=['GET'])
@jwt_optional
@json_resp
def get_sights():
    """Gestion des observations
    If method is POST, add a sight to database else, return all sights
        ---
        definitions:
          id:
            type:int
          insee:
            type: string
          name:
            type: string
          geom:
            type: geometry
        responses:
          200:
            description: A list of all sights
        """

    sights = SightModel.query.all()
    features = []
    print(sights)
    for d in sights:
        print(d.id_sight, d.uuid_sinp, d.cd_nom, d.date, get_geojson_feature(d.geom))
        # print(type(d.as_dict()))
        #
        feature = get_geojson_feature(d.geom)
        # feature['properties']
        feature['properties']=d.as_dict(True)
        features.append(feature)
    return FeatureCollection(features)