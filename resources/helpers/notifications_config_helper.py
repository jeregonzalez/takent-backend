from database.models.notification import NotificationsConfigurationCommonUser, NotificationsConfigurationEnterpriseUser
from database.models.user import CommonUser


def is_notification_active(user, notification_type):
    notification_model = NotificationsConfigurationCommonUser if isinstance(user, CommonUser) \
        else NotificationsConfigurationEnterpriseUser

    if not notification_model.objects(user=user).count():
        return True

    notification_config = notification_model.objects.get(user=user)

    return getattr(notification_config, notification_type, False)
