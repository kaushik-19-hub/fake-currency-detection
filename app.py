import os
import sqlite3
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms
from flask import Flask, render_template, request, redirect, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.secret_key = "super_secret_key"

DATABASE = "database.db"
UPLOAD_FOLDER = "static/uploads"
MODEL_PATH = "efficientnet_b3_banknote_best2.pth"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

def build_model():
    model = models.efficientnet_b3(weights=None)
    model.classifier = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(1536,256),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256,2)
    )
    return model

model = None
try:
    model = build_model()
    state_dict = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
    model.load_state_dict(state_dict)
    model.eval()
    print("Model loaded successfully")
except Exception as e:
    print("Model loading error:", e)

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def predict_currency(image_path):

    if model is None:

        return "Model Error", 0

    image = Image.open(image_path).convert("RGB")

    image = transform(image).unsqueeze(0)

    with torch.no_grad():

        output = model(image)

        probs = torch.softmax(output, dim=1)

        confidence, pred = torch.max(probs, 1)

        confidence = round(confidence.item()*100,2)

        result = "Fake" if pred.item()==0 else "Real"

    return result, confidence

def login_required():
    return "user_id" in session

@app.route("/")
def root():
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        confirm_password=request.form["confirm_password"]
        if password!=confirm_password:
            flash("Passwords do not match")
            return redirect("/register")
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? OR email=?",(username,email))
        existing=cursor.fetchone()
        if existing:
            conn.close()
            flash("User already exists")
            return redirect("/register")
        password_hash=generate_password_hash(password)
        cursor.execute("INSERT INTO users (username,email,password_hash,role) VALUES (?,?,?,?)",
                       (username,email,password_hash,"user"))
        conn.commit(); conn.close()
        flash("Registration successful")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user=cursor.fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"]=user["id"]
            session["username"]=user["username"]
            session["role"]=user["role"]
            return redirect("/home")
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/forgot_password", methods=["GET","POST"])
def forgot_password():
    if request.method=="POST":
        username=request.form["username"]
        new_password=request.form["new_password"]
        confirm_password=request.form["confirm_password"]
        if new_password!=confirm_password:
            flash("Passwords do not match")
            return redirect("/forgot_password")
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user=cursor.fetchone()
        if not user:
            conn.close()
            flash("User not found")
            return redirect("/forgot_password")
        password_hash=generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash=? WHERE username=?",
                       (password_hash, username))
        conn.commit(); conn.close()
        flash("Password updated")
        return redirect("/login")
    return render_template("forgot_password.html")

@app.route("/home")
def home():
    if not login_required():
        return redirect("/login")
    return render_template("home.html")

@app.route("/detect")
def detect():
    if not login_required():
        return redirect("/login")
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM detection_history WHERE user_id=? ORDER BY id DESC",
                   (session["user_id"],))
    history=cursor.fetchall()
    conn.close()
    return render_template("detect.html", history=history)

@app.route("/predict", methods=["POST"])
def predict():
    if not login_required():
        return jsonify({"error":"Unauthorized"})
    if "image" not in request.files:
        return jsonify({"error":"No image"})
    image=request.files["image"]
    filename=secure_filename(image.filename)
    filepath=os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)
    result, confidence = predict_currency(filepath)
    image_path="/" + filepath.replace("\\","/")
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO detection_history (user_id,image_path,result,confidence_score) VALUES (?,?,?,?)",
                   (session["user_id"], image_path, result, confidence))
    conn.commit(); conn.close()
    return jsonify({"result":result, "confidence":confidence})

@app.route("/capture_mobile", methods=["POST"])
def capture_mobile():
    if not login_required():
        return jsonify({"error": "Unauthorized"})

    data = request.json["image"]
    encoded = data.split(",")[1]

    filename = "mobile_capture.png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(encoded))

    result, confidence = predict_currency(filepath)

    image_path = "/" + filepath.replace("\\", "/")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO detection_history (user_id,image_path,result,confidence_score) VALUES (?,?,?,?)",
        (session["user_id"], image_path, result, confidence)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "result": result,
        "confidence": confidence
    })

@app.route("/delete_history/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    if not login_required():
        return jsonify({"success":False})
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM detection_history WHERE id=? AND user_id=?",
                   (history_id, session["user_id"]))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route("/admin")
def admin():
    if not login_required():
        return redirect("/login")
    if session["role"] != "admin":
        abort(403)
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM users")
    users=cursor.fetchall()
    cursor.execute("SELECT * FROM detection_history ORDER BY id DESC")
    logs=cursor.fetchall()
    conn.close()
    return render_template("admin.html", users=users, logs=logs)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if session["role"]!="admin":
        abort(403)
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND username!='admin'", (user_id,))
    conn.commit(); conn.close()
    return redirect("/admin")

@app.route("/delete_log/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    if session["role"]!="admin":
        abort(403)
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM detection_history WHERE id=?", (log_id,))
    conn.commit(); conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
