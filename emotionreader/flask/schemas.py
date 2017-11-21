from flask_marshmallow import Marshmallow
from marshmallow import post_load, validates_schema, ValidationError

from .models import Session, Person, Video, VideoSession


ma = Marshmallow()


class PersonSchema(ma.ModelSchema):
    class Meta:
        model = Person


class SessionSchema(ma.ModelSchema):
    class Meta:
        model = Session
        exclude = ('video_sessions',)

    users = ma.Nested(PersonSchema, many=True)

    @validates_schema
    def validate_user_count(self, data):
        if len(data['users']) != data['user_count']:
            raise ValidationError('user_count must equal the amount of given users')


class VideoSchema(ma.ModelSchema):
    class Meta:
        model = Video
        exclude = ('video_sessions',)


class VideoSessionSchema(ma.ModelSchema):
    class Meta:
        model = VideoSession


session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True, exclude=('users', 'video_sessions'))
person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)
video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)
video_session_schema = VideoSessionSchema()
videos_session_schema = VideoSessionSchema(many=True)
