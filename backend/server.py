from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local
from backend.services.mailer import EmailTLDR

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/")
async def health_check():
    return {"ping": "pong"}


@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    try:
        email_tldr_instance = EmailTLDR(email, password)
        email_tldr_instance.summarize_and_send()
        return {"success": True, "error": None}
    except Exception as ex:
        return {"success": False, "error": str(ex)}
