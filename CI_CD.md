# CI/CD — YTLottery

## CI (Continuous Integration) — Automatyczne testy

### Krok 1 — Stworzenie pliku workflow
- Stwórz plik: `.github/workflows/tests.yml`
- GitHub szuka workflow'ów dokładnie w `.github/workflows/`
- W pliku YAML definiujesz:
  1. `name:` — nazwa workflow (np. "YTLottery")
  2. `on:` — kiedy odpalić (push na main, pull_request do main)
  3. `jobs:` — definicja zadania
     - `runs-on: ubuntu-latest`
     - `steps:`
       - checkout kodu (`actions/checkout`)
       - instalacja Pythona (`actions/setup-python`)
       - instalacja zależności (`pip install -r requirements.txt`)
       - odpalenie `pytest`

### Krok 2 — Dodanie pytest do zależności
- Dodaj `pytest` do `requirements.txt` lub jako dev dependency w `pyproject.toml`

### Krok 3 — Push na GitHub
- `git add .github/workflows/tests.yml`
- `git commit` + `git push` na main
- Wynik testów w zakładce **Actions** na GitHubie

### Dodatkowo
- W `pyproject.toml` dodaj sekcję `[tool.pytest.ini_options]` z `pythonpath = ["."]` — żeby pytest widział moduł `app`

---

## CD (Continuous Deployment) — Automatyczny deploy na VPS

### Krok 1 — Skonfiguruj systemd service na VPS

Stwórz plik `/etc/systemd/system/ytlottery.service`:

```ini
[Unit]
Description=FastAPI YTLottery Service
After=network.target

[Service]
User=ytapp
Group=ytapp
WorkingDirectory=/opt/ytlottery
ExecStart=/opt/ytlottery/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Komendy:
- `sudo systemctl daemon-reload`
- `sudo systemctl enable ytlottery` — startuje przy boot
- `sudo systemctl start ytlottery` — odpala teraz
- `sudo systemctl restart ytlottery` — restart
- `sudo systemctl status ytlottery` — status
- `journalctl -u ytlottery -f` — logi na żywo

### Krok 2 — Wygeneruj klucz SSH dla GitHub Actions

Na swoim komputerze (nie na VPS):
```bash
ssh-keygen -t ed25519 -C "github-actions" -f github-actions-key
```
Powstaną dwa pliki:
- `github-actions-key` — klucz prywatny (idzie do GitHub Secrets)
- `github-actions-key.pub` — klucz publiczny (idzie na VPS)

Na VPS dodaj klucz publiczny:
```bash
echo "ZAWARTOŚĆ_KLUCZA_PUBLICZNEGO" >> ~/.ssh/authorized_keys
```

Na GitHubie (Settings → Secrets and variables → Actions) dodaj secrety:
- `VPS_SSH_KEY` — zawartość klucza prywatnego
- `VPS_USER` — username na VPS (np. `root`)
- `VPS_HOST` — IP VPS

### Krok 3 — Dodaj deploy job do workflow

W `.github/workflows/tests.yml` dodaj job `deploy`:

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to VPS
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USER }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: |
          cd /opt/ytlottery
          git pull origin main
          sudo systemctl restart ytlottery
```

---

## Ważne uwagi

- Klucz prywatny nigdy nie ląduje w kodzie — tylko w GitHub Secrets
- GitHub Secrets są szyfrowane i nie da się ich odczytać po zapisaniu
- Deploy odpala się tylko po pushu na main, nie przy PR
- Jak testy nie przejdą — deploy się nie odpali (`needs: test`)
- Upewnij się że `sudo systemctl restart` nie wymaga hasła
  (dodaj regułę w sudoers: `ALL=(ALL) NOPASSWD: /bin/systemctl restart ytlottery`)

## Przydatne linki
- https://docs.github.com/en/actions
- https://docs.github.com/en/actions/writing-workflows/quickstart