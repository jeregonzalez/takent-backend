from datetime import datetime

from flask_restful import Resource

from database.models.notification import Notification
from database.models.offer import Offer
from database.models.parametric_docs import StateOffer, StateService
from database.models.service import Service
from database.models.user import CommonUser, EnterpriseUser
from resources.helpers import enterprise_helper, notifications_config_helper
from resources.helpers.notifications_helper import SuggestInfoCompletionNotification, OffersNearingToFinishNotification, \
    SuggestPublishNewOfferNotification
from resources.utils.messages import Message

NOTIFICATION_DAYS_WINDOW = 5


class GenerateNotificationsApi(Resource):

    def get(self):
        # Suggest information completion
        for user in CommonUser.objects(state='active'):
            if not notifications_config_helper.is_notification_active(user, 'suggest_info_completion'):
                continue

            last_notification = Notification.objects(user=user, type='suggest_info_completion').order_by('-date').first()
            if last_notification and abs((last_notification.date - datetime.today()).days) < NOTIFICATION_DAYS_WINDOW:
                continue

            info = {
                'education': user.education,
                'experience': user.experience,
                'skill': user.skill,
                'curriculum': user.curriculum,
                'language': user.language
            }

            if any(not item for item in info.values()):
                missing_info = (item[0] for item in info.items() if not item[1])
                SuggestInfoCompletionNotification(user=user, missing_info=missing_info).save()

        # Offer nearing to finish
        for user in EnterpriseUser.objects(state='active'):
            if not notifications_config_helper.is_notification_active(user, 'offers_nearing_to_finish'):
                continue

            last_notification = Notification.objects(user=user, type='offers_nearing_to_finish').order_by('-date').first()
            if last_notification and abs((last_notification.date - datetime.today()).days) < NOTIFICATION_DAYS_WINDOW:
                continue

            enterprise = enterprise_helper.get_enterprise(user_account=user.account)

            for offer in Offer.objects(enterprise=enterprise, state='active'):
                if abs((offer.publication_date - datetime.today()).days) >= 23:
                    OffersNearingToFinishNotification(entity=offer.id, user=user, offer_name=offer.title).save()

        # Suggest publish new offer
        for user in EnterpriseUser.objects(state='active'):
            if not notifications_config_helper.is_notification_active(user, 'suggest_publish_new_offer'):
                continue

            last_notification = Notification.objects(user=user, type='suggest_publish_new_offer').order_by('-date').first()
            if last_notification and abs((last_notification.date - datetime.today()).days) < NOTIFICATION_DAYS_WINDOW:
                continue

            enterprise = enterprise_helper.get_enterprise(user_account=user.account)

            last_offer = Offer.objects(enterprise=enterprise).order_by('-publication_date').first()

            if last_offer and (datetime.today() - last_offer.publication_date).days > 14:
                SuggestPublishNewOfferNotification(user=user).save()

        return Message.ok()


class ExpireOffersApi(Resource):

    def get(self):
        for offer in Offer.objects(state='active'):
            if (datetime.today() - offer.publication_date).days > 30:
                offer.update(state=StateOffer.objects.get(name='finished'))

        return Message.ok()


class ExpireServicesApi(Resource):

    def get(self):
        for service in Service.objects(state='active'):
            if (datetime.today() - service.publication_date).days > 30:
                service.update(state=StateService.objects.get(name='finished'))

        return Message.ok()


class PublishProgrammedOffersApi(Resource):

    def get(self):
        for offer in Offer.objects(state='programmed'):
            if (datetime.today() - offer.publication_date).days == 0:
                offer.update(state=StateOffer.objects.get(name='active'))

        return Message.ok()
