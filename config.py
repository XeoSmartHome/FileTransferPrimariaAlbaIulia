

class BaseConfig(object):
    # DATABASE SETTINGS
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data_base.db'
    SECRET_KEY = '****'

    # UPLOAD SETTINGS
    MAX_CONTENT_LENGTH = 2024 * 1024 * 1024  # bytes
    FILE_FILE_SPAN = 5 * 24 * 60 * 60  # seconds

    # EMAIL SETTINGS
    MAIL_SERVER = 'mail.apulum.ro'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '****'
    MAIL_PASSWORD = '****'
    MAIL_DEFAULT_SENDER = 'TRANSFER PRIMARIA ALBA IULIA <transfer@apulum.ro>'

    # SECURE PASSWORD
    PASSWORD_SALT = '****'

    # ADMIN
    BASIC_AUTH_USERNAME = '****'
    BASIC_AUTH_PASSWORD = '****'

    # SERVER
    SERVER_IP = 'xx.xx.xx.xx'
    SERVER_PORT = 80
    SERVER_NAME = 'transfer.apulum.ro'
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # FOLDERS
    TEMPORARY_FOLDER = 'files_temp'
    ARCHIVES_FOLDER = 'files'
