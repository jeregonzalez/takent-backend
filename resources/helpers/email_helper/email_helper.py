import os
import smtplib
from abc import ABC
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException

from resources.helpers.log_helper import LOGGER
from resources.utils.project_vars import ProjectVars

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587

COMMON_IMAGES = {
    'logo_takent': 'logo_takent.png',
    'icon_twitter': 'logo_twitter.png',
    'icon_facebook': 'logo_facebook.png',
    'icon_instagram': 'logo_instagram.png',
    'background_takent': 'background_takent.jpg'
}

IMAGES = {
    'email_activation': {
        'button_activation': 'button_activation.jpeg'
    },
    'email_change_password': {
        'button_change_password': 'button_change_password.jpeg'
    },
    'email_delete_admin': {
        'button_be_admin': 'button_be_admin.jpeg'
    },
    'email_take': {
        'button_take': 'button_contact.jpeg'
    }
}

EMAILS_MAP = {
    'email_activation': 'email_activation.html',
    'email_change_password': 'email_change_password.html',
    'email_delete_admin': 'email_delete_admin.html',
    'email_take': 'email_take.html'
}

SUBJECTS = {
    'email_activation': 'Activación de cuenta - Takent',
    'email_change_password': 'Cambio de clave de acceso - Takent',
    'email_delete_admin': 'Asignación de nuevo admin - Takent',
    'email_take': 'Hola {}, la empresa {} quiere contactarse con vos'
}


class Email(ABC):
    email_type = None

    def __init__(self, destination_email, enterprise_name=None, user_name=None, commentary=None):
        """
        Inicializador del email
        :param destination_email: dirección de destinatario de email
        """
        self.destination_email = destination_email
        self.smtp = smtplib.SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT)
        self.root_message = MIMEMultipart('related')
        self.alternative_message = MIMEMultipart('alternative')
        self.enterprise_name = enterprise_name
        self.user_name = user_name
        self.commentary = commentary

    def _init_email(self):
        """
        Método que inicializa el email
        """
        self.root_message['Subject'] = SUBJECTS.get(self.email_type)
        self.root_message['From'] = ProjectVars.get_project_var('TAKENT_EMAIL')
        self.root_message['To'] = self.destination_email
        self.root_message.preamble = 'This is a multi-part message in MIME format.'
        self.root_message.attach(self.alternative_message)

    def _set_body(self):
        """
        Método que arma el body del mail
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{}/html/{}'.format(current_dir, EMAILS_MAP.get(self.email_type))) as html_file:
            body_message = html_file.read()
        self.alternative_message.attach(MIMEText(body_message, 'html'))

    def _set_images(self):
        """
        Método que carga las imagenes al documento como documentos anexados
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        for key, value in COMMON_IMAGES.items():
            with open('{}/images/{}'.format(current_dir, value), 'rb') as file:
                image = MIMEImage(file.read())
            image.add_header('Content-ID', '<{}>'.format(key))
            self.root_message.attach(image)
        for key, value in IMAGES.get(self.email_type).items():
            with open('{}/images/{}'.format(current_dir, value), 'rb') as file:
                image = MIMEImage(file.read())
            image.add_header('Content-ID', '<{}>'.format(key))
            self.root_message.attach(image)

    def send_email(self):
        """
        Método que envía el email a destinatario
        """
        takent_email = ProjectVars.get_project_var('TAKENT_EMAIL')
        takent_password = ProjectVars.get_project_var('TAKENT_EMAIL_PASSWORD')
        self._init_email()
        self._set_body()
        self._set_images()
        LOGGER.debug('Sending {} to {}'.format(self.email_type, self.destination_email))
        try:
            self.smtp.starttls()
            self.smtp.ehlo()
            self.smtp.login(takent_email, takent_password)
            self.smtp.sendmail(takent_password, self.destination_email, self.root_message.as_string())
        except SMTPException as e:
            LOGGER.error(e)
        finally:
            self.smtp.quit()


class EmailActivation(Email):
    def __init__(self, destination_email, ticket_hash):
        super().__init__(destination_email)
        self.email_type = 'email_activation'
        self.ticket_hash = ticket_hash

    def _set_body(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{}/html/{}'.format(current_dir, EMAILS_MAP.get(self.email_type))) as html_file:
            body_message = html_file.read()
        url_activation = '{}/api/v1/user/activate?ticket={}'.format(ProjectVars.get_project_var('FRONTEND_URL'),
                                                                    self.ticket_hash)
        body_message = body_message.replace('$(url_activation)', url_activation)
        self.alternative_message.attach(MIMEText(body_message, 'html'))


class EmailChangePassword(Email):
    def __init__(self, destination_email, new_password):
        super().__init__(destination_email)
        self.email_type = 'email_change_password'
        self.new_password = new_password

    def _set_body(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{}/html/{}'.format(current_dir, EMAILS_MAP.get(self.email_type))) as html_file:
            body_message = html_file.read()
        body_message = body_message.replace('$(password)', self.new_password)
        self.alternative_message.attach(MIMEText(body_message, 'html'))


class EmailAdmin(Email):
    def __init__(self, destination_email, enterprise_name, user_name):
        super().__init__(destination_email, enterprise_name, user_name)
        self.email_type = 'email_delete_admin'


class EmailTake(Email):
    def __init__(self, destination_email, enterprise_name=None, user_name=None, commentary=None):
        super().__init__(destination_email, enterprise_name, user_name, commentary)
        self.email_type = 'email_take'

    def _init_email(self):
        self.root_message['Subject'] = SUBJECTS.get(self.email_type).format(self.user_name, self.enterprise_name)
        self.root_message['From'] = ProjectVars.get_project_var('TAKENT_EMAIL')
        self.root_message['To'] = self.destination_email
        self.root_message.preamble = 'This is a multi-part message in MIME format.'
        self.root_message.attach(self.alternative_message)

    def _set_body(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{}/html/{}'.format(current_dir, EMAILS_MAP.get(self.email_type))) as html_file:
            body_message = html_file.read()

        if not self.commentary:
            self.commentary = ""
        body_message = body_message.replace('$(commentary)', self.commentary)
        body_message = body_message.replace('$(user_name)', self.user_name)
        body_message = body_message.replace('$(enterprise)', self.enterprise_name)

        self.alternative_message.attach(MIMEText(body_message, 'html'))
