import os
import sys

# Ensure backend directory is in sys.path whether executed from root or backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "backend":
    sys.path.insert(0, current_dir)
else:
    backend_dir = os.path.join(current_dir, "backend")
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)

# Enforce essential Linux container memory bounds
os.environ.setdefault("MALLOC_ARENA_MAX", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
# Prevent Uvicorn from starting a supervisor process
os.environ.pop("WEB_CONCURRENCY", None)

print("=" * 60, flush=True)
print(">>> [AI Data Center ML] Initializing FastAPI service...", flush=True)
print(f">>> [AI Data Center ML] Python version: {sys.version.split()[0]}", flush=True)
print(f">>> [AI Data Center ML] Working directory: {os.getcwd()}", flush=True)
print("=" * 60, flush=True)

if __name__ == "__main__":
    import uvicorn

    port_str = os.environ.get("PORT", "10000").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 10000

    print(f">>> [AI Data Center ML] Binding Uvicorn to 0.0.0.0:{port}...", flush=True)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info",
        timeout_keep_alive=75,
    )
