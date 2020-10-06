from flask_restful import abort


class Message:

    @staticmethod
    def ok(message):
        return message, 200

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
