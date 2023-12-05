from flask import render_template, url_for, flash, redirect, request
from melhem import app, db, bcrypt, socketio
from melhem.forms import RegistrationForm, LoginForm
from melhem.models import User, Rooms
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from time import localtime, strftime
from PIL import Image
import sklearn

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Input, Flatten, Dense, MaxPooling2D, Conv2D, Dropout
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.optimizers import SGD, RMSprop, Adam

import numpy as np
import pickle
import json
import os

with open('melhem/pharmacy/plants.json', 'r') as file:
    plants = json.load(file)
plants = plants["plants"]

def predict(values, dic):
    template_name = None
    # diabetes
    if len(values) == 8:
        template_name = "diabetes"
        func_name = "diabetes"
        illness_name = "Süýji keseli"
        dic2 = {'NewBMI_Obesity 1': 0, 'NewBMI_Obesity 2': 0, 'NewBMI_Obesity 3': 0, 'NewBMI_Overweight': 0,
                'NewBMI_Underweight': 0, 'NewInsulinScore_Normal': 0, 'NewGlucose_Low': 0,
                'NewGlucose_Normal': 0, 'NewGlucose_Overweight': 0, 'NewGlucose_Secret': 0}

        if dic['BMI'] <= 18.5:
            dic2['NewBMI_Underweight'] = 1
        elif 18.5 < dic['BMI'] <= 24.9:
            pass
        elif 24.9 < dic['BMI'] <= 29.9:
            dic2['NewBMI_Overweight'] = 1
        elif 29.9 < dic['BMI'] <= 34.9:
            dic2['NewBMI_Obesity 1'] = 1
        elif 34.9 < dic['BMI'] <= 39.9:
            dic2['NewBMI_Obesity 2'] = 1
        elif dic['BMI'] > 39.9:
            dic2['NewBMI_Obesity 3'] = 1

        if 16 <= dic['Insulin'] <= 166:
            dic2['NewInsulinScore_Normal'] = 1

        if dic['Glucose'] <= 70:
            dic2['NewGlucose_Low'] = 1
        elif 70 < dic['Glucose'] <= 99:
            dic2['NewGlucose_Normal'] = 1
        elif 99 < dic['Glucose'] <= 126:
            dic2['NewGlucose_Overweight'] = 1
        elif dic['Glucose'] > 126:
            dic2['NewGlucose_Secret'] = 1

        dic.update(dic2)
        values2 = list(map(float, list(dic.values())))

        model = pickle.load(open('melhem/models/diabetes.pkl','rb'))
        values = np.asarray(values2)
        # illness_name = "{{url_for('static', filename='Images/plants/anagal.jpg')}}"
        return illness_name, func_name, template_name, model.predict(values.reshape(1, -1))[0]

    # breast_cancer
    elif len(values) == 22:
        template_name = "breast-cancer"
        func_name = "breast_cancer"
        illness_name = "Kükrek rak keseli"

        model = pickle.load(open('melhem/models/breast_cancer.pkl','rb'))
        values = np.asarray(values)
        return illness_name, func_name, template_name, model.predict(values.reshape(1, -1))[0]

    # heart disease
    elif len(values) == 13:
        template_name = "heart"
        func_name = 'heart'
        illness_name = "Ýüregiň sagdynlygynyň"

        model = pickle.load(open('melhem/models/heart.pkl','rb'))
        values = np.asarray(values)
        prediction = model.predict(values.reshape(1, -1))[0]
        return illness_name, func_name, template_name, not prediction

    # kidney disease
    elif len(values) == 24:
        template_name = "kidney"
        func_name = 'kidney'
        illness_name = "Böwrek keseli"

        model = pickle.load(open('melhem/models/kidney.pkl','rb'))
        values = np.asarray(values)
        prediction = model.predict(values.reshape(1, -1))[0]
        return illness_name, func_name, template_name, not prediction

    # liver disease
    elif len(values) == 10:
        template_name = "liver"
        func_name = 'liver'
        illness_name = "Bagyr keseli"
        model = pickle.load(open('melhem/models/liver.pkl','rb'))
        values = np.asarray(values)
        return illness_name, func_name, template_name, model.predict(values.reshape(1, -1))[0]


ROOMS = ['Umumy Bejergi', 'Ýürek keselleri', 'Öýken keselleri', 'Ýokanç keselleri']

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/covid-19')
def covid_19():
    return render_template('covid.html')

@app.route('/pneumonia')
def pneumonia():
    return render_template('pneumonia.html')

@app.route('/malaria')
def malaria():
    return render_template('malaria.html')

@app.route('/breast-cancer')
def breast_cancer():
    return render_template('breast-cancer.html')

@app.route('/diabetes')
def diabetes():
    return render_template('diabetes.html')

@app.route('/heart')
def heart():
    return render_template('heart.html')

@app.route('/kidney')
def kidney():
    return render_template('kidney.html')

@app.route('/liver')
def liver():
    return render_template('liver.html')

@app.route('/advice')
def advice():
    return redirect('chats')


