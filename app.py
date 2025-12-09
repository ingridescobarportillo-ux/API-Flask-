import requests
from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from datetime import timedelta

from routes.routes import rutas
from models.db_mdl import valida_usuario

app = Flask(__name__, template_folder='templates')
app.register_blueprint(rutas, url_prefix="/api")

app.secret_key = "CAMBIA_ESTA_CLAVE"
app.permanent_session_lifetime = timedelta(minutes=30)

RECAPTCHA_SECRET_KEY = "6LfhqiMsAAAAAKDf_DA8IX2Y2pEuWb355QZB08U5"


# ----------------------------------------------------
# RUTA PRINCIPAL
# ----------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ----------------------------------------------------
# LOGIN (GET + POST)
# ----------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # Validar CAPTCHA
    captcha_response = request.form.get('g-recaptcha-response')

    if not captcha_response:
        return render_template("login.html", message="Debes completar el captcha.")

    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': captcha_response
    }

    validation = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data).json()

    if not validation.get("success"):
        return render_template("login.html", message="Captcha incorrecto. Intenta de nuevo.")

    # Validar usuario
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        user = valida_usuario(username, password)

        if user:
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.usuario
            session["api_key"] = user.api_key
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", message="Usuario o contraseña incorrectos.")

    except Exception as e:
        print("Error en login:", e)
        return render_template("login.html", message="Error interno. Consulte al administrador.")


# ----------------------------------------------------
# DASHBOARD
# ----------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# ----------------------------------------------------
# LOGOUT
# ----------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------------------------------------------
# EJECUTAR SERVIDOR
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)