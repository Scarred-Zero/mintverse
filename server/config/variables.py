import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# DATABASE VARIABLES
MYSQL_DATABASE_URI = os.getenv("MYSQL_DATABASE_URI")

# MAIL VARIABLES
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_DEFAULT_FROM = os.getenv("MAIL_DEFAULT_FROM")


ADMIN_NAME = os.getenv("ADMIN_NAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
