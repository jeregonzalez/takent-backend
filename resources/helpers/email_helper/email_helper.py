from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from resources.helpers.email_helper.data_images import data
from abc import ABC
import smtplib
from smtplib import SMTPException


class Email(ABC):

    def __init__(self, strTo):
        """
        Inicializador del email
        :param strTo: dirección de destinatario de email
        """
        self.msgText = None
        self.msgImage = None
        self.password = 'proyectofinal2020'
        self.strFrom = 'takentuser@gmail.com'
        self.strTo = strTo
        self.smtp = smtplib.SMTP(host='smtp.gmail.com', port=587)
        self.msgRoot = MIMEMultipart('related')
        self.msgAlternative = MIMEMultipart('alternative')

    def set_server(self):
        """
        Método que inicializa el email
        """
        # Create the root message and fill in the from, to, and subject headers
        self.msgRoot['Subject'] = 'Prueba HTML'
        self.msgRoot['From'] = self.strFrom
        self.msgRoot['To'] = self.strTo
        self.msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        # self.msgAlternative = MIMEMultipart('alternative')
        self.msgRoot.attach(self.msgAlternative)

    def body_email(self):
        """
        Método que arma el body del mail
        """

    def charge_images(self):
        """
        Método que carga las imagenes al documento como documentos anexados
        """

    def send_mail(self):
        """
        Método que envía el email a destinatario
        :param body_mail: body del email en html
        :param images: un diccionario de imagenes a cargar al email
        """
        self.set_server()
        self.body_email()
        self.charge_images()

        try:
            self.smtp.starttls()
            self.smtp.login(self.strFrom, self.password)
            self.smtp.sendmail(self.strFrom, self.strTo, self.msgRoot.as_string())
            self.smtp.quit()

        except SMTPException as detail:
            print("Error SMTP:", detail)


class EmailActivation(Email):

    def __init__(self, strTo):
        super().__init__(strTo)

    def body_email(self):
        html = open('resources/helpers/email_helper/html/html_email_activation.html').read()
        self.msgText = MIMEText(html, 'html')
        self.msgAlternative.attach(self.msgText)

    def charge_images(self):
        list_images = data['images_activation']
        for key in list_images:
            file = open(key, 'rb')
            self.msgImage = MIMEImage(file.read())
            file.close()

            self.msgImage.add_header('Content-ID', '<{}>'.format(list_images[key]))
            self.msgRoot.attach(self.msgImage)


class EmailPassword(Email):
    def __init__(self, strTo):
        super().__init__(strTo)

    def body_email(self):
        html = open('resources/helpers/email_helper/html/html_email_change_pass.html').read()
        self.msgText = MIMEText(html, 'html')
        self.msgAlternative.attach(self.msgText)

    def charge_images(self):
        list_images = data['images_password']

        for key in list_images:
            file = open(key, 'rb')
            self.msgImage = MIMEImage(file.read())
            file.close()

            self.msgImage.add_header('Content-ID', '<{}>'.format(list_images[key]))
            self.msgRoot.attach(self.msgImage)


class EmailAdmin(Email):
    def __init__(self, strTo):
        super().__init__(strTo)

    def body_email(self):
        html = open('resources/helpers/email_helper/html/html_email_delete_admin.html').read()
        self.msgText = MIMEText(html, 'html')
        self.msgAlternative.attach(self.msgText)

    def charge_images(self):
        list_images = data['images_admin']

        for key in list_images:
            file = open(key, 'rb')
            self.msgImage = MIMEImage(file.read())
            file.close()

            self.msgImage.add_header('Content-ID', '<{}>'.format(list_images[key]))
            self.msgRoot.attach(self.msgImage)

