from multiprocessing import Process

from flask import (Flask, render_template, request, make_response, jsonify,
                   abort)

from . import models
from . import schemas
from emotionreader.video import record_to_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'

db = models.db
ma = schemas.ma

db.init_app(app)
ma.init_app(app)


@app.cli.command('initdb')
def init_db_command():
    db.create_all()
    print('initialized the database')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/sessions/', methods=['GET', 'PUT'])
def sessions():
    if request.method == 'GET':
        all_sessions = models.Session.query.all()
        return schemas.sessions_schema.jsonify(all_sessions)
    else:
        json_data = request.get_json()
        if not json_data:
            abort(400)

        data, errors = schemas.session_schema.load(json_data)
        if errors:
            return make_response(jsonify(errors), 422)

        db.session.add(data)
        db.session.commit()
        return schemas.session_schema.jsonify(data)


@app.route('/api/session/<int:id>/', methods=['GET'])
def session_detail(id):
    session = models.Session.query.get(id)
    return schemas.session_schema.jsonify(session)


@app.route('/api/session/<int:id>/video_sessions/')
def session_video_sessions(id):
    video_sessions = models.VideoSession.query.filter_by(session_id=id)
    return schemas.videos_session_schema.jsonify(video_sessions)


@app.route('/api/users/')
def users():
    users = models.Person.query.all()
    return schemas.persons_schema.jsonify(users)


@app.route('/api/session/<int:session_id>/video/<int:video_id>/video_sessions/')
def video_sessions(session_id, video_id):
    video_sessions = models.VideoSession.query.filter_by(
            session_id=session_id, video_id=video_id)
    return schemas.videos_session_schema.jsonify(video_sessions)


@app.route('/api/videos/', methods=['GET', 'PUT'])
def videos():
    if request.method == 'GET':
        videos = models.Video.query.all()
        return schemas.videos_schema.jsonify(videos)
    else:
        json_data = request.get_json()
        if not json_data:
            abort(400)

        data, errors = schemas.video_schema.load(json_data)
        if errors:
            return make_response(jsonify(errors), 422)

        db.session.add(data)
        db.session.commit()
        return schemas.video_schema.jsonify(data)


@app.route('/api/action/record/<int:session_id>/<int:video_id>/')
def record(session_id, video_id):
    # needs to run in separate process, otherwise it might be locked by GIL
    session = models.Session.query.get(session_id)
    video = models.Video.query.get(video_id)
    if not session or not video:
        return make_response(jsonify({'error': 'session or video not found'}), 404)

    p = Process(target=record_to_file, args=(session, video))
    p.start()
    return jsonify({'message': 'started recording'})


def run_webserver(args):
    app.run(host='127.0.0.1', port='5000', debug=args.debug)


def initdb(args):
    db.create_all(app=app)
    print('initialized the database')
