from flask_mail import Mail, Message

mail_manager = Mail()


def send_email(to, subject, message):
    msg = Message(
        subject,
        recipients=[to],
        html=message,
    )
    mail_manager.send(msg)
