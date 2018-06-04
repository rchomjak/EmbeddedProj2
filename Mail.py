import smtplib


#from io import BytesIO 

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sys

class Email(object):

    text = (
    """
    Motion has been detected  
    Photo is in attachement
                

    Yours motion detection system 3000
    """
    )

    def __init__(self, config):
        self.config = config
        self.smtp_server = None

    def send(self, picts_fd=None, in_text=None):
        self.text = str(Email.text)
        if in_text is not None:
           self.text = str(in_text) 

        def init_smtp():
            self.smtp_server = smtplib.SMTP(self.config.server_smtp.address)
            self.smtp_server.ehlo()
            self.smtp_server.starttls()
            self.smtp_server.ehlo()
            self.smtp_server.login(self.config.server_smtp.username, self.config.server_smtp.password)

        init_smtp()

        self.message = MIMEMultipart()
        self.message['From'] = self.config.server_smtp.From
        self.message['To'] = ", ".join(self.config.user.recipients)
        self.message['Subject'] = "Yours motion system"
        self.message.attach(MIMEText(self.text))



        for pict_id ,pict_fd in enumerate(picts_fd):

            img = MIMEApplication(pict_fd.getvalue())
            img['Content-Disposition'] = 'attachment, filename="{}"'.format(str(pict_id) + ".png")
            self.message.attach(img)

        self.smtp_server.sendmail(self.config.server_smtp.From, ", ".join(self.config.user.recipients), self.message.as_string())
 
        self.smtp_server.close()

