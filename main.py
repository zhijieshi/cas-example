from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from cas import CASClient
import uvicorn

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="replace-with-a-secure-secret")
templates = Jinja2Templates(directory="templates")

# UConn CAS configuration
cas_client = CASClient(
    version='3',
    service_url='http://localhost:8000/login',
    server_url='https://login.uconn.edu/cas/login'
)

@app.get("/", name="home")
async def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(
        request=request, name="home.html", context={"user": user}
    )

@app.get("/login")
async def login(request: Request, ticket: str | None = None):
     # If CAS redirected back with a ticket
    if ticket:
        user, attributes, pgtiou = cas_client.verify_ticket(ticket)
        request.session["user"] = user
        request.session["attributes"] = attributes
        print("CAS attributes:", attributes)
        return RedirectResponse(url=request.url_for("home"))

    # Otherwise redirect to UConn CAS login
    return RedirectResponse(url=cas_client.get_login_url())

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url=cas_client.get_logout_url(
            redirect_url=request.url_for("home")
        )
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

