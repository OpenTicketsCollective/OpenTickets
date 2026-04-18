import subprocess
import sys

# Run hypercorn (plain HTTP, no certs - nginx handles HTTPS)
cmd = [
    sys.executable, "-m", "hypercorn",
    "backend:app",
    "--reload",
    "--bind", "0.0.0.0:8000",
]

subprocess.run(cmd)
