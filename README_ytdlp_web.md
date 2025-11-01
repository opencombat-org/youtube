# ytdlp-web (FastAPI)

Interfaz web minimalista para descargar videos (o audio) con **yt-dlp**. Incluye borrado de archivos desde la UI.

## Ejecución local

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r web/ytdlp/requirements.txt
export APP_STORAGE=./downloads
uvicorn web.ytdlp.main:app --reload
```

## Docker

```bash
docker build -t ytdlp-web -f web/ytdlp/Dockerfile .
docker run -p 8080:8080 -v $(pwd)/downloads:/data ytdlp-web
```

Abre: http://localhost:8080

## Kubernetes (microk8s)

```bash
microk8s kubectl apply -f k8s/ytdlp/pvc.yaml
microk8s kubectl apply -f k8s/ytdlp/deployment.yaml
microk8s kubectl apply -f k8s/ytdlp/service.yaml
microk8s kubectl apply -f k8s/ytdlp/ingress.yaml
```

Habilita el addon de ingress si hace falta:

```bash
microk8s enable ingress
```

Asegura DNS apuntando a tu IP pública para `youtube.able256.com`.

## Notas

- El contenedor usa `/data` para almacenar los ficheros descargados.
- Para TLS en microk8s, crea un secret y descomenta la sección `tls` del Ingress.
