# Plan testów — YTLottery

## Stack testowy

- **pytest** — framework testowy
- **httpx** — wymagany przez FastAPI TestClient
- **pytest-asyncio** — wsparcie dla endpointów async (na przyszłość)
- Mockowanie `pytchat` — izolacja od zewnętrznego API YouTube

## 1. Testy jednostkowe — `logic.py` (priorytet: wysoki)

Najprostsze do napisania, najwieksza wartosc. Nie wymagaja stawiania serwera.

### `get_video_id()`

- Poprawne URL-e: `watch?v=ID`, `youtu.be/ID`, `embed/ID`, `shorts/ID`
- Niepoprawne URL-e: pusty string, losowy tekst, URL bez ID
- Edge case'y: URL z dodatkowymi parametrami, biale znaki

### `AuthorsManager`

- `add_author()` — dodawanie uczestnika, duplikaty, typy danych
- `delete_author()` — usuwanie istniejacego i nieistniejacego uczestnika
- `draw_winner()` — losowanie z pustej listy, z 1 osoba, z wieloma osobami, powtarzalnosc losowania
- `get_authors()` — zwracanie listy uczestnikow
- `clear_authors()` — czyszczenie listy

### `check_keyword_in_message()`

- Dopasowanie, brak dopasowania, wielkosc liter, pusty keyword, pusta wiadomosc

## 2. Testy API — `app.py` (priorytet: sredni)

Uzywaja FastAPI TestClient, testuja endpointy bez uruchamiania serwera.

### Endpointy do przetestowania

| Endpoint | Scenariusze |
|---|---|
| `POST /apply-url` | Prawidlowy URL, nieprawidlowy URL, brak URL |
| `POST /start` | Start bez URL, start z keyword, start bez keyword |
| `POST /stop` | Stop bez aktywnego nasluchiwania |
| `POST /draw` | Losowanie bez uczestnikow, z uczestnikami |
| `POST /delete` | Usuwanie istniejacego / nieistniejacego uczestnika |
| `POST /add-author` | Dodawanie z brakujacymi danymi |
| `POST /clear` | Czyszczenie listy |

### Wymagane mocki

- `pytchat.create()` — unikanie realnych polaczen z YouTube
- Multiprocessing — mockowanie kolejek i procesow

## 3. Testy integracyjne (priorytet: niski, na pozniej)

- Pelny flow: `apply-url` -> `start` -> dodanie uczestnikow -> `draw` -> `clear`
- Komunikacja miedzy procesami (multiprocessing queues)
- Wielokrotne losowania (keep/remove winner)

## Struktura plikow

```
tests/
  __init__.py
  conftest.py           # wspolne fixtures (TestClient, mocki)
  test_logic.py         # testy jednostkowe logic.py
  test_api.py           # testy endpointow app.py
  test_integration.py   # testy integracyjne (pozniej)
```

## Kolejnosc realizacji

1. Zainstalowac zaleznosci testowe (`pytest`, `httpx`)
2. Stworzyc strukture katalogu `tests/`
3. Napisac testy jednostkowe dla `logic.py`
4. Napisac testy API dla `app.py`
5. (Opcjonalnie) Dopisac testy integracyjne
