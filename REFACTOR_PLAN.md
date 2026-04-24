# Refaktoryzacja — YTLottery (przed testami)

## 1. AuthorsManager — hardcoded multiprocessing (logic.py:10)

**Problem:** Klasa odpowiedzialna za logike biznesowa (dodaj/usun/losuj) jest scisle powiazana z infrastruktura multiprocessing. Nie da sie przetestowac w izolacji bez uruchamiania procesow.

```python
# PRZED
self.authors_dict = multiprocessing.Manager().dict()
```

**Fix:** Wstrzyknac dict przez konstruktor.

```python
# PO
class AuthorsManager:
    def __init__(self, authors_dict=None):
        self.authors_dict = authors_dict if authors_dict is not None else {}
```

---

## 2. apply_url() — 3 odpowiedzialnosci (logic.py:99-110)

**Problem:** Walidacja URL, tworzenie polaczenia z czatem i komunikacja przez queue — wszystko w jednej funkcji. Trudno przetestowac sama walidacje.

**Fix:** Rozbic na mniejsze funkcje:
- walidacja URL (zwraca video_id lub None)
- tworzenie polaczenia (zwraca chat lub None)
- komunikacja queue (pozostaje w apply_url)

---

## 3. start_chat_listener() — monolit (logic.py:112-134)

**Problem:** Jedna funkcja robi: setup polaczenia, nasluchiwanie w petli, filtrowanie keywordow, dodawanie autorow. Nie da sie przetestowac fragmentow osobno.

**Fix:** Wyciagnac logike petli do osobnej funkcji:
- `process_chat_messages(chat, keyword, authors_manager)` — przetwarza wiadomosci
- `start_chat_listener()` — odpowiada tylko za zarzadzanie cyklem zycia

---

## 4. AppManager — brak DI (logic.py:31-37)

**Problem:** Tworzy wszystko w __init__: AuthorsManager, queue, event, process. Brak mozliwosci wstrzykniecia mockow.

```python
# PRZED
class AppManager:
    def __init__(self):
        self.authors_manager = AuthorsManager()
        self.stop_event = multiprocessing.Event()
        ...
```

**Fix:** Akceptowac zaleznosci przez konstruktor z sensownymi defaultami.

```python
# PO
class AppManager:
    def __init__(self, authors_manager=None, stop_event=None,
                 from_main_to_listener_queue=None,
                 from_listener_to_main_queue=None):
        self.authors_manager = authors_manager or AuthorsManager()
        self.stop_event = stop_event or multiprocessing.Event()
        ...
```

---

## 5. app.py — globalny stan (app.py:31)

**Problem:** Globalna zmienna app_manager utrudnia testowanie. FastAPI ma wbudowany system dependency injection.

```python
# PRZED
app_manager: AppManager = None

@app.on_event("startup")
def startup_event():
    global app_manager
    app_manager = AppManager()
```

**Fix:** Uzyc Depends() z FastAPI.

```python
# PO
def get_app_manager():
    return app_manager

@app.post("/draw")
def draw_winner(manager: AppManager = Depends(get_app_manager)):
    ...
```

---

## Kolejnosc realizacji

1. **Punkt 1** — AuthorsManager DI (najwiekszy wplyw na testy jednostkowe)
2. **Punkt 4** — AppManager DI (umozliwia mockowanie w testach API)
3. **Punkt 2** — Rozbicie apply_url()
4. **Punkt 3** — Rozbicie start_chat_listener()
5. **Punkt 5** — Dependency injection w FastAPI
