# language: Python, file: install_deps.py, target: Windows 11 / Linux, Python 3.10+
import io
import os
from pathlib import Path
import subprocess
import sys
import zipfile

PACKAGES = [
    "psutil",
    "requests",
    "urllib3",
    "PySocks",
    "certifi",
    "pyTelegramBotAPI",
    "playwright",
    "speedtest-cli",
    "Flask",
]

REPO_URL = "https://github.com/hazardbr6/host"
REPO_DIR = Path("host")
# Set a specific filename (e.g., "main.py") or leave None to auto-detect
ENTRY_FILE = None


def install_directly():
  print("[*] Installing packages directly via pip...")
  cmd = [sys.executable, "-m", "pip", "install"] + PACKAGES
  result = subprocess.run(cmd, capture_output=True, text=True)

  print(result.stdout)
  if result.stderr:
    print(result.stderr, file=sys.stderr)

  if "playwright" in PACKAGES:
    print("[*] Installing Playwright browsers...")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install"], capture_output=True
    )

  print("[+] Direct dependency installation complete.")


def clone_or_download_repo(repo_url: str, dest_dir: Path):
  """Clones the target repo using git, falling back to a GitHub ZIP download if git is unavailable."""
  if dest_dir.exists() and any(dest_dir.iterdir()):
    print(
        f"[*] Directory '{dest_dir}' already exists. Pulling latest"
        " updates..."
    )
    subprocess.run(["git", "-C", str(dest_dir), "pull"], check=False)
    return

  print(f"[*] Fetching repository from {repo_url}...")
  try:
    subprocess.run(
        ["git", "clone", f"{repo_url.rstrip('/')}.git", str(dest_dir)],
        check=True,
    )
    print(f"[+] Cloned via git to {dest_dir}")
  except (subprocess.CalledProcessError, FileNotFoundError):
    print(
        "[!] Git clone failed or Git not installed. Falling back to ZIP"
        " download..."
    )
    import requests

    base_url = repo_url.rstrip("/").removesuffix(".git")
    for branch in ("main", "master"):
      archive_url = f"{base_url}/archive/refs/heads/{branch}.zip"
      resp = requests.get(archive_url, timeout=30)
      if resp.status_code == 200:
        break
    else:
      raise RuntimeError(
          f"Failed to download repository archive from {base_url}"
      )

    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
      root_folder = z.namelist()[0].split("/")[0]
      z.extractall(dest_dir.parent)
      extracted_path = dest_dir.parent / root_folder
      if extracted_path != dest_dir:
        if dest_dir.exists():
          import shutil

          shutil.rmtree(dest_dir)
        extracted_path.rename(dest_dir)
    print(f"[+] Extracted archive to {dest_dir}")


def install_repo_requirements(repo_dir: Path):
  """Installs repo-specific requirements.txt if present."""
  req_file = repo_dir / "requirements.txt"
  if req_file.is_file():
    print(f"[*] Installing repo requirements from {req_file}...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        check=False,
    )


def run_repo(repo_dir: Path, entry_filename: str | None = None):
  """Locates the entry script and executes it using the active Python environment."""
  target_script = None

  if entry_filename:
    candidate = repo_dir / entry_filename
    if candidate.is_file():
      target_script = candidate
  else:
    # Priority order for standard entry filenames
    preferred = ["main.py", "app.py", "host.py", "run.py", "bot.py", "server.py"]
    for name in preferred:
      candidate = repo_dir / name
      if candidate.is_file():
        target_script = candidate
        break

    # Fallback to the first top-level .py file found
    if not target_script:
      py_files = sorted(repo_dir.glob("*.py"))
      if py_files:
        target_script = py_files[0]

  if not target_script or not target_script.is_file():
    raise FileNotFoundError(
        f"No Python entry file found in '{repo_dir}'. Set ENTRY_FILE explicitly."
    )

  print(f"[+] Launching {target_script.name} in working directory {repo_dir}...")
  # Unbuffered stream directly to terminal so long-running servers/bots show live output
  subprocess.run(
      [sys.executable, str(target_script.resolve())], cwd=str(repo_dir)
  )


if __name__ == "__main__":
  install_directly()
  clone_or_download_repo(REPO_URL, REPO_DIR)
  install_repo_requirements(REPO_DIR)
  run_repo(REPO_DIR, ENTRY_FILE)
