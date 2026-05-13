#!/usr/bin/env python3
"""
SMOT-KNOWLEDGE — Remote Launcher per Mac Mini M4

Connettiti al server Linux con GPU, avvia backend/frontend,
fai port forwarding e apri il browser. Tutto in un comando.

Uso:
  python3 smot.py                        # connessione SSH automatica
  python3 smot.py --host 192.168.1.100   # IP specifico
  python3 smot.py --local                # tutto in locale (senza SSH)
  python3 smot.py --status               # verifica stato remoto
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
from pathlib import Path


# ─── Configurabile ─────────────────────────────────────────────

DEFAULT_HOST = ""            # lascia vuoto per auto-detect
DEFAULT_USER = "michele-finocchiaro"
DEFAULT_PORT = 8000
DEFAULT_FRONTEND_PORT = 5173
REMOTE_DIR = "/home/michele-finocchiaro/SMOT-KNOWLEDGE"
SSH_KEY = ""                 # lascia vuoto per default (~/.ssh/id_*)


# ─── Colori ────────────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"


# ─── Utility ───────────────────────────────────────────────────

def banner():
    print(f"\n{C.BOLD}{C.CYAN}  ⚡ SMOT-KNOWLEDGE — Remote Launcher{C.RESET}")
    print(f"  {C.DIM}{'─' * 44}{C.RESET}\n")


def info(msg):
    print(f"  {C.CYAN}▶{C.RESET} {msg}")


def ok(msg):
    print(f"  {C.GREEN}✓{C.RESET} {msg}")


def warn(msg):
    print(f"  {C.YELLOW}⚠{C.RESET} {msg}")


def fail(msg):
    print(f"  {C.RED}✗{C.RESET} {msg}")


def run(cmd, capture=True, timeout=30, check=True):
    """Esegue un comando locale e ritorna (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd, capture_output=capture, text=True, timeout=timeout
        )
        return r.returncode, r.stdout.strip() if r.stdout else "", r.stderr.strip() if r.stderr else ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -2, "", "comando non trovato"


def ssh_cmd(host, *args):
    """Costruisce una lista di comandi SSH."""
    cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no"]
    if SSH_KEY:
        cmd += ["-i", SSH_KEY]
    cmd += [f"{DEFAULT_USER}@{host}"]
    cmd += list(args)
    return cmd


def ssh(host, *args, timeout=30):
    """Esegue un comando SSH e ritorna (rc, stdout, stderr)."""
    cmd = ssh_cmd(host, *args)
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "SSH timeout"
    except FileNotFoundError:
        return -2, "", "ssh non trovato"


# ─── Host detection ────────────────────────────────────────────

def find_host():
    """Cerca automaticamente il server Linux sulla rete locale."""
    # Prova hostname noti
    for name in ["linux-desktop", "smot-server", "ubuntu", "localhost"]:
        try:
            ip = socket.gethostbyname(name)
            rc, _, _ = ssh(name, "echo", "pong", timeout=5)
            if rc == 0:
                return name
        except Exception:
            continue
    # Scansiona la subnet /24 per host con porta 22 aperta e risposta
    try:
        # Prende l'IP locale del Mac
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        subnet = ".".join(local_ip.split(".")[:3])
        info(f"Scansione {subnet}.0/24 per il server...")
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            rc, out, _ = ssh(ip, "echo", "pong", timeout=2)
            if rc == 0 and "pong" in out:
                return ip
    except Exception:
        pass
    return ""


# ─── Status check ──────────────────────────────────────────────

