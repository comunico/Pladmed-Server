from flask import Blueprint
from flask import current_app, make_response, jsonify, request, Response
from pladmed.models.user import User
from pladmed.utils.decorators import user_protected, superuser
from pladmed.utils.response import (
    error_response, HTTP_CREATED, HTTP_OK, HTTP_NOT_FOUND, HTTP_BAD_REQUEST,
    HTTP_NO_CONTENT
)
from flask_mail import Mail, Message
from smtplib import SMTPException
from threading import Thread
import logging
from passlib.hash import pbkdf2_sha256 as secure_password
import traceback

auth = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)

@auth.route('/forgot', methods=["POST"])
def forgot():
    data = request.get_json(force=True)
    url_base = request.url_root

    try:
        user = current_app.db.users.find_user(data["email"])

        user_data = user.public_data()

        access_token = current_app.token.create_token(user_data)

        msg = Message()
        msg.subject = "Reset de password"
        msg.recipients = [data["email"]]
        msg.sender = 'Pladmed'
        msg.body = url_base + 'reset-password/' + access_token
        with current_app.app_context():
            mail = Mail()
            mail.send(msg)

        return make_response({"Mesage": "Message sent!"}, HTTP_OK)
    except Exception:
        print(traceback.format_exc())
        return error_response(HTTP_NOT_FOUND, "Invalid email or have a problem to send mail")

@auth.route('/reset-password/<string:reset_token>', methods=["POST"])
def reset(reset_token):
    data = request.get_json(force=True)

    try:
        if data["password"] == data["repassword"]:
            hash_pass = secure_password.hash(data["password"])

            token_data = current_app.token.identity(reset_token)

            user = current_app.db.users.find_user(token_data["email"])
            user_updated = current_app.db.users.change_password(user, hash_pass)

        return make_response({"Mesage": "Reset OK!"}, HTTP_OK)
    except:
        traceback.print_exc()
        return error_response(HTTP_NOT_FOUND, "Invalid token")
