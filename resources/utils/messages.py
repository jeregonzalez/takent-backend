from flask_restful import abort


class Message:

    @staticmethod
    def ok(message=None):
        return {'message': message if message else 'OK'}, 200

    @staticmethod
    def created():
        return {'message': 'Created'}, 201

    @staticmethod
    def updated():
        return '', 204

    @staticmethod
    def deleted():
        return '', 204

    @staticmethod
    def bad_request(message):
        abort(400, message=message)
