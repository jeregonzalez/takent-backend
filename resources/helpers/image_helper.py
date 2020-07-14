import base64

from werkzeug.exceptions import InternalServerError

from resources.helpers.log_helper import LOGGER


def decode(image_string):
    try:
        image = base64.b64decode(image_string)
        return image
    except Exception as e:
        LOGGER.error('Error decoding the image: {}'.format(e))
        raise InternalServerError


def encode(image):
    try:
        image_string = base64.b64encode(image.read())
        return image_string
    except Exception as e:
        LOGGER.error('Error encoding the image: {}'.format(e))
        raise InternalServerError
