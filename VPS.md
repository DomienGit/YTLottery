# Konfiguracja FastAPI na VPS (Użytkownik Systemowy)

Dokumentacja procesu wdrażania aplikacji FastAPI na dedykowanym użytkowniku systemowym o minimalnych uprawnieniach.

## 1. Utworzenie bezpiecznego użytkownika
Stworzyliśmy użytkownika systemowego `ytapp`, który jest odizolowany od reszty systemu:
```bash
sudo useradd -r -s /usr/sbin/nologin ytapp
```
*   `-r`: Konto systemowe (brak wygasania hasła, niski UID).
*   `-s /usr/sbin/nologin`: Brak dostępu do powłoki (shell) - nikt nie może się zalogować na to konto przez SSH.

## 2. Lokalizacja projektu i uprawnienia
Projekt został umieszczony w `/opt/ytlottery`, co jest standardem dla aplikacji serwerowych (poza folderami domowymi użytkowników `/home`).

```bash
sudo chown -R ytapp:ytapp /opt/ytlottery
sudo chmod -R 755 /opt/ytlottery
```

## 3. Automatyzacja przez Systemd
Stworzyliśmy plik usługi `/etc/systemd/system/ytlottery.service`, aby system zarządzał procesem aplikacji.

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

## 4. Reverse Proxy (NGINX)
NGINX działa jako "front" serwera, odbierając ruch na porcie 80/443 i przekazując go do FastAPI (port 8000).

**Konfiguracja `/etc/nginx/sites-available/ytlottery`:**
```nginx
server {
    server_name ytlottery.pl www.ytlottery.pl;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Obsługa plików statycznych bezpośrednio przez NGINX
    location /img/ { alias /opt/ytlottery/img/; }
}
```

## 5. Certyfikat SSL (HTTPS)
Użyliśmy Certbota (Let's Encrypt) do zabezpieczenia połączenia.

```bash
sudo apt install python3-certbot-nginx
sudo certbot --nginx -d ytlottery.pl -d www.ytlottery.pl
```

## 6. Napotkane problemy i ich przyczyny

### Problem A: `status=203/EXEC` (Błąd uruchamiania)
**Przyczyna:** Środowisko wirtualne (`.venv`) linkowało do interpretera Pythona w folderze `/root/`, do którego użytkownik `ytapp` nie miał uprawnień.
**Rozwiązanie:** Stworzenie nowego `.venv` za pomocą systemowego Pythona (`python3 -m venv .venv`).

### Problem B: Certbot "Could not install certificate"
**Przyczyna:** W pliku NGINX brakowało dyrektywy `server_name ytlottery.pl;` lub była ona błędna, przez co Certbot nie wiedział, do którego "bloku" dopisać konfigurację SSL.
**Rozwiązanie:** Ręczne uzupełnienie `server_name` w konfiguracji NGINX i ponowne uruchomienie `certbot install`.

## 7. Komendy zarządzające
*   `sudo systemctl restart ytlottery` – restart aplikacji FastAPI.
*   `sudo systemctl reload nginx` – przeładowanie NGINX (po zmianach w domenie).
*   `sudo journalctl -u ytlottery -f` – podgląd logów aplikacji.
*   `sudo certbot renew --dry-run` – test automatycznego odnawiania SSL.
