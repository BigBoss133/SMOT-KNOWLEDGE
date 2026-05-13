#!/usr/bin/env python3
"""
SMOT-KNOWLEDGE — Remote Launcher per Mac

Connessione SSH via cavo Cat 7 al server Linux con GPU.
Avvio automatico backend/frontend, port forwarding, browser.
Un solo modello, un solo comando.

Uso:
  python3 smot.py --host 192.168.1.100
  python3 smot.py --host 192.168.1.100 --status
  python3 smot.py --local
"""

import os
import sys
import time
import json
import signal
import socket
import subprocess
import argparse
import urllib.request
import webbrowser

# ─── Default ──────────────────────────────────────────────────

DEFAULT_USER = "michele-finocchiaro"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
REMOTE_DIR = "/home/michele-finocchiaro/SMOT-KNOWLEDGE"

# ─── Colori ANSI ──────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"


def info(msg):  print(f"  {C.CYAN}▶{C.RESET} {msg}")
def ok(msg):    print(f"  {C.GREEN}✓{C.RESET} {msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠{C.RESET} {msg}")
def fail(msg):  print(f"  {C.RED}✗{C.RESET} {msg}")


# ─── SSH ──────────────────────────────────────────────────────

def ssh_run(host, *args, timeout=15):
    cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
           f"{DEFAULT_USER}@{host}"]
    cmd.extend(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -2, "", "ssh non trovato"


def verify_ssh(host):
    rc, out, err = ssh_run(host, "echo", "pong")
    if rc != 0:
        fail(f"SSH: {host} non raggiungibile — {err}")
        return False
    ok(f"SSH: {host} — tunnel via cavo Cat 7")
    return True


# ─── Remote checks ────────────────────────────────────────────

def remote_status(host):
    status = {"host": host, "backend": False, "frontend": False, "ollama": False}

    rc, out, _ = ssh_run(host, "curl", "-s", "http://localhost:8000/api/health", timeout=8)
    if rc == 0 and out:
        try:
            d = json.loads(out)
            status["backend"] = True
            status["model"] = d.get("model", "?")
            status["rag_docs"] = d.get("rag_docs", 0)
            ok(f"Backend: {d['model']} — {d.get('rag_docs', 0)} documenti in KB")
        except Exception:
            warn("Backend: risposta non valida")
    else:
        warn("Backend: non attivo")

    rc, out, _ = ssh_run(host, "curl", "-s", "http://localhost:11434/api/tags", timeout=8)
    if rc == 0 and out:
        try:
            if json.loads(out).get("models"):
                status["ollama"] = True
                ok("Ollama: attivo")
        except Exception:
            warn("Ollama: risposta non valida")
    else:
        warn("Ollama: non attivo")

    rc, out, _ = ssh_run(host, "sh", "-c",
                         "ps aux | grep 'vite' | grep -v grep | head -1", timeout=5)
    if rc == 0 and out:
        status["frontend"] = True
        ok("Frontend: attivo")
    else:
        warn("Frontend: non attivo")

    return status


# ─── Start services ───────────────────────────────────────────

def start_services(host):
    info("Avvio backend...")
    ssh_run(host, "sh", "-c",
            f"cd {REMOTE_DIR}/backend && nohup uvicorn main:app "
            f"--host 0.0.0.0 --port {BACKEND_PORT} > /tmp/smot-backend.log 2>&1 &",
            timeout=8)
    time.sleep(3)

    info("Avvio frontend...")
    ssh_run(host, "sh", "-c",
            f"cd {REMOTE_DIR}/frontend && nohup npm run dev "
            f"> /tmp/smot-frontend.log 2>&1 &",
            timeout=8)
    time.sleep(3)

    ok("Servizi avviati")


# ─── Port forwarding ──────────────────────────────────────────

FORWARD_PROC = [None]

def start_tunnel(host):
    info("Port forwarding SSH...")
    cmd = [
        "ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-L", f"{BACKEND_PORT}:localhost:{BACKEND_PORT}",
        "-L", f"{FRONTEND_PORT}:localhost:{FRONTEND_PORT}",
        "-N", f"{DEFAULT_USER}@{host}",
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        FORWARD_PROC[0] = proc
        time.sleep(2)
        if proc.poll() is None:
            ok(f"Tunnel: localhost:{BACKEND_PORT}  ↔  {host}:{BACKEND_PORT}")
            ok(f"        localhost:{FRONTEND_PORT}  ↔  {host}:{FRONTEND_PORT}")
            return True
        fail(f"Tunnel SSH fallito (exit {proc.returncode})")
        return False
    except FileNotFoundError:
        fail("ssh non trovato — installalo con 'brew install openssh'")
        return False


def stop_tunnel():
    p = FORWARD_PROC[0]
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
    FORWARD_PROC[0] = None


# ─── Browser ──────────────────────────────────────────────────

def open_browser():
    url = f"http://localhost:{FRONTEND_PORT}"
    info(f"Apro browser: {url}")
    try:
        webbrowser.open(url)
        ok("Browser aperto")
    except Exception:
        warn("Apri manualmente il browser su " + url)


# ─── Modalità locale ──────────────────────────────────────────

def run_local():
    def _get(url):
        try:
            r = urllib.request.urlopen(url, timeout=3)
            return r.status == 200, r.read().decode()
        except Exception:
            return False, ""

    ollama_ok, _ = _get("http://localhost:11434/api/tags")
    ok("Ollama: attivo") if ollama_ok else warn("Ollama non raggiungibile")

    be_ok, data = _get(f"http://localhost:{BACKEND_PORT}/api/health")
    if not be_ok:
        info("Avvio backend...")
        subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
            cwd=os.path.join(os.path.dirname(__file__), "backend"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        be_ok, data = _get(f"http://localhost:{BACKEND_PORT}/api/health")
    ok("Backend: attivo") if be_ok else warn("Backend: errore")

    if os.path.isdir(os.path.join(os.path.dirname(__file__), "frontend")):
        rc, out, _ = subprocess.run(
            ["sh", "-c", "ps aux | grep 'vite' | grep -v grep"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip() if False else (None, "", "")
        info("Frontend pronto")
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=os.path.join(os.path.dirname(__file__), "frontend"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        ok("Frontend avviato")

    open_browser()
    print(f"\n  {C.DIM}Premi Ctrl+C per fermare{C.RESET}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()


# ─── Main ─────────────────────────────────────────────────────

def main():
    global DEFAULT_USER

    parser = argparse.ArgumentParser(
        description="SMOT-KNOWLEDGE — Remote Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Esempi:
  python3 smot.py --host 192.168.1.100    ← tunnel Cat 7 al server
  python3 smot.py --host 192.168.1.100 --status
  python3 smot.py --local                 ← tutto in locale""")
    parser.add_argument("--host", help="IP del server Linux (rete locale via Cat 7)")
    parser.add_argument("--local", action="store_true", help="Esecuzione locale")
    parser.add_argument("--status", action="store_true", help="Solo verifica stato")
    parser.add_argument("--user", default="", help=f"Utente SSH (default: {DEFAULT_USER})")
    args = parser.parse_args()

    if args.user:
        DEFAULT_USER = args.user

    # ── Verifica host IMMEDIATA ──
    host = args.host
    if not args.local and not host:
        fail("Specifica l'IP del server: python3 smot.py --host <IP>")
        sys.exit(1)

    if not args.local:
        print(f"\n  Verifica tunnel SSH verso {host}...", end=" ", flush=True)
        if not verify_ssh(host):
            sys.exit(1)

    # ── Banner ──
    print(f"\n{C.BOLD}{C.CYAN}  ⚡ SMOT-KNOWLEDGE{C.RESET}")
    print(f"  {C.DIM}{'─' * 40}{C.RESET}\n")

    # ── Modalità locale ──
    if args.local:
        run_local()
        return

    # ── Solo status ──
    if args.status:
        st = remote_status(host)
        print(f"\n  {C.BOLD}Riepilogo{C.RESET}")
        for k, v in st.items():
            if k == "host":
                continue
            mark = f"{C.GREEN}✓{C.RESET}" if v else f"{C.RED}✗{C.RESET}"
            val = v if isinstance(v, str) else ("attivo" if v else "spento")
            print(f"  {mark} {k}: {val}")
        return

    # ── Full start ──
    st = remote_status(host)

    if not (st.get("backend") and st.get("frontend")):
        start_services(host)
        time.sleep(2)
        st = remote_status(host)

    if not start_tunnel(host):
        fail("Tunnel SSH non riuscito — verifica che le porte siano libere")
        sys.exit(1)

    open_browser()

    model = st.get("model", "gemma3:4b")
    print(f"\n  {C.BOLD}⚡ SMOT-KNOWLEDGE attivo{C.RESET}")
    print(f"  {C.DIM}Modello:{C.RESET} {model}")
    print(f"  {C.DIM}Chat:   {C.CYAN}http://localhost:{FRONTEND_PORT}{C.RESET}")
    print(f"  {C.DIM}API:    {C.CYAN}http://localhost:{BACKEND_PORT}/api/health{C.RESET}")
    print(f"  {C.DIM}Premi Ctrl+C per fermare tutto{C.RESET}\n")

    try:
        while True:
            time.sleep(1)
            if FORWARD_PROC[0] and FORWARD_PROC[0].poll() is not None:
                fail("Tunnel perso — riconnessione...")
                break
    except KeyboardInterrupt:
        print()

    stop_tunnel()
    ok("Fermo.")


if __name__ == "__main__":
    main()