def check_remote(host):
    """Verifica lo stato del server remoto."""
    info(f"Connessione a {host}...")

    # Test SSH
    rc, out, err = ssh(host, "echo", "pong")
    if rc != 0:
        fail(f"SSH non raggiungibile: {err}")
        return False, {}
    ok(f"SSH: {host}")

    # Backend health
    status = {"host": host, "backend": False, "frontend": False, "ollama": False}
    rc, out, _ = ssh(host, "curl", "-s", "http://localhost:8000/api/health")
    if rc == 0 and out:
        try:
            data = json.loads(out)
            status["backend"] = True
            status["model"] = data.get("model", "?")
            status["rag_docs"] = data.get("rag_docs", 0)
            ok(f"Backend: {data.get('model', '?')} — {data.get('rag_docs', 0)} doc")
        except json.JSONDecodeError:
            warn("Backend: risposta non valida")
    else:
        warn("Backend: non attivo")

    # Ollama
    rc, out, _ = ssh(host, "curl", "-s", "http://localhost:11434/api/tags")
    if rc == 0 and out:
        try:
            models = json.loads(out).get("models", [])
            status["ollama"] = True
            status["models"] = [m["name"] for m in models]
            ok(f"Ollama: {len(models)} modelli — {', '.join(m['name'] for m in models[:3])}")
        except json.JSONDecodeError:
            warn("Ollama: risposta non valida")
    else:
        warn("Ollama: non attivo")

    # Frontend (check via ps)
    rc, out, _ = ssh(host, "sh", "-c",
                     "ps aux | grep 'vite' | grep -v grep | head -1")
    if rc == 0 and out:
        status["frontend"] = True
        ok("Frontend: attivo")
    else:
        warn("Frontend: non attivo")

    return True, status


# ─── Start services ────────────────────────────────────────────

def start_services(host):
    """Avvia backend e frontend sul server remoto."""
    info("Avvio servizi...")

    # Backend
    rc, out, err = ssh(host, "sh", "-c",
                       f"cd {REMOTE_DIR}/backend && nohup uvicorn main:app "
                       f"--host 0.0.0.0 --port 8000 > /tmp/smot-backend.log 2>&1 &",
                       timeout=10)
    if rc == 0:
        ok("Backend avviato")
    else:
        warn(f"Backend: {err}")

    time.sleep(2)

    # Frontend
    rc, out, err = ssh(host, "sh", "-c",
                       f"cd {REMOTE_DIR}/frontend && nohup npm run dev "
                       f"> /tmp/smot-frontend.log 2>&1 &",
                       timeout=10)
    if rc == 0:
        ok("Frontend avviato")
    else:
        warn(f"Frontend: {err}")

    time.sleep(3)
    return True


# ─── Port forwarding ───────────────────────────────────────────

SSH_FORWARD_PROC = [None]


def start_port_forwarding(host):
    """Avvia SSH port forwarding in background."""
    info("Port forwarding SSH...")

    cmd = [
        "ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-L", f"{DEFAULT_FRONTEND_PORT}:localhost:{DEFAULT_FRONTEND_PORT}",
        "-L", f"{DEFAULT_PORT}:localhost:{DEFAULT_PORT}",
        "-N",
    ]
    if SSH_KEY:
        cmd += ["-i", SSH_KEY]
    cmd.append(f"{DEFAULT_USER}@{host}")

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        SSH_FORWARD_PROC[0] = proc
        time.sleep(2)
        if proc.poll() is None:
            ok(f"Forwarding: localhost:{DEFAULT_PORT} → {host}:{DEFAULT_PORT}")
            ok(f"            localhost:{DEFAULT_FRONTEND_PORT} → {host}:{DEFAULT_FRONTEND_PORT}")
            return True
        else:
            fail(f"Forwarding fallito (exit code {proc.returncode})")
            return False
    except FileNotFoundError:
        fail("ssh non trovato — installalo con 'brew install openssh'")
        return False


def stop_port_forwarding():
    """Ferma il port forwarding."""
    proc = SSH_FORWARD_PROC[0]
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        SSH_FORWARD_PROC[0] = None


# ─── Browser ───────────────────────────────────────────────────

def open_browser():
    """Apre il browser sul frontend."""
    url = f"http://localhost:{DEFAULT_FRONTEND_PORT}"
    info(f"Apertura browser: {url}")
    try:
        webbrowser.open(url)
        ok("Browser aperto")
    except Exception as e:
        warn(f"Browser: {e}")
        print(f"  Apri manualmente: {C.CYAN}{url}{C.RESET}")


# ─── Local mode ────────────────────────────────────────────────

