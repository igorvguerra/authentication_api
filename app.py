from flask import Flask, request, jsonify
from database import db
from models.user import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Authentication sucessfully completed."})
    
    return jsonify({"message": "Invalid credentials."}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User sucessfully Logout."})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Registration successful."})

    return jsonify({"message": "Invalid data."}), 400


@app.route('/user/<int:id_user>', methods={'GET'})
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}
    
    return jsonify({"message": "User not found."}), 404


@app.route('/user/<int:id_user>', methods={'PUT'})
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id and current_user.role == "user":
        return jsonify({"message": "Access denied."}), 403

    if user and data.get("password"):
        user.password = data.get("password")
        
        db.session.commit()

        return jsonify({"message": f"User {id_user} password was sucessfully updated."})
    
    return jsonify({"message": "User not found."}), 404


@app.route('/user/<int:id_user>', methods={'DELETE'})
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)
    
    if current_user.role != 'admin':
        return jsonify({"message": "Access denied."}), 403
    
    if id_user == current_user.id:
        return jsonify({"message": "Current user is not allowed to delete itself."}), 403
    
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {id_user} deleted."})
    
    return jsonify({"message": "User not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)