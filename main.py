from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, uuid, shutil

app = FastAPI()

# Static files (imagenes)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# "Base de datos" temporal (memoria)
WARDROBE = []

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "items": WARDROBE}
    )

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/{filename}"

@app.post("/add")
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    img_solo: UploadFile = File(...),
    img_worn: UploadFile = File(...),
):
    solo_url = save_upload(img_solo)
    worn_url = save_upload(img_worn)

    WARDROBE.append({
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "category": category,
        "img_solo": solo_url,
        "img_worn": worn_url,
    })

    return RedirectResponse("/", status_code=303)
