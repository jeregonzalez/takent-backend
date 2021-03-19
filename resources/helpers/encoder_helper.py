import abc
import datetime
import json

from bson import ObjectId
from flask_mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine.queryset.base import BaseQuerySet

from database.models.enterprise import Enterprise
from database.models.offer import Offer, Postulant
from database.models.service import Service, ServiceRequest
from database.models.user import User, CommonUser
from resources.helpers import user_helper


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        encoder = Encoder(obj)
        encoded_obj = encoder.encode()
        if encoded_obj is not None:
            return encoded_obj
        return json.JSONEncoder.default(self, obj)


class Encoder:

    def __init__(self, obj):
        if issubclass(obj.__class__, User):
            self._strategy = EncodeStrategyUser(obj)
        elif issubclass(obj.__class__, Offer):
            self._strategy = EncodeStrategyOffer(obj)
        elif issubclass(obj.__class__, Service):
            self._strategy = EncodeStrategyService(obj)
        elif issubclass(obj.__class__, Enterprise):
            self._strategy = EncodeStrategyEnterprise(obj)
        elif issubclass(obj.__class__, Postulant):
            self._strategy = EncodeStrategyPostulant(obj)
        elif issubclass(obj.__class__, ServiceRequest):
            self._strategy = EncodeStrategyServiceRequest(obj)
        elif issubclass(obj.__class__, BaseQuerySet):
            self._strategy = EncodeStrategyBaseQuerySet(obj)
        elif issubclass(obj.__class__, Document) or issubclass(obj.__class__, EmbeddedDocument):
            self._strategy = EncodeStrategyGeneralMongoObject(obj)
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, ObjectId):
            self._strategy = EncodeStrategyToString(obj)
        else:
            self._strategy = EncodeStrategyDefault(obj)

    def encode(self) -> object:
        return self._strategy.encode()


class EncodeStrategy:

    def __init__(self, obj):
        self.obj = obj

    @abc.abstractmethod
    def encode(self):
        pass


class EncodeStrategyUser(EncodeStrategy):
    HIDE_FIELDS = ['password', 'profile_photo', 'curriculum']

    def encode(self):
        response = self.obj.to_mongo()
        for field in self.HIDE_FIELDS:
            response.pop(field, None)
            if isinstance(self.obj, CommonUser) and self.obj.address:
                response['address'] = self.obj.address.format_response()
        return response


class EncodeStrategyOffer(EncodeStrategy):

    def encode(self):
        response = self.obj.to_mongo()
        if self.obj.address:
            response['address'] = self.obj.address.format_response()
        if self.obj.enterprise:
            response['enterprise'] = self.obj.enterprise.to_mongo()
            if self.obj.enterprise.address:
                response['enterprise']['address'] = self.obj.enterprise.address.format_response()
        user_info = user_helper.get_user_from_jwt(['user_account', 'user_type'])
        if user_info.get('user_type') == 'common':
            if self.obj.postulants and any(postulant.postulant.id == user_info.get('user_account')
                                           for postulant in self.obj.postulants):
                response['postulated'] = True
            else:
                response['postulated'] = False
        return response


class EncodeStrategyGeneralMongoObject(EncodeStrategy):
    def encode(self):
        return self.obj.to_mongo()


class EncodeStrategyToString(EncodeStrategy):
    def encode(self):
        return str(self.obj)


class EncodeStrategyDefault(EncodeStrategy):
    def encode(self):
        return None


class EncodeStrategyBaseQuerySet(EncodeStrategy):
    def encode(self):
        return [item for item in self.obj]


class EncodeStrategyEnterprise(EncodeStrategy):
    HIDE_FIELDS = ['photos']

    def encode(self):
        response = self.obj.to_mongo()
        if self.obj.address:
            response['address'] = self.obj.address.format_response()
        return response


class EncodeStrategyPostulant(EncodeStrategy):

    def encode(self):
        response = self.obj.to_mongo()
        if self.obj.postulant:
            response['postulant'] = self.obj.postulant.to_mongo()
            if self.obj.postulant.address:
                response['postulant']['address'] = self.obj.postulant.address.format_response()
        return response


class EncodeStrategyService(EncodeStrategy):

    def encode(self):
        response = self.obj.to_mongo()
        response['publication_user'] = {
            '_id': self.obj.publication_user.id,
            'name': self.obj.publication_user.name,
            'surname': self.obj.publication_user.surname,
            'phone': self.obj.publication_user.phone
        }
        if self.obj.address:
            response['address'] = self.obj.address.format_response()
        user_account = user_helper.get_user_from_jwt('user_account')
        if self.obj.service_requests and any(service_request.user.id == user_account
                                             for service_request in self.obj.service_requests):
            response['requested'] = True
        else:
            response['requested'] = False
        response['service_requests_pending'] = 0
        response['service_requests_completed'] = 0
        if self.obj.service_requests:
            for service_request in self.obj.service_requests:
                if service_request.state.name == 'pending':
                    response['service_requests_pending'] += 1
                elif service_request.state.name == 'completed':
                    response['service_requests_completed'] += 1
        average_score, score_count = user_helper.calculate_average_score(user=self.obj.publication_user)
        response['score'] = average_score
        response['score_count'] = score_count
        return response


class EncodeStrategyServiceRequest(EncodeStrategy):

    def encode(self):
        response = self.obj.to_mongo()
        if self.obj.user:
            response['user'] = self.obj.user.to_mongo()
            if self.obj.user.address:
                response['user']['address'] = self.obj.user.address.format_response()
        return response
