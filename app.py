from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from flask_login import login_required, login_user, current_user, logout_user
import hashlib
import os
from flask_compress import Compress
import time
import shutil
import _thread as thread
import html
from App.database_models import db, User, File, Receiver
from App.mail_manager import mail_manager, send_email
from App.administrator import admin, basic_auth
from App.login_maneger import login_manager
from config import BaseConfig
from gevent import pywsgi


app = Flask(__name__)

app.config.from_object(BaseConfig)

db.init_app(app)
basic_auth.init_app(app)
mail_manager.init_app(app)
admin.init_app(app)

Compress(app)

login_manager.init_app(app)


def hash_password(password):
    return hashlib.md5((password + app.config['PASSWORD_SALT']).encode('utf-8')).hexdigest()


@app.route('/')
def handle_index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if current_user.is_authenticated:
        return render_template('please_logout.html')

    if request.method == 'GET':
        return render_template('login.html')

    email = html.escape(request.form['email'])
    password = html.escape(request.form['password'])

    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
        return render_template('login.html', email=email, message='Login failed')

    if request.form.get("remember-me"):
        login_user(user, remember=True)
    else:
        login_user(user, remember=False)

    return redirect(url_for('handle_index'))


@app.route('/logout')
@login_required
def handle_logout():
    logout_user()
    return render_template('logout.html')


def create_file_name():
    return hashlib.md5((current_user.email + str(time.time())).encode('utf-8')).hexdigest()


def human_readable_file_size(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def create_download_link(file_name, receiver_email):
    return hashlib.md5((file_name + receiver_email).encode('utf-8')).hexdigest()


@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def handle_upload_file():
    if request.method == 'GET':
        return render_template('upload_file.html')

    emails = html.escape(request.form['emails']).split(',')
    message = html.escape(request.form['message'])[0:1023]

    # create a unique file name
    file_name = create_file_name()
    temp_path = app.config['TEMPORARY_FOLDER'] + '/' + file_name
    path = app.config['ARCHIVES_FOLDER'] + '/' + file_name

    # create a temporary folder to save the files
    os.mkdir(temp_path)

    # try to save the files
    try:
        files = request.files.getlist("files[]")
        file_number = len(files)
        for file in files:
            file.save(temp_path + '/' + file.filename)
    except Exception as e:
        print(e)
        return 'Upload fail'

    # archive folder
    shutil.make_archive(path, 'zip', temp_path)

    # get archive size
    file_size = os.path.getsize(path + '.zip')

    # delete temporary folder
    shutil.rmtree(temp_path)

    # create data base row
    file = File(current_user.id, file_name, message)
    file.files = file_number
    file.size = file_size
    db.session.add(file)

    # commit to obtain File id
    db.session.commit()

    for receiver_email in emails:
        token = create_download_link(file_name, receiver_email)
        download_url = url_for('handle_download_file', token=token, _external=True)

        receiver = Receiver(file.id, token, receiver_email)
        db.session.add(receiver)

        try:
            text = render_template('emails/you_received_some_files.html',
                                   username=current_user.username,
                                   sender_email=current_user.email,
                                   download_url=download_url,
                                   file_number=file_number,
                                   file_size=human_readable_file_size(file_size),
                                   delete_time=time.ctime(time.time() + app.config['FILE_FILE_SPAN']),
                                   message=message
                                   )
            subject = current_user.username + ' send you some files'
            send_email(receiver_email, subject, text)
        except Exception as e:
            print(e)

    # save Receivers to data base
    db.session.commit()

    subject = 'Your files has been sent'
    message = render_template('emails/file_sent.html',
                              receivers=emails,
                              file_number=file_number,
                              file_size=human_readable_file_size(file_size),
                              delete_time=time.ctime(time.time() + app.config['FILE_FILE_SPAN']),
                              message=message
                              )
    send_email(current_user.email, subject, message)

    return 'Successful send'


@app.route('/download_file/<token>', methods=['GET', 'POST'])
def handle_download_file(token):
    receiver = Receiver.query.filter_by(token=token).first()
    if receiver is None:
        return render_template('download_file.html',
                               message='Link is invalid or has expired')

    file = File.query.filter_by(id=receiver.file_id).first()
    if file is None:
        return render_template('download_file.html',
                               message='Link is invalid or has expired')

    sender = User.query.filter_by(id=file.user_id).first()
    if sender is None:
        return render_template('download_file.html',
                               message='Link is invalid or has expired')

    if request.method == 'POST':
        if receiver.downloaded_file is False:
            try:
                subject = receiver.email + ' downloaded your files'
                message = render_template('emails/receiver_downloaded_your_file.html',
                                          receiver=receiver.email,
                                          file_size=human_readable_file_size(file.size),
                                          file_number=file.files,
                                          message=file.message)
                send_email(sender.email, subject, message)
                receiver.downloaded_file = True
                db.session.commit()
            except Exception as e:
                print(e)
        return send_from_directory(app.config['ARCHIVES_FOLDER'], file.file_name + '.zip')

    return render_template('download_file.html',
                           message=file.message)


def automatic_delete_old_files(app: Flask):
    with app.app_context():
        folder = app.config['ARCHIVES_FOLDER']
        while 1:
            print('delete old files process running')
            try:
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    creation_time = os.path.getmtime(file_path)
                    print(time.time() - creation_time)
                    if time.time() - creation_time > app.config['FILE_FILE_SPAN']:
                        os.remove(file_path)
                        # clear database
                        db.session.commit()
                        db_file = File.query.filter_by(file_name=file.replace('.zip', '')).first()
                        db_receiver = Receiver.query.filter_by(file_id=db_file.id).first()
                        db.session.delete(db_file)
                        db.session.delete(db_receiver)
                        db.session.commit()
                        # log event
                        print('Deleted file - ' + file)
            except Exception as e:
                print(e)
            time.sleep(10 * 60)


if __name__ == '__main__':
    db.create_all(app=app)
    thread.start_new_thread(automatic_delete_old_files, (app, ))

    http_server = pywsgi.WSGIServer((app.config['SERVER_IP'], app.config['SERVER_PORT']), app)
    http_server.serve_forever()
