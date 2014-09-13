import os
from contextlib import closing

from sqlite3 import dbapi2 as sqlite3

from werkzeug import secure_filename

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_from_directory

from www.jukenode.mongo_models import *


app = Flask(__name__)
app.config.from_object('settings')

audio_upload = dict(
    name='audios',
    extensions=('mp3', 'wav'),
)


@app.route('/audio/play/<file_id>')
def audio_play(file_id):
    doc = AUD.get(file_id=file_id)
    return AUD.send_flask_file(doc)

@app.route('/audio/delete', methods=['POST'])
def audio_delete():
    if request.method == 'POST':
        file_id = request.form.get('file_id')
        AUD.delete(file_id=file_id)
    return redirect(url_for('upload_audio_list'))

@app.route('/audio/upload', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST':
        audio = request.files['file']
        _id = AUD.save_flask_upload(audio)
        return redirect(url_for('upload_audio_list'))

    return '''
    <!doctype html>
    <title>Upload audio file</title>
    <h1>Upload Audio</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''



@app.route('/audio/list')
def upload_audio_list():
    media_list = AUD.list()
    return render_template('media/index.html', media_list=media_list)


@app.route('/')
def show_nodes():
    cur = NOD.find()
    nodes = list(cur)
    return render_template('show_nodes.html', nodes=nodes)


@app.route('/node/add', methods=['POST'])
def add_node():
    if not session.get('logged_in'):
        abort(401)
    node = dict(
        (key, val) for key, val in request.form.items()
    )
    NOD.col.update(
        {"node_name": node['node_name']},
        node,
        upsert=True
    )
    flash('saved: %s' % node['node_name'])
    return redirect(url_for('show_nodes'))

@app.route('/node/remove', methods=['POST'])
def remove_node():
    if not session.get('logged_in'):
        abort(401)

    node_name = request.form.get('node_name')
    NOD.col.remove({'node_name': node_name})
    flash('removed: %s' % node_name)
    return redirect(url_for('show_nodes'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_nodes'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(use_reloader=False)