@app.route("/predict", methods = ['POST', 'GET'])
def predictPage():
    try:
        if request.method == 'POST':
            to_predict_dict = request.form.to_dict()

            for key, value in to_predict_dict.items():
                try:
                    to_predict_dict[key] = int(value)
                except ValueError:
                    to_predict_dict[key] = float(value)

            to_predict_list = list(map(float, list(to_predict_dict.values())))
            illness_name, func_name, template_name, pred = predict(to_predict_list, to_predict_dict)
            print("Prediction: ", pred)
    except:
        message = "Dogry maglumat girizmegiňizi haýyş edýäris!"
        return render_template("{}.html".format(template_name), message=message)

    return render_template('predict.html', pred=pred, template_name=template_name,
                    func_name=func_name, illness_name=illness_name, plants=plants)

@app.route("/pneumoniapredict", methods = ['POST', 'GET'])
def pneumoniapredictPage():
    if request.method == 'POST':
        try:
            # base model
            base_model = VGG19(include_top=False, input_shape=(128,128,3))
            x = base_model.output
            flat=Flatten()(x)
            class_1 = Dense(4608, activation='relu')(flat)
            drop_out = Dropout(0.2)(class_1)
            class_2 = Dense(1152, activation='relu')(drop_out)
            output = Dense(2, activation='softmax')(class_2)
            model = Model(base_model.inputs, output)

            img = Image.open(request.files['image'])
            img_path = os.path.join(os.path.dirname(__file__), 'uploads', request.files['image'].filename)
            img.save(img_path)
            os.path.isfile(img_path)
            # img = tf.keras.utils.load_img(img_path, target_size=(128, 128))
            # img = tf.keras.utils.img_to_array(img)

            img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128))
            img = tf.keras.preprocessing.image.img_to_array(img)
            img = np.expand_dims(img, axis=0)

            model.load_weights(filepath="melhem/models/pneumonia.h5")
            pred = np.argmax(model.predict(img))
            print("prediction result:", pred)
        except:
            message = "Haýyşt edýäris analiziň suratyny ýükläň!"
            return render_template('pneumonia.html', message=message)
        return render_template('pneumonia_predict.html', pred=pred, plants=plants)
    else:
        return redirect('pneumonia')

@app.route("/malariapredict", methods = ['POST', 'GET'])
def malariapredictPage():
    if request.method == 'POST':
        try:
            # Build the network
            base_model = VGG19(include_top=False, input_shape=(128,128,3))
            x = base_model.output
            flat=Flatten()(x)
            class_1 = Dense(4608, activation='relu')(flat)
            drop_out = Dropout(0.2)(class_1)
            class_2 = Dense(1152, activation='relu')(drop_out)
            output = Dense(2, activation='softmax')(class_2)
            model = Model(base_model.inputs, output)

            img = Image.open(request.files['image'])
            img_path = os.path.join(os.path.dirname(__file__), 'uploads', request.files['image'].filename)
            img.save(img_path)
            os.path.isfile(img_path)

            img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128))
            img = tf.keras.preprocessing.image.img_to_array(img)
            img = np.expand_dims(img, axis=0)

            # Load weights
            model.load_weights(filepath='melhem/models/malaria.h5')

            pred = np.argmax(model.predict(img))
        except:
            message = "Haýyşt edýäris analiziň suratyny ýükläň!"
            return render_template('malaria.html', message=message)
    return render_template('malaria_predict.html', pred=pred, plants=plants)

