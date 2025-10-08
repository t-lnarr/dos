# filename: browser_like_rate.py
# Python 3.8+ (tercihen 3.10+)
# İhtiyaç: pip install aiohttp

import asyncio
import time
import aiohttp
from datetime import datetime

URL = "https://www.tdu.edu.tm/"   # <<< burayı sadece kendi test/localhost veya iznin olan site ile değiştir
REQUESTS_PER_SECOND = 50
TIMEOUT = 10  # saniye

# Tarayıcı benzeri headers
BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",  # aiohttp otomatik handle eder
    "Referer": "https://www.google.com/",
    # Diğer header'lar istenirse eklenebilir (Cookie, DNT, etc.)
}

def now():
    return datetime.now().strftime("%H:%M:%S")

async def fetch(session: aiohttp.ClientSession, idx: int):
    try:
        t0 = time.perf_counter()
        async with session.get(URL, timeout=TIMEOUT) as resp:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            status = resp.status
            # Küçük içerik okumak istersen: text = await resp.text()
            print(f"{now()}  #{idx:02d}  {status}  {elapsed_ms:.0f} ms")
            return status
    except asyncio.TimeoutError:
        print(f"{now()}  #{idx:02d}  TIMEOUT")
    except aiohttp.ClientResponseError as e:
        print(f"{now()}  #{idx:02d}  HTTP_ERR {e.status}")
    except aiohttp.ClientConnectorError as e:
        print(f"{now()}  #{idx:02d}  CONN_ERR: {e}")
    except Exception as e:
        print(f"{now()}  #{idx:02d}  ERROR: {e}")

async def main():
    # TCP connection pooling ve header'ları burada veriyoruz
    conn = aiohttp.TCPConnector(limit=REQUESTS_PER_SECOND*2)  # eşzamanlı bağlantı limiti
    timeout = aiohttp.ClientTimeout(total=None)  # per-request timeout handled in fetch
    async with aiohttp.ClientSession(headers=BROWSER_HEADERS, connector=conn, timeout=timeout) as session:
        round_count = 0
        print("Başlıyor — durdurmak için Ctrl+C")
        try:
            while True:
                round_count += 1
                start = time.time()
                tasks = [asyncio.create_task(fetch(session, i+1)) for i in range(REQUESTS_PER_SECOND)]
                # hepsini bekle (istekler paralel)
                await asyncio.gather(*tasks)
                elapsed = time.time() - start
                # 1 saniyeyi doldur: (ör. istekler 0.2s sürdüyse 0.8s bekle)
                to_sleep = max(0.0, 1.0 - elapsed)
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)
        except KeyboardInterrupt:
            print("\nKapatılıyor — görüşürüz! ✌️")

if __name__ == "__main__":
    asyncio.run(main())
