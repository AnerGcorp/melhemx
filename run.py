from melhem import app, socketio, db

if __name__ == '__main__':
    db.create_all()
    db.session.commit()
    socketio.run(app, host='0.0.0.0', port=5100, debug=True)
