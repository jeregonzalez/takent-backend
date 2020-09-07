class Message:

    @staticmethod
    def ok(response):
        return response, 200

    @staticmethod
    def created(entity):
        return {'message': '{} created successfully'.format(entity)}, 201

    @staticmethod
    def update():
        return '', 204

    @staticmethod
    def delete():
        return '', 204

    @staticmethod
    def added(entity):
        return {'message': '{} created and added successfully'.format(entity)}, 201
