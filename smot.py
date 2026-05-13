#!/usr/bin/env python3
"""SMOT-KNOWLEDGE — Remote Launcher per Mac via tunnel SSH Cat 7."""

import os, sys, time, subprocess, argparse, signal, webbrowser

DEFAULT_USER = "michele-finocchiaro"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
REMOTE_DIR = "/home/michele-finocchiaro/SMOT-KNOWLEDGE"

class C:
    BOLD = "\033[1m"; DIM = "\033[2m"
    GREEN = "\033[92m"; YELLOW = "\033[93m"; CYAN = "\033[96m"; RED = "\033[91m"
    RESET = "\033[0m"

def info(msg):  print(f"  {C.CYAN}▶{C.RESET} {msg}")
def ok(msg):    print(f"  {C.GREEN}✓{C.RESET} {msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠{C.RESET} {msg}")
def fail(msg):  print(f"  {C.RED}✗{C.RESET} {msg}")

def ssh(host, cmd, timeout=15):
    c = ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
         "-o", "BatchMode=yes", f"{DEFAULT_USER}@{host}", cmd]
    try:
        r = subprocess.run(c, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -2, "", "ssh non trovato"

def verify_ssh(host):
    print(f"\n  Verifica tunnel SSH verso {host}...", end=" ", flush=True)
    rc, out, err = ssh(host, "echo pong")
    if rc != 0:
        print(f"{C.RED}✗{C.RESET}")
        fail(f"SSH: {host} — {err}")
        return False
    print(f"{C.GREEN}✓{C.RESET}")
    ok(f"SSH: {host} — tunnel via cavo Cat 7")
    return True

def remote_check(host):
    st = {"backend": False, "frontend": False}
    rc, out, _ = ssh(host, f"curl -sf http://localhost:{BACKEND_PORT}/api/health && echo OK")
    st["backend"] = rc == 0 and "OK" in out
    rc, out, _ = ssh(host, "ps aux | grep vite | grep -v grep | head -1")
    st["frontend"] = rc == 0 and bool(out)
    return st

def install_deps(host):
    info("Installazione dipendenze backend...")
    rc, out, _ = ssh(host, f"cd {REMOTE_DIR}/backend && pip3 install --break-system-packages -r requirements.txt -q", timeout=90)
    if rc == 0:
        ok("Dipendenze backend installate")
        return True
    fail(f"Installazione fallita:\n{out[:200]}")
    return False

def start_backend(host):
    info("Avvio backend...")
    ssh(host, f"cd {REMOTE_DIR}/backend && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port {BACKEND_PORT} > /tmp/smot-backend.log 2>&1 < /dev/null &", timeout=10)
    for i in range(8):
        time.sleep(2)
        if remote_check(host)["backend"]:
            ok("Backend avviato")
            return True
    rc, out, _ = ssh(host, "tail -30 /tmp/smot-backend.log")
    fail(f"Backend non parte — log:\n{out}")
    return False

def start_frontend(host):
    info("Avvio frontend...")
    ssh(host, f"cd {REMOTE_DIR}/frontend && nohup npm run dev > /tmp/smot-frontend.log 2>&1 < /dev/null &", timeout=10)
    for i in range(8):
        time.sleep(2)
        if remote_check(host)["frontend"]:
            ok("Frontend avviato")
            return True
    rc, out, _ = ssh(host, "tail -30 /tmp/smot-frontend.log")
    fail(f"Frontend non parte — log:\n{out}")
    return False

def start_tunnel(host):
    info("Port forwarding SSH...")
    cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
           "-o", "ServerAliveInterval=30",
           "-L", f"{BACKEND_PORT}:localhost:{BACKEND_PORT}",
           "-L", f"{FRONTEND_PORT}:localhost:{FRONTEND_PORT}",
           "-N", f"{DEFAULT_USER}@{host}"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        if proc.poll() is None:
            ok(f"Tunnel: localhost:{BACKEND_PORT}  ↔  {host}:{BACKEND_PORT}")
            return proc
        fail(f"Tunnel fallito (exit {proc.returncode})")
        return None
    except FileNotFoundError:
        fail("ssh non trovato")
        return None

def stop_tunnel(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

def open_browser():
    url = f"http://localhost:{FRONTEND_PORT}"
    info(f"Apro browser: {url}")
    try:
        webbrowser.open(url)
        ok("Browser aperto")
    except Exception:
        warn("Apri: " + url)

def main():
    global DEFAULT_USER
    p = argparse.ArgumentParser(description="SMOT-KNOWLEDGE — Remote Launcher")
    p.add_argument("--host", help="IP server Linux (es. 10.0.0.2)")
    p.add_argument("--local", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--user", default="", help=f"SSH user (default: {DEFAULT_USER})")
    args = p.parse_args()
    if args.user:
        DEFAULT_USER = args.user
    if not args.local and not args.host:
        fail("Specifica IP: python3 smot.py --host 10.0.0.2")
        sys.exit(1)
    if not args.local and not verify_ssh(args.host):
        sys.exit(1)
    print()

    if args.local:
        info("Modalità locale — avvia backend e frontend manualmente")
        return

    st = remote_check(args.host)
    for k, v in st.items():
        (ok if v else warn)(f"{k}: {'attivo' if v else 'non attivo'}")
    if args.status:
        return

    need_deps = False
    if not st["backend"]:
        rc, out, _ = ssh(args.host, "python3 -c 'import fastapi, uvicorn, httpx, lancedb' 2>&1")
        if rc != 0:
            need_deps = True

    if need_deps:
        if not install_deps(args.host):
            sys.exit(1)

    if not st["backend"]:
        start_backend(args.host)
    if not st["frontend"]:
        start_frontend(args.host)

    st2 = remote_check(args.host)
    if not st2["backend"]:
        fail("Backend non partito")
        sys.exit(1)

    tunnel = start_tunnel(args.host)
    if not tunnel:
        sys.exit(1)

    open_browser()
    print(f"\n  {C.BOLD}⚡ SMOT-KNOWLEDGE attivo{C.RESET}")
    print(f"  {C.DIM}Chat:   {C.CYAN}http://localhost:{FRONTEND_PORT}{C.RESET}")
    print(f"  {C.DIM}Premi Ctrl+C per fermare{C.RESET}\n")
    try:
        while True:
            time.sleep(1)
            if tunnel.poll() is not None:
                fail("Tunnel perso")
                break
    except KeyboardInterrupt:
        print()
    stop_tunnel(tunnel)
    ok("Fermo.")

if __name__ == "__main__":
    main()
