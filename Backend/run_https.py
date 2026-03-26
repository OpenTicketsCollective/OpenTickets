import subprocess
import sys
from pathlib import Path

# Get paths
backend_dir = Path(__file__).parent
root_dir = backend_dir.parent
cert_file = root_dir / "cert.pem"
key_file = root_dir / "key.pem"

# Verify certificates exist
if not cert_file.exists():
    print(f"[ERROR] Certificate file not found: {cert_file}")
    sys.exit(1)
if not key_file.exists():
    print(f"[ERROR] Key file not found: {key_file}")
    sys.exit(1)

print(f"[OK] Starting HTTPS backend on https://127.0.0.1:8000")
print(f"[OK] Using certificates from {root_dir}")

# Run uvicorn with SSL
cmd = [
    sys.executable, "-m", "uvicorn",
    "backend:app",
    "--reload",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--ssl-keyfile", str(key_file),
    "--ssl-certfile", str(cert_file),
]

subprocess.run(cmd, cwd=backend_dir)
