import os
from typing import List, Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

import threading

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except Exception:
    raise RuntimeError("yt-dlp no está instalado. Asegúrate de incluirlo en requirements.txt")

APP_STORAGE = os.environ.get("APP_STORAGE", "/data")
os.makedirs(APP_STORAGE, exist_ok=True)

# Plantillas
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"]))

app = FastAPI(title="YouTube Downloader (yt-dlp)")

# Lista de descargas actuales (demo)
download_threads = {}  # url -> threading.Thread


def listar_archivos() -> List[str]:
    files = []
    for name in sorted(os.listdir(APP_STORAGE)):
        path = os.path.join(APP_STORAGE, name)
        if os.path.isfile(path):
            files.append(name)
    return files


def build_opts(destino: str, solo_audio: bool = False):
    formato = "bestaudio/best" if solo_audio else "bv*+ba/b"
    postprocessors = []
    merge_fmt = None
    if solo_audio:
        postprocessors = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        merge_fmt = "mp4"

    ydl_opts = {
        "paths": {"home": destino},
        "outtmpl": "%(title).200s.%(ext)s",
        "windowsfilenames": True,
        "format": formato,
        "merge_output_format": merge_fmt,
        "extractor_args": {"youtube": {"player_client": "web"}},
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://www.youtube.com/",
        },
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
        "concurrent_fragment_downloads": 4,
        "skip_unavailable_fragments": True,
        "overwrites": True,
        "trim_file_name": 200,
        "force_ipv4": True,
        "noprogress": False,
        "postprocessors": postprocessors,
    }
    return ydl_opts


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    files = listar_archivos()
    template = env.get_template("index.html")
    return template.render(files=files)


@app.post("/download")
async def download(url: str = Form(...), solo_audio: Optional[bool] = Form(False)):
    if not url:
        raise HTTPException(400, detail="Falta URL")

    def _job():
        ydl_opts = build_opts(APP_STORAGE, solo_audio=bool(solo_audio))
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
        except DownloadError as e:
            print(f"[yt-dlp] Error: {e}")
        except Exception as e:
            print(f"[app] Error inesperado: {e}")
        finally:
            download_threads.pop(url, None)

    if url not in download_threads:
        t = threading.Thread(target=_job, daemon=True)
        download_threads[url] = t
        t.start()

    return RedirectResponse("/", status_code=303)


@app.get("/files/{name}")
async def get_file(name: str):
    path = os.path.join(APP_STORAGE, name)
    if not os.path.isfile(path):
        raise HTTPException(404, detail="No encontrado")
    return FileResponse(path, filename=name)


@app.post("/delete")
async def delete(name: str = Form(...)):
    path = os.path.join(APP_STORAGE, name)
    if os.path.isfile(path):
        os.remove(path)
    else:
        raise HTTPException(404, detail="No encontrado")
    return RedirectResponse("/", status_code=303)