@app.route("/covidpredict", methods = ['POST', 'GET'])
def covidpredictPage():
    if request.method == 'POST':
        try:
            # base model
            base_model = VGG19(include_top=False, input_shape=(128,128,3))
            x = base_model.output
            flat=Flatten()(x)
            class_1 = Dense(4608, activation='relu')(flat)
            drop_out = Dropout(0.2)(class_1)
            class_2 = Dense(1152, activation='relu')(drop_out)
            output = Dense(2, activation='softmax')(class_2)
            model = Model(base_model.inputs, output)

            img = Image.open(request.files['image'])
            img_path = os.path.join(os.path.dirname(__file__), 'uploads', request.files['image'].filename)
            img.save(img_path)
            os.path.isfile(img_path)
            # img = tf.keras.utils.load_img(img_path, target_size=(128, 128))
            # img = tf.keras.utils.img_to_array(img)

            img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128))
            img = tf.keras.preprocessing.image.img_to_array(img)

            img = np.expand_dims(img, axis=0)

            model.load_weights(filepath="melhem/models/pneumonia.h5")
            pred = np.argmax(model.predict(img))
            print("prediction result:", pred)
        except:
            message = "Haýyşt edýäris analiziň suratyny ýükläň!"
            return render_template('covid.html', message=message)
        return render_template('covid_predict.html', pred=pred, plants=plants)
    else:
        return redirect('pneumonia')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if  form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, profile_photo=None, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Siz üstünlikli ýazga alyndyňyz!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Ýazga Alynmak', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Ulgama girme synanşygy başarnyksyz. Email ýa-da açar sözi barlaň!', 'danger')
    return render_template('login.html', title='Ulgama Gir', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# my custom modifications
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        db.session.rollback()
        user = User.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            try:
                img = Image.open(request.files['image'])
                img_path = os.path.join(os.path.dirname(__file__), 'static/uploads', request.files['image'].filename)
                img.save(img_path)
                # print(img_path)
                # os.path.isfile(img_path)
                img_path_db = os.path.join('static/uploads', request.files['image'].filename)
                user.profile_photo = img_path_db
                db.session.commit()
            except:
                message = "Haýyşt edýäris suratyňyzy täzeden ýükläň!"
                return render_template('account.html', message=message)
        return render_template('account.html', title='Account')

@app.route('/chats')
def chats():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.is_authenticated:
        userList = User.query.all()
        return render_template('chats.html', roomList = ROOMS, room = 'global chat', userList = userList)
    return render_template('chats.html', roomList = ROOMS, room = 'global chat')

@app.route('/about')
def about():
    return render_template("about.html")




''' SOCKET.IO EVENTS '''

@socketio.on('message')
def handleMessage(msg):
    msgDict = json.loads(msg)
    msgToDeliver = {'sender':msgDict['sender'], 'receiver':msgDict['receiver'], 'content':msgDict['content'], 'timestamp':strftime("%I:%M %p", localtime()), 'room':msgDict['room']}
    print("\n\n{}\n\n".format(msgDict))
    if(msgDict['room'] == 'GLOBAL'):
        send(json.dumps(msgToDeliver), broadcast=True)
    elif msgDict['room'].lower() in ROOMS:
        send(json.dumps(msgToDeliver), room = msgToDeliver['room'])
    elif msgDict['room'].lower() not in ROOMS:    # One-to-one
        # roomname1 = msgDict['receiver'] + '_' + msgDict['sender']
        row1 = Rooms.query.filter_by(roomname=msgDict['room']).first()
        # row2 = Rooms.query.filter_by(roomname=roomname1).first()
        print("Message from {} to {}".format(msgDict['sender'], msgDict['receiver']))
        if row1:
            row = row1
        # if row2:
            # row = row2
        else:
            print("/nerror in handle message/n")
            return
        row.count = row.count + 1
        print("row.count:", row.count)
        print("row.message", row.message)
        dict1 = json.loads(row.message)

        dict1[row.count] = msgDict
        row.message = json.dumps(dict1)
        db.session.commit()
        send(json.dumps(msgToDeliver), room = msgToDeliver['room'])


@socketio.on('join')
def join(data):
    data = json.loads(data)
    print('\n\n', data)
    join_room(data['room'])
    msgToDeliver = {
        'sender':'SYSTEM',
        'content':"{} ulgamda..".format(data['sender'], data['room']),
        'timestamp':strftime('%I:%M %p', localtime())
    }
    send(json.dumps(msgToDeliver), room = data['room'])

@socketio.on('leave')
def leave(data):
    data = json.loads(data)
    print('\n\n', data)
    leave_room(data['room'])
    msgToDeliver = {
        'sender':'SYSTEM',
        'content':"{} has left {}".format(data['sender'], data['room']),
        'timestamp':strftime('%I:%M %p', localtime())
    }
    send(json.dumps(msgToDeliver), room = data['room'])

@socketio.on('connect')
def connect():
    user = User.query.filter_by(username = current_user.username).first()
    user.last_sid = request.sid
    db.session.commit()
    # user.updateSessionID(request.sid)
    print('\n\n', user)



@socketio.on('request_for_connection')
def request_for_connection(request):
    request = json.loads(request)
    print('\n\n', request)
    # Search for recepient of request, named as recipient
    recipient = User.query.filter_by(username = request['to']).first()
    print("\n\nIn request_for_connection:\n{}\n\n".format(recipient))
    emit('request_to_connect', json.dumps(request), room = recipient.last_sid)

@socketio.on('accept_request')
def accept_request(accept_msg):
    accept_msg = json.loads(accept_msg)
    print('\n\n', accept_msg)
    # Search for sender's entry and use his sid to deliver the request acceptance
    sender = User.query.filter_by(username = accept_msg['sender']).first()
    emit('request_accepted', json.dumps(accept_msg), room = sender.last_sid)


@socketio.on('make_new_room')
def make_new_room(room_name):
    room_name = json.loads(room_name)
    # room_name1 = room_name['receiver'] + '_' + room_name['sender']
    # row1 = Rooms.query.filter_by(roomname=room_name1).first()
    row2 = Rooms.query.filter_by(roomname=room_name['room']).first()
    if not row2:
        row = Rooms(roomname=room_name['room'])
        db.session.add(row)
        db.session.commit()
    # elif row1:
        # emit('load_history', row1.message, room=row1.roomname)
    elif row2:
        emit('load_history', row2.message, room=row2.roomname)
    else:
        print("/nNot a new room/n")