def check_local():
    """Verifica e avvia tutto in locale (senza SSH)."""
    info("Modalità locale")

    def get(url):
        try:
            r = urllib.request.urlopen(url, timeout=3)
            return r.status == 200, r.read().decode()
        except Exception:
            return False, ""

    ollama_ok, _ = get("http://localhost:11434/api/tags")
    if ollama_ok:
        ok("Ollama: attivo")
    else:
        warn("Ollama non raggiungibile — avvialo con 'ollama serve'")

    backend_ok, data = get("http://localhost:8000/api/health")
    if backend_ok:
        ok("Backend: attivo")
    else:
        info("Avvio backend...")
        subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=os.path.join(os.path.dirname(__file__), "backend"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        backend_ok, _ = get("http://localhost:8000/api/health")
        ok("Backend avviato" if backend_ok else "Backend: errore avvio")

    frontend_ok = False
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    if os.path.isdir(frontend_dir):
        frontend_ok = True
        rc, out, _ = run(["sh", "-c", "ps aux | grep 'vite' | grep -v grep"],
                         timeout=5, check=False)
        if "vite" not in out:
            info("Avvio frontend...")
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            ok("Frontend avviato")
        else:
            ok("Frontend: già attivo")

    return backend_ok or frontend_ok


# ─── Main ──────────────────────────────────────────────────────

def main():
    global DEFAULT_USER
    parser = argparse.ArgumentParser(
        description="SMOT-KNOWLEDGE — Remote Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python3 smot.py                   ← auto-detect host + avvia tutto
  python3 smot.py --host 192.168.1.100
  python3 smot.py --local            ← tutto sulla macchina corrente
  python3 smot.py --status           ← solo verifica stato remoto
        """
    )
    parser.add_argument("--host", help="IP del server Linux")
    parser.add_argument("--local", action="store_true", help="Modalità locale (senza SSH)")
    parser.add_argument("--status", action="store_true", help="Solo verifica stato")
    parser.add_argument("--user", default="", help=f"Utente SSH (default: {DEFAULT_USER})")
    args = parser.parse_args()

    if args.user:
        DEFAULT_USER = args.user

    banner()

    # ── Modalità locale ──
    if args.local:
        check_local()
        open_browser()
        print(f"\n  {C.DIM}Premi Ctrl+C per fermare{C.RESET}")
        try:
            signal.pause()
        except KeyboardInterrupt:
            print()
        return

    # ── Trova host ──
    host = args.host or DEFAULT_HOST or find_host()
    if not host:
        fail("Nessun host trovato. Specifica: python3 smot.py --host <IP>")
        sys.exit(1)

    if host != DEFAULT_HOST:
        ok(f"Host: {host}")

    # ── Solo status ──
    if args.status:
        connected, status = check_remote(host)
        if not connected:
            sys.exit(1)
        print(f"\n  {C.BOLD}Riepilogo{C.RESET}")
        for k, v in status.items():
            if k != "host":
                print(f"  {'  ' if v else f'{C.RED}✗{C.RESET}'} {k}: {v}")
        return

    # ── Full start ──
    connected, status = check_remote(host)

    if not connected:
        sys.exit(1)

    if not (status.get("backend") and status.get("frontend")):
        start_services(host)
        time.sleep(2)
        _, status = check_remote(host)

    if not start_port_forwarding(host):
        warn("Port forwarding fallito — assicurati che le porte 8000 e 5173 siano libere")
        sys.exit(1)

    open_browser()

    print(f"\n  {C.BOLD}⚡ SMOT-KNOWLEDGE attivo!{C.RESET}")
    print(f"  {C.DIM}Chat:   {C.CYAN}http://localhost:{DEFAULT_FRONTEND_PORT}{C.RESET}")
    print(f"  {C.DIM}API:    {C.CYAN}http://localhost:{DEFAULT_PORT}/api/health{C.RESET}")
    print(f"  {C.DIM}Premi Ctrl+C per terminare tutto{C.RESET}\n")

    # Tieni in esecuzione
    try:
        while True:
            time.sleep(1)
            if SSH_FORWARD_PROC[0] and SSH_FORWARD_PROC[0].poll() is not None:
                fail("Port forwarding perso — riconnessione...")
                break
    except KeyboardInterrupt:
        print()
        info("Arresto...")

    stop_port_forwarding()
    ok("Fermo. ⚡ SMOT-KNOWLEDGE")


if __name__ == "__main__":
    main()
