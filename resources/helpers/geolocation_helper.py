from typing import Type, Union, List

from geopy import distance

from database.models.offer import Offer
from database.models.parametric_docs import StateService, StateOffer
from database.models.service import Service
from database.models.user import CommonUser


def get_near_services(*args, **kwargs) -> List[Service]:
    return _get_near('services', *args, **kwargs)


def get_near_offers(*args, **kwargs) -> List[Offer]:
    return _get_near('offers', *args, **kwargs)


def _get_near(obj_type: str, latitude: float, longitude: float, radius: float, user: CommonUser,
              filter_by_preferred: bool = True) -> list:
    obj: Type[Union[Offer, Service]] = Offer if obj_type == 'offers' else Service
    filters = {
        'state': (StateService if obj_type == 'offers' else StateOffer).objects.get(name='active'),
        'address__location__ne': None
    }
    if filter_by_preferred:
        filters['sector__in'] = user.preferred_services
    all_entities = obj.objects(**filters)
    user_location = (latitude, longitude)
    near_entities = []
    for entity in all_entities:
        entity_location = (entity.address.location.lat, entity.address.location.lng)
        dist: float = distance.distance(user_location, entity_location).meters
        if dist <= radius:
            near_entities.append(entity)
    return near_entities
