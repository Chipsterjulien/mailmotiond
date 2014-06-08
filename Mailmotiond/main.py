import sys
import os
import logging
import logging.handlers
import configparser
import time
import glob

from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64


class Mail():
    def __init__(self, *args, **kwargs):
        conf_obj = kwargs.get('conf')

        self.smtp = conf_obj['Mail']['smtp']
        self.port = conf_obj['Mail']['port']
        self.login = conf_obj['Mail']['login']
        self.password = conf_obj['Mail']['password']
        self.send_to = conf_obj['Mail']['send to']

        self.From = self.login + '@' + '.'.join(self.smtp.split('.')[1:])

    def send(self, *args, **kwargs):
        picture = kwargs.get('pic')

        msg = MIMEMultipart()
        msg['Charset'] = "UTF-8"
        msg['Date'] = formatdate(localtime=True)
        msg['From'] = self.login + '@' + '.'.join(self.smtp.split('.')[1:])
        msg['Subject'] = "Détection d'un mouvement suspect"
        msg['To'] = self.send_to

        msg.attach(MIMEText('', 'html'))

        part = MIMEBase('application', 'octet-stream')
        fp = open(picture, 'rb')
        part.set_payload(fp.read())
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=picture)
        msg.attach(part)

        try:
            server = SMTP_SSL(self.smtp, self.port)

            server.set_debuglevel(False)
            server.ehlo
            server.login(self.login, self.password)
            try:
                server.sendmail(self.From, self.send_to, msg.as_string())
            finally:
                server.quit()

        except Exception as e:
            logging.critical("Unable to send an email\n{0}".format(str(e)))
            sys.exit(2)


def check_file(*args, **kwargs):
    """ Test if file exist, can test some permissions and create empty file.
    """
    fp = kwargs.get('fp')
    read = kwargs.get('read', False)
    write = kwargs.get('write', False)
    create = kwargs.get('create', False)

    if not os.path.exists(fp):
        if create:
            with open(fp, 'w'):
                pass
        else:
            print("File \"{0}\" don't exist !\nExiting …".format(fp),
                  file=sys.stderr)
            sys.exit(2)

    if read:
        if not os.access(fp, os.R_OK):
            print("You don't have read permissions on \"{0}\" !\nExiting …"
                  .format(fp), file=sys.stderr)
            sys.exit(2)

    if write:
        if not os.access(fp, os.W_OK):
            print("You don't have write permissions on \"{0}\" !\nExiting …"
                  .format(fp), file=sys.stderr)
            sys.exit(2)


def find_picture(*args, **kwargs):
    loop = True
    conf_obj = kwargs.get('conf')
    mail = Mail(conf=conf_obj)

    while loop:
        pict_list = glob.glob(os.path.join(conf_obj['Default']['picture path'],
                                           '*.jpg'))

        for picture in pict_list:
            mail.send(pic=picture)
            os.remove(picture)

        time.sleep(int(conf_obj['Default']['sleep time']))


def load_conf(*args, **kwargs):
    conf = configparser.ConfigParser()
    conf.read(kwargs.get('conf'))

    if not conf.sections():
        logging.critical("{0} is not valid or is empty file !\nExiting …"
                         .format(kwargs.get('conf')), file=sys.stderr)
        sys.exit(2)

    if 'Default' not in conf:
        logging.critical('There is not \"Default\" section in conf file: \
                         \"{0}\" !\nExiting …'.format(kwargs.get('conf')),
                         file=sys.stderr)
        sys.exit(2)

    for i in ['sleep time', 'picture path', 'smtp', 'port', 'login',
              'password', 'send to']:
        if not(i in conf['Default']) and not(i in conf['Mail']):
            logging.critical("\"{0}\" is not in conf file: \"{1}\" !\n\
                             Exiting …".format(i, kwargs.get('conf')),
                             file=sys.stderr)
            sys.exit(2)

    try:
        int(conf['Default']['sleep time'])
    except ValueError:
        logging.critical("\"{0}\" is not an integer. Edit \"{1}\" file !\nExi\
                         ting …".format(conf['Default']['sleep time'],
                         kwargs.get('conf')))
        sys.exit(2)

    return conf


def log_activity(*args, **kwargs):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(kwargs.get('log'), 'a',
                                                        1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)


def main():
    #################
    # Faire des tests
    # Utiliser pudb
    #################

    conf_file = '/etc/mailmotiond/mailmotiond.conf'
    log_file = '/var/log/mailmotiond/main.log'
    # conf_file = '/home/julien/Desktop/mailer_daemon_motion/cfg/mailmotiond.conf'
    # log_file = '/home/julien/Desktop/mailer_daemon_motion/cfg/main.log'

    check_file(fp=conf_file, read=True, write=False, create=False)
    check_file(fp=log_file, read=False, write=True, create=True)

    log_activity(log=log_file)
    conf_obj = load_conf(conf=conf_file)

    find_picture(conf=conf_obj)
