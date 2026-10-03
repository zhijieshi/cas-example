from flask import Flask, redirect, request, session, url_for, render_template
from cas import CASClient

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-secret"

# UConn CAS configuration
cas_client = CASClient(
    version='3',
    service_url='http://localhost:5000/login',
    server_url='https://login.uconn.edu/cas/login'
)

@app.route("/")
def home():
    user = session.get("user")
    return render_template("home.html", user=user)

@app.route("/login")
def login():
    ticket = request.args.get("ticket")

    # If CAS redirected back with a ticket
    if ticket:
        user, attributes, pgtiou = cas_client.verify_ticket(ticket)
        session["user"] = user
        session["attributes"] = attributes
        print("CAS attributes:", attributes)
        return redirect(url_for("home"))

    # Otherwise redirect to UConn CAS login
    return redirect(cas_client.get_login_url())

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        cas_client.get_logout_url(
            redirect_url=url_for("home", _external=True)
        )
    )

if __name__ == "__main__":
    app.run(debug=True)

