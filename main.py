import os
import asyncio
import re
from typing import Dict, Optional, Tuple, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import aiohttp

# =========================
# CONFIG (BURAYI DÜZENLE)
# =========================

OBS_URL = "https://obis1.selcuk.edu.tr"
OBS_USERNAME = os.environ.get("OBS_USERNAME")
OBS_PASSWORD = os.environ.get("OBS_PASSWORD")

BROWSER_CONFIG = {
    "headless": True,
    "slow_mo": 0,
    "viewport": {"width": 1280, "height": 800},
    "timeout": 30000
}

RETRY_CONFIG = {
    "max_attempts": 3,
    "delay_between_attempts": 2
}

TELEGRAM_BOT_TOKEN = os.environ.get("OBS_PASSWORD")
TELEGRAM_CHAT_ID = os.environ.get("OBS_PASSWORD")

# =========================
# LOGGING (SIMPLE)
# =========================

def log_info(msg): print(f"[INFO] {msg}")
def log_success(msg): print(f"[OK] {msg}")
def log_warning(msg): print(f"[WARN] {msg}")
def log_error(msg): print(f"[ERROR] {msg}")
def log_debug(msg): print(f"[DEBUG] {msg}")

# =========================
# BOT SINIFI
# =========================

class OBSBot:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.base_url = OBS_URL.rstrip("/")

    # -------- Browser --------

    async def start(self):
        log_info("Tarayıcı başlatılıyor")
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=BROWSER_CONFIG["headless"],
            slow_mo=BROWSER_CONFIG["slow_mo"]
        )
        self.context = await self.browser.new_context(
            viewport=BROWSER_CONFIG["viewport"],
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(BROWSER_CONFIG["timeout"])
        log_success("Tarayıcı hazır")

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        log_info("Tarayıcı kapatıldı")

    # -------- Login --------

    async def login(self) -> bool:
        for attempt in range(RETRY_CONFIG["max_attempts"]):
            try:
                log_info("OBS giriş deneniyor")
                await self.page.goto(self.base_url, wait_until="networkidle")
                await self.page.fill('input[name="id"]', OBS_USERNAME)
                await self.page.fill('input[name="pass"]', OBS_PASSWORD)

                await self._solve_captcha()
                await self.page.click("button.btn-login")
                await self.page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)

                if "ogrenci" in self.page.url.lower():
                    log_success("Giriş başarılı")
                    return True

            except Exception as e:
                log_warning(f"Giriş hatası: {e}")
                await asyncio.sleep(RETRY_CONFIG["delay_between_attempts"])

        return False

    async def _solve_captcha(self):
        img = await self.page.query_selector("img#Image1")
        if not img:
            return

        title = await img.get_attribute("title")
        if title and title.isdigit():
            await self.page.fill("#TxtCaptcha", title)

    # -------- Ders Kayıt --------

    async def go_to_course_registration(self) -> bool:
        url = f"{self.base_url}/DersKaydi"
        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        return "DersKaydi" in self.page.url

    async def check_dolu_courses(self) -> List[str]:
        """
        SADECE:
        - Satırda 'Dolu' varsa
        - Ama + ikonu gelmişse
        """
        opened = []

        rows = await self.page.query_selector_all("table tr")

        for row in rows:
            try:
                text = (await row.inner_text()).lower()
                if "dolu" not in text:
                    continue

                cells = await row.query_selector_all("td")
                if len(cells) < 2:
                    continue

                course_name = (await cells[1].inner_text()).strip()

                plus_icon = await row.query_selector("a i.fa-plus, a img")
                if plus_icon:
                    log_success(f"KONTENJAN AÇILDI: {course_name}")
                    opened.append(course_name)

            except Exception:
                continue

        return opened

    # -------- Telegram --------

    async def send_telegram_notification(self, courses: List[str]):
        if not courses:
            return

        message = "📢 KONTENJAN AÇILDI!\n\n"
        for c in courses:
            message += f"✅ {c}\n"

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)

    # -------- Main Run --------

    async def run(self):
        await self.start()

        if not await self.login():
            log_error("Giriş başarısız")
            await self.stop()
            return

        if not await self.go_to_course_registration():
            log_error("Ders kayıt sayfası açılamadı")
            await self.stop()
            return

        opened = await self.check_dolu_courses()
        if opened:
            await self.send_telegram_notification(opened)

        await self.stop()

# =========================
# ENTRY
# =========================

if __name__ == "__main__":
    asyncio.run(OBSBot().run())
