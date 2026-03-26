# YTLottery 🎰

A web application designed for running giveaways and lotteries during YouTube live streams. It automatically collects participants from the chat (optionally filtered by a keyword) and features a dynamic "slot machine" winner selection.

🚀 **Live at:** [ytlottery.pl](https://ytlottery.pl)

## ✨ Features

- **YouTube Integration**: Connects to any YouTube video, live stream, or short via URL.
- **Keyword Filtering**: Optionally restrict participants to those who type a specific word or phrase.
- **Real-time Updates**: Automatically fetches and displays new participants as they comment.
- **Participant Management**: Manually add or remove entries from the drawing pool.
- **Animated Drawing**: Interactive "slot machine" animation for picking winners.
- **Winner Control**: Choose to keep the winner in the pool or remove them for subsequent rounds.
- **Modern UI**: Clean, responsive interface powered by GSAP animations.

## 🛠️ Technology Stack

- **Backend**: Python ([FastAPI](https://fastapi.tiangolo.com/))
- **Chat Listener**: [pytchat](https://github.com/taizan-ocean/pytchat) (YouTube chat scraping)
- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Animations**: [GSAP](https://greensock.com/gsap/) (GreenSock Animation Platform)

## 📖 Quick Start Guide

1. **Connect**: Paste your YouTube link and click **Confirm**.
2. **Filter (Optional)**: Click "Filter by keyword" to set a required entry phrase.
3. **Collect**: Click **Start** to begin listening to the live chat.
4. **Draw**: Once you have enough entries, click **Stop**, then **Draw Winner** to start the animation.

---

## 🖥️ For Developers (Self-hosting)

If you wish to run your own instance of the application:

### Prerequisites
- Python 3.14+

### Local Installation
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
3. Access the application at `http://127.0.0.1:8000`.

## ⚠️ Known Limitations
The project uses `pytchat`, which relies on public chat data. YouTube may occasionally apply rate limits to the server's IP address. If connection issues occur, try restarting the application or refreshing the stream link.
