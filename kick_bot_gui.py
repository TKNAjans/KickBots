import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
import asyncio
import random
import queue
import threading
import time
import os
import psutil
import shutil
import requests
import re
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Durum göstergesi için renkler
COLOR_IDLE = "#808080"  # Gri
COLOR_SUCCESS = "#00ff00"  # Yeşil
COLOR_FAILED = "#ff0000"  # Kırmızı

# Global değişkenler
bot_tasks = []
cancel_event = None
proxy_list = []
used_proxies = []
proxy_stats = {"total": 0, "working": 0, "failed": 0}
proxy_file = None
chrome_path = os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe")
drivers = []
current_language = "Türkçe"

# Dil sözlüğü
languages = {
    "Türkçe": {
        "title": "KICK BOT KONTROL PANELI",
        "target_url": "Hedef URL:",
        "bot_count": "Bot Sayısı:",
        "use_proxy": "Proxy Kullan",
        "select_proxy_file": "Proxy Dosyası Seç",
        "select_chromedriver": "ChromeDriver Yolu Seç",
        "start_bots": "BOTLARI BAŞLAT",
        "stop_bots": "BOTLARI DURDUR",
        "clear_logs": "Logları Temizle",
        "sent_bots": "Gönderilen Bot:",
        "viewer_count": "İzleyici Sayısı:",
        "proxy_stats": "Proxy İstatistikleri:",
        "bot_status": "Bot Durumları:",
        "system_usage": "Sistem Kullanımı:",
        "cpu_usage": "CPU Kullanımı: 0%",
        "ram_usage": "RAM Kullanımı: 0%",
        "log_title": "İşlem Günlüğü:",
        "copyright": "Copyright © 2025 KICK BOT - Versiyon 1.0",
        "theme_select": "Tema Seç",
        "chromedriver_not_found": "ChromeDriver bulunamadı: {}. Lütfen ChromeDriver yolunu seçin.",
        "chromedriver_found": "ChromeDriver bulundu: {}",
        "invalid_bot_count": "Bot sayısı geçerli bir pozitif sayı olmalı.",
        "invalid_url": "Geçerli bir URL girin (örn: https://kick.com/yayin).",
        "no_proxy_file": "Proxy dosyası seçilmedi, proxysiz devam ediliyor.",
        "channel_not_live": "Kanal ({}) şu anda yayında değil.",
        "starting_bots": "{} bot başlatılıyor ({}) | Başlangıç izleyici: {}",
        "no_proxies": "Proxy listesi boş, proxysiz devam ediliyor.",
        "insufficient_proxies": "Yetersiz proxy: {} mevcut, {} bot isteniyor.",
        "headless_active": "Bot {}: Başsız mod aktif, tarayıcı görünmez çalışıyor.",
        "bot_success": "Bot {} yayına bağlandı ve video oynatılıyor (Selenium): {}",
        "video_not_found": "Bot {}: Video elementi bulunamadı, sayfa yüklendi ama oynatma başlatılamadı: {}",
        "quality_button_clicked": "Bot {}: Kalite butonuna tıklandı.",
        "quality_set": "Bot {}: Kalite 160p olarak ayarlandı.",
        "quality_failed": "Bot {}: Kalite ayarlama başarısız, kalite butonu veya 160p seçeneği bulunamadı.",
        "proxy_failed": "Bot {}: Kullanılabilir proxy kalmadı!",
        "bot_error": "Bot {}: {} - {}",
        "proxy_removed": " | Proxy kaldırıldı: {}",
        "viewer_updated": "İzleyici sayısı güncellendi: {}",
        "logs_cleared": "Loglar temizlendi.",
        "stopping_bots": "Botlar durduruluyor...",
        "bots_stopped": "Tüm tarayıcılar kapatıldı ve bot durumları sıfırlandı.",
        "system_overloaded": "Sistem aşırı yüklendi (CPU/RAM %99), botlar durduruluyor...",
        "system_overloaded_wait": "Sistem aşırı yüklü, bot {} bekliyor...",
        "bots_started": "Toplam {} bot başlatıldı.",
        "bots_stopped_final": "Botlar durduruldu. Son izleyici sayısı: {}",
        "proxy_file_selected": "Proxy dosyası seçildi ve kopyalandı: {}",
        "chromedriver_selected": "ChromeDriver yolu seçildi: {}",
        "close_prompt": "Programı kapatmak istediğinizden emin misiniz?"
    },
    "English": {
        "title": "KICK BOT CONTROL PANEL",
        "target_url": "Target URL:",
        "bot_count": "Bot Count:",
        "use_proxy": "Use Proxy",
        "select_proxy_file": "Select Proxy File",
        "select_chromedriver": "Select ChromeDriver Path",
        "start_bots": "START BOTS",
        "stop_bots": "STOP BOTS",
        "clear_logs": "Clear Logs",
        "sent_bots": "Sent Bots:",
        "viewer_count": "Viewer Count:",
        "proxy_stats": "Proxy Statistics:",
        "bot_status": "Bot Status:",
        "system_usage": "System Usage:",
        "cpu_usage": "CPU Usage: 0%",
        "ram_usage": "RAM Usage: 0%",
        "log_title": "Operation Log:",
        "copyright": "Copyright © 2025 KICK BOT - Versiyon 1.0",
        "theme_select": "Select a Theme",
        "chromedriver_not_found": "ChromeDriver not found: {}. Please select the ChromeDriver path.",
        "chromedriver_found": "ChromeDriver found: {}",
        "invalid_bot_count": "Bot count must be a valid positive number.",
        "invalid_url": "Enter a valid URL (e.g., https://kick.com/stream).",
        "no_proxy_file": "No proxy file selected, proceeding without proxies.",
        "channel_not_live": "Channel ({}) is not currently live.",
        "starting_bots": "{} bots are starting ({}), Initial viewers: {}",
        "no_proxies": "Proxy list is empty, proceeding without proxies.",
        "insufficient_proxies": "Insufficient proxies: {} available, {} bots requested.",
        "headless_active": "Bot {}: Headless mode active, browser running invisibly.",
        "bot_success": "Bot {} connected to the stream and video is playing (Selenium): {}",
        "video_not_found": "Bot {}: Video element not found, page loaded but playback couldn't start: {}",
        "quality_button_clicked": "Bot {}: Quality button clicked.",
        "quality_set": "Bot {}: Quality set to 160p.",
        "quality_failed": "Bot {}: Failed to set quality, quality button or 160p option not found.",
        "proxy_failed": "Bot {}: No available proxies left!",
        "bot_error": "Bot {}: {} - {}",
        "proxy_removed": " | Proxy removed: {}",
        "viewer_updated": "Viewer count updated: {}",
        "logs_cleared": "Logs cleared.",
        "stopping_bots": "Stopping bots...",
        "bots_stopped": "All browsers closed and bot statuses reset.",
        "system_overloaded": "System overloaded (CPU/RAM 99%), stopping bots...",
        "system_overloaded_wait": "System overloaded, bot {} is waiting...",
        "bots_started": "Total {} bots started.",
        "bots_stopped_final": "Bots stopped. Final viewer count: {}",
        "proxy_file_selected": "Proxy file selected and copied: {}",
        "chromedriver_selected": "ChromeDriver path selected: {}",
        "close_prompt": "Are you sure you want to close the program?"
    }
}

def get_log_file():
    """Tarih bazlı log dosyası yolu oluştur ve logs klasörünü oluştur."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return os.path.join(log_dir, f"bot_log_{time.strftime('%Y-%m-%d')}.txt")

def validate_proxy(proxy):
    """Proxy formatını doğrula: http, socks5, user:pass destekli."""
    pattern = r'^(?:(http|socks5)://)?(?:([^:]+:[^@]+@)?)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
    match = re.match(pattern, proxy)
    if match:
        protocol = match.group(1) or "http"
        ip = match.group(3)
        port = match.group(4)
        return protocol, ip, port
    return None

def load_proxies(proxy_file_path):
    """Proxy dosyasından geçerli proxy'leri yükle."""
    proxies = []
    try:
        with open(proxy_file_path, "r") as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    if validate_proxy(proxy):
                        proxies.append(proxy)
                    else:
                        with open(get_log_file(), "a", encoding="utf-8") as f:
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [UYARI] Geçersiz proxy formatı: {proxy}\n")
        return proxies
    except FileNotFoundError:
        return []

def select_proxy_file(log_box):
    """Proxy dosyası seç ve kopyala."""
    global proxy_file
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        proxy_file = f"proxy_{timestamp}.txt"
        shutil.copy(file_path, proxy_file)
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[BILGI] {languages[current_language]['proxy_file_selected'].format(proxy_file)}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        return proxy_file
    return None

def select_chrome_path(log_box, entry_url, entry_count, proxy_check, btn_select_proxy, btn_start, btn_stop, btn_clear_log):
    """ChromeDriver yolunu seç ve alanları aktif et."""
    global chrome_path
    file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
    if file_path:
        chrome_path = file_path
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[BILGI] {languages[current_language]['chromedriver_selected'].format(chrome_path)}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        # Alanları aktif et
        entry_url.config(state="normal")
        entry_count.config(state="normal")
        proxy_check.config(state="normal")
        btn_select_proxy.config(state="normal" if proxy_var.get() else "disabled")
        btn_start.config(state="normal")
        btn_stop.config(state="normal")
        btn_clear_log.config(state="normal")
    return chrome_path

def get_channel_name(url):
    """URL'den kanal adını çıkar."""
    parsed_url = urlparse(url)
    return parsed_url.path.strip("/")

def get_viewer_count(channel_name):
    """API'den izleyici sayısını ve yayın durumunu al."""
    try:
        api_url = f"https://kick.com/api/v1/channels/{channel_name}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            is_live = data.get("livestream", {}).get("is_live", False)
            viewer_count = data.get("livestream", {}).get("viewer_count", 0)
            return is_live, viewer_count
        else:
            return False, 0
    except Exception as e:
        return False, 0

def update_viewer_count(channel_name, viewer_var, log_box):
    """İzleyici sayısını 60 saniyede bir güncelle."""
    is_live, viewer_count = get_viewer_count(channel_name)
    viewer_var.set(str(viewer_count))
    log_box.config(state="normal")
    log_box.insert(tk.END, f"[BILGI] {languages[current_language]['viewer_updated'].format(viewer_count)}\n")
    log_box.yview(tk.END)
    log_box.config(state="disabled")
    log_box.after(60000, update_viewer_count, channel_name, viewer_var, log_box)

async def visit_url(url, bot_id, log_queue, use_proxy, proxy_list, used_proxies, proxy_stats, cancel_event):
    driver = None
    try:
        # Selenium ayarları
        options = Options()
        options.add_argument("--headless=chrome")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-accelerated-video-decode")
        options.add_argument("--mute-audio")  # Sesleri kapat
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Proxy ayarı
        proxy_url = None
        if use_proxy and proxy_list:
            if not proxy_list:
                message = f"[UYARI] {languages[current_language]['proxy_failed'].format(bot_id)}"
                log_queue.put(message)
                with open(get_log_file(), "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                return False
            proxy_url = random.choice(proxy_list)
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            protocol, _, _ = validate_proxy(proxy_url)
            if protocol == "http":
                proxy.http_proxy = proxy_url
                proxy.ssl_proxy = proxy_url
            elif protocol == "socks5":
                proxy.socks_proxy = proxy_url
                proxy.socks_version = 5
            capabilities = webdriver.DesiredCapabilities.CHROME
            proxy.add_to_capabilities(capabilities)
            try:
                if not os.path.exists(chrome_path):
                    message = f"[HATA] {languages[current_language]['chromedriver_not_found'].format(chrome_path)}"
                    log_queue.put(message)
                    with open(get_log_file(), "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                    return False
                service = Service(executable_path=chrome_path)
                driver = webdriver.Chrome(
                    service=service,
                    options=options,
                    desired_capabilities=capabilities
                )
            except SessionNotCreatedException as e:
                message = f"[HATA] {languages[current_language]['bot_error'].format(bot_id, str(e), url)}\n" \
                          f"[BILGI] {languages[current_language]['chromedriver_selected']}: https://chromedriver.chromium.org/downloads"
                log_queue.put(message)
                with open(get_log_file(), "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                return False
        else:
            try:
                if not os.path.exists(chrome_path):
                    message = f"[HATA] {languages[current_language]['chromedriver_not_found'].format(chrome_path)}"
                    log_queue.put(message)
                    with open(get_log_file(), "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                    return False
                service = Service(executable_path=chrome_path)
                driver = webdriver.Chrome(
                    service=service,
                    options=options
                )
            except SessionNotCreatedException as e:
                message = f"[HATA] {languages[current_language]['bot_error'].format(bot_id, str(e), url)}\n" \
                          f"[BILGI] {languages[current_language]['chromedriver_selected']}: https://chromedriver.chromium.org/downloads"
                log_queue.put(message)
                with open(get_log_file(), "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                return False
        
        # Açık tarayıcıyı listeye ekle
        drivers.append(driver)

        # Bot tespitini önleme
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        log_queue.put(f"[BILGI] {languages[current_language]['headless_active'].format(bot_id)}")
        
        # Sayfayı aç
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        # Video oynatımını kontrol et ve oynat
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            video = driver.find_element(By.TAG_NAME, "video")
            driver.execute_script("arguments[0].muted = true;", video)  # Videoyu sessize al
            driver.execute_script("arguments[0].play();", video)
            # Oynatma durumunu doğrula
            is_playing = driver.execute_script("return arguments[0].paused === false;", video)
            if not is_playing:
                driver.execute_script("arguments[0].play();", video)
            # Rastgele fare hareketleri, kaydırma ve tıklama
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(100, 500), random.randint(100, 500)).click().perform()
            driver.execute_script("window.scrollBy(0, 500);")
            actions.move_by_offset(random.randint(-200, 200), random.randint(-200, 200)).click().perform()
            message = f"[BAŞARILI] {languages[current_language]['bot_success'].format(bot_id, url)}"
            log_queue.put(message)

            # Kaliteyi 160p’ye ayarla
            try:
                # Kalite/Ayarlar butonunu bul ve tıkla
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Kalite' or contains(@aria-label, 'quality')]"))
                ).click()
                log_queue.put(f"[BILGI] {languages[current_language]['quality_button_clicked'].format(bot_id)}")
                
                # 160p seçeneğini bul ve tıkla
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '160p')]"))
                ).click()
                log_queue.put(f"[BILGI] {languages[current_language]['quality_set'].format(bot_id)}")
            except TimeoutException:
                log_queue.put(f"[UYARI] {languages[current_language]['quality_failed'].format(bot_id)}")

        except TimeoutException:
            message = f"[UYARI] {languages[current_language]['video_not_found'].format(bot_id, url)}"
        
        log_queue.put(message)
        with open(get_log_file(), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        
        # Başarılı proxy'yi used listesine taşı
        if use_proxy and proxy_url:
            proxy_list.remove(proxy_url)
            used_proxies.append(proxy_url)
            proxy_stats["working"] += 1
        
        # Durdurulana kadar yayında kal
        while not cancel_event.is_set():
            await asyncio.sleep(10)
        
        driver.quit()
        drivers.remove(driver)
        return True
    except Exception as e:
        message = f"[HATA] {languages[current_language]['bot_error'].format(bot_id, str(e), url)}"
        if use_proxy and proxy_url and proxy_url in proxy_list:
            proxy_list.remove(proxy_url)
            proxy_stats["failed"] += 1
            message += f"{languages[current_language]['proxy_removed'].format(proxy_url)}"
        log_queue.put(message)
        with open(get_log_file(), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        if driver:
            driver.quit()
            if driver in drivers:
                drivers.remove(driver)
        return False

def update_log(log_box, log_queue):
    while True:
        try:
            message = log_queue.get_nowait()
            log_box.config(state="normal")
            log_box.insert(tk.END, message + "\n")
            log_box.yview(tk.END)
            log_boxuencias
        except queue.Empty:
            break
    log_box.after(100, update_log, log_box, log_queue)

def update_system_stats(cpu_meter, ram_meter):
    """CPU ve RAM kullanımını güncelle (Meter ile)."""
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    cpu_meter.configure(amountused=cpu_usage)
    ram_meter.configure(amountused=ram_usage)
    cpu_meter.after(2000, update_system_stats, cpu_meter, ram_meter)

def clear_log(log_box):
    log_box.config(state="normal")
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, f"[BILGI] {languages[current_language]['logs_cleared']}\n")
    log_box.yview(tk.END)
    log_box.config(state="disabled")

def stop_bots(log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, total_bots):
    global cancel_event, drivers
    if cancel_event:
        cancel_event.set()
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[BILGI] {languages[current_language]['stopping_bots']}\n")
        # Tüm açık tarayıcıları kapat
        for driver in drivers:
            try:
                driver.quit()
            except:
                pass
        drivers.clear()
        # Bot durum alanını sıfırla
        for widget in status_frame.winfo_children():
            widget.destroy()
        max_display = 20
        cols_per_row = 10
        labels = []
        for i in range(min(total_bots, max_display)):
            row = i // cols_per_row
            col = i % cols_per_row
            label = ttk.Label(status_frame, text="", width=3, background=COLOR_IDLE, relief="solid", borderwidth=1)
            label.grid(row=row, column=col, pady=2, padx=2, sticky="w")
            labels.append(label)
        log_box.insert(tk.END, f"[BILGI] {languages[current_language]['bots_stopped']}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        btn_start.config(state="normal")
        btn_stop.config(state="disabled")
        btn_select_chrome.config(state="normal")
        # Alanları aktif et
        entry_url.config(state="normal")
        entry_count.config(state="normal")
        proxy_check.config(state="normal")
        btn_select_proxy.config(state="normal" if proxy_var.get() else "disabled")

def is_system_overloaded():
    """Sistem yükü kontrolü, eşik %99."""
    return psutil.cpu_percent() > 99 or psutil.virtual_memory().percent > 99

def check_system_load(total_bots, log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame):
    """Tüm botlar aktif olduktan sonra sistem yükünü kontrol et."""
    active_bots = len(drivers)
    if active_bots >= total_bots:  # Tüm botlar aktifse kontrol başlasın
        if is_system_overloaded():
            log_box.config(state="normal")
            log_box.insert(tk.END, f"[UYARI] {languages[current_language]['system_overloaded']}\n")
            log_box.config(state="disabled")
            stop_bots(log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, total_bots)
        else:
            log_box.after(5000, check_system_load, total_bots, log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame)

def update_proxy_stats(stats_label, proxy_stats):
    """Proxy istatistiklerini güncelle."""
    stats_label.config(text=f"{languages[current_language]['proxy_stats']} Toplam: {proxy_stats['total']}, Çalışan: {proxy_stats['working']}, Hatalı: {proxy_stats['failed']}")

def toggle_proxy_file_button(proxy_var, btn_select_proxy):
    """Proxy Kullan işaretlenirse dosya seç butonunu aktif et."""
    btn_select_proxy.config(state="normal" if proxy_var.get() else "disabled")

def on_closing(root, log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, total_bots):
    """Program kapatılırken uyarı göster ve tarayıcıları temizle."""
    if messagebox.askokcancel("Kapat", languages[current_language]["close_prompt"]):
        stop_bots(log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, total_bots)
        root.destroy()

def start_bots(entry_url, entry_count, log_box, count_var, viewer_var, status_frame, progress_bar, root, btn_start, btn_stop, btn_select_chrome, proxy_var, proxy_check, btn_select_proxy, stats_label):
    global bot_tasks, cancel_event, proxy_list, used_proxies, proxy_stats, proxy_file, drivers
    url = entry_url.get().strip()
    try:
        total_bots = int(entry_count.get())
        if total_bots <= 0:
            raise ValueError("Bot sayısı pozitif olmalı.")
    except ValueError:
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[UYARI] {languages[current_language]['invalid_bot_count']}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        return

    if not url or not url.startswith("https://"):
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[UYARI] {languages[current_language]['invalid_url']}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        return

    if not os.path.exists(chrome_path):
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[UYARI] {languages[current_language]['chromedriver_not_found'].format(chrome_path)}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        return

    if proxy_var.get() and not proxy_file:
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[UYARI] {languages[current_language]['no_proxy_file']}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        proxy_var.set(False)

    # Kanal adı ve yayın durumu kontrolü
    channel_name = get_channel_name(url)
    is_live, viewer_count = get_viewer_count(channel_name)
    viewer_var.set(str(viewer_count))
    if not is_live:
        log_box.config(state="normal")
        log_box.insert(tk.END, f"[UYARI] {languages[current_language]['channel_not_live'].format(channel_name)}\n")
        log_box.yview(tk.END)
        log_box.config(state="disabled")
        return

    log_box.config(state="normal")
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, f"[BILGI] {languages[current_language]['starting_bots'].format(total_bots, url, viewer_count)}\n")
    count_var.set(str(total_bots))
    progress_bar["value"] = total_bots
    progress_bar["maximum"] = total_bots
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")
    btn_select_chrome.config(state="disabled")

    # URL, bot sayısı ve proxy alanlarını devre dışı bırak
    entry_url.config(state="disabled")
    entry_count.config(state="disabled")
    proxy_check.config(state="disabled")
    btn_select_proxy.config(state="disabled")

    # İzleyici sayısını güncelle
    log_box.after(60000, update_viewer_count, channel_name, viewer_var, log_box)

    for widget in status_frame.winfo_children():
        widget.destroy()

    labels = []
    max_display = 20
    cols_per_row = 10
    for i in range(min(total_bots, max_display)):
        row = i // cols_per_row
        col = i % cols_per_row
        label = ttk.Label(status_frame, text="", width=3, background=COLOR_IDLE, relief="solid", borderwidth=1)
        label.grid(row=row, column=col, pady=2, padx=2, sticky="w")
        labels.append(label)

    log_queue = queue.Queue()
    cancel_event = asyncio.Event()
    use_proxy = proxy_var.get()
    proxy_list = load_proxies(proxy_file) if use_proxy and proxy_file else []
    used_proxies.clear()
    proxy_stats = {"total": len(proxy_list), "working": 0, "failed": 0}
    update_proxy_stats(stats_label, proxy_stats)

    if use_proxy and not proxy_list:
        log_queue.put(f"[UYARI] {languages[current_language]['no_proxies']}")
        use_proxy = False
        proxy_var.set(False)

    if use_proxy and len(proxy_list) < total_bots:
        log_queue.put(f"[UYARI] {languages[current_language]['insufficient_proxies'].format(len(proxy_list), total_bots)}")
        total_bots = min(total_bots, len(proxy_list))

    async def run_bots():
        started_bots = 0
        bot_tasks.clear()
        # Tüm botları sırayla başlat
        for i in range(total_bots):
            if cancel_event.is_set():
                break
            while is_system_overloaded():
                log_queue.put(f"[UYARI] {languages[current_language]['system_overloaded_wait'].format(i+1)}")
                await asyncio.sleep(1)
            bot_id = i + 1
            bot_tasks.append(visit_url(url, bot_id, log_queue, use_proxy, proxy_list, used_proxies, proxy_stats, cancel_event))
            label_idx = i % max_display
            labels[label_idx].config(background=COLOR_SUCCESS)  # Direkt yeşil
            started_bots += 1

        # Tüm botların sonucunu bekle
        results = await asyncio.gather(*bot_tasks, return_exceptions=True)
        for i, result in enumerate(results):
            label_idx = i % max_display
            if not result:
                labels[label_idx].config(background=COLOR_FAILED)
            update_proxy_stats(stats_label, proxy_stats)
            root.update_idletasks()

        log_queue.put(f"[BILGI] {languages[current_language]['bots_started'].format(started_bots)}")
        # Tüm botlar aktif olduktan sonra sistem yükünü kontrol et
        log_box.after(5000, check_system_load, total_bots, log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame)
        is_live, viewer_count = get_viewer_count(channel_name)
        viewer_var.set(str(viewer_count))
        message = f"[BILGI] {languages[current_language]['bots_stopped_final'].format(viewer_count)}"
        log_queue.put(message)
        with open(get_log_file(), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        btn_start.config(state="normal")
        btn_stop.config(state="disabled")
        btn_select_chrome.config(state="normal")
        entry_url.config(state="normal")
        entry_count.config(state="normal")
        proxy_check.config(state="normal")
        btn_select_proxy.config(state="normal" if proxy_var.get() else "disabled")
        log_box.config(state="disabled")

    def run_async_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bots())
        loop.close()

    threading.Thread(target=run_async_in_thread, daemon=True).start()
    update_log(log_box, log_queue)

def update_language(event, root, title_label, url_label, bot_count_label, proxy_check, btn_select_proxy, btn_select_chrome, btn_start, btn_stop, btn_clear_log, sent_bots_label, viewer_count_label, proxy_stats_label, stats_label, bot_status_label, system_usage_label, theme_label, log_title_label):
    global current_language
    current_language = language_combobox.get()
    # Tüm GUI elemanlarını güncelle
    title_label.config(text=languages[current_language]["title"])
    url_label.config(text=languages[current_language]["target_url"])
    bot_count_label.config(text=languages[current_language]["bot_count"])
    proxy_check.config(text=languages[current_language]["use_proxy"])
    btn_select_proxy.config(text=languages[current_language]["select_proxy_file"])
    btn_select_chrome.config(text=languages[current_language]["select_chromedriver"])
    btn_start.config(text=languages[current_language]["start_bots"])
    btn_stop.config(text=languages[current_language]["stop_bots"])
    btn_clear_log.config(text=languages[current_language]["clear_logs"])
    sent_bots_label.config(text=languages[current_language]["sent_bots"])
    viewer_count_label.config(text=languages[current_language]["viewer_count"])
    proxy_stats_label.config(text=languages[current_language]["proxy_stats"])
    stats_label.config(text=f"{languages[current_language]['proxy_stats']} Toplam: 0, Çalışan: 0, Hatalı: 0")
    bot_status_label.config(text=languages[current_language]["bot_status"])
    system_usage_label.config(text=languages[current_language]["system_usage"])
    theme_label.config(text=languages[current_language]["theme_select"])
    log_title_label.config(text=languages[current_language]["log_title"])
    copyright_label.config(text=languages[current_language]["copyright"])

def update_theme(event, root):
    selected_theme = theme_combobox.get()
    root.style.theme_use(selected_theme)

# GUI başlat
root = ttk.Window(themename="darkly")
root.title("Kick Bot (Pro)")
root.geometry("850x900")
root.resizable(False, False)
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.iconbitmap("program.ico")

# Özel stiller
style = ttk.Style()
style.configure("Custom.TEntry", lightcolor="#00ff00", fieldbackground="#2d2d2d", foreground="#ffffff", padding=5)
style.configure("Custom.TButton", font=("Arial", 11, "bold"), padding=10)
style.map("Custom.TButton", background=[("active", "#00cc00")])
style.configure("Large.TButton", font=("Arial", 14, "bold"), padding=15)
style.map("Large.TButton", background=[("active", "#00cc00")])
style.configure("Custom.TCheckbutton", font=("Arial", 11), foreground="#ffffff")
style.configure("Count.TLabel", font=("Arial", 14, "bold"), foreground="#00ff00", background="#2d2d2d", padding=(12, 6), anchor="center")
style.configure("Stats.TLabel", font=("Arial", 10), foreground="#ffffff", background="#2d2d2d")
style.configure("Viewer.TLabel", font=("Arial", 12, "bold"), foreground="#00ff00", background="#2d2d2d", padding=(12, 6), anchor="center")
style.configure("System.TLabel", font=("Arial", 10, "bold"), foreground="#ffffff", background="#2d2d2d")
style.configure("Custom.Scrollbar", troughcolor="#2d2d2d", background="#00ff00", width=8)
style.layout("Vertical.Custom.Scrollbar", [
    ("Vertical.Scrollbar.trough", {
        "children": [
            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "ns"})
        ],
        "sticky": "ns"
    })
])
style.layout("Horizontal.Custom.Scrollbar", [
    ("Horizontal.Scrollbar.trough", {
        "children": [
            ("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "ew"})
        ],
        "sticky": "ew"
    })
])

frame = ttk.Frame(root, padding=20, style="dark.TFrame")
frame.pack(fill=tk.BOTH, expand=True)

# Tema seçimi (dil seçeneğinin soluna)
theme_label = ttk.Label(frame, text=languages[current_language]["theme_select"], font=("Arial", 10, "bold"), foreground="#ffffff")
theme_label.grid(row=0, column=2, sticky="ne", pady=(0, 20), padx=(0, 10))
theme_combobox = ttk.Combobox(frame, values=["darkly", "flatly", "litera", "superhero", "cyborg", "vapor"], state="readonly", width=10)
theme_combobox.set("darkly")
theme_combobox.grid(row=0, column=2, sticky="ne", pady=(0, 20))

# Dil seçeneği (sağ üst köşe)
language_combobox = ttk.Combobox(frame, values=["Türkçe", "English"], state="readonly", width=10)
language_combobox.set("Türkçe")
language_combobox.grid(row=0, column=3, sticky="ne", pady=(0, 20))

# Başlık
title_label = ttk.Label(frame, text=languages[current_language]["title"], font=("Arial", 22, "bold"), foreground="#00ff00", anchor="center")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

# URL girişi
url_label = ttk.Label(frame, text=languages[current_language]["target_url"], font=("Arial", 12, "bold"), foreground="#ffffff")
url_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_url = ttk.Entry(frame, width=50, font=("Arial", 11), style="Custom.TEntry")
entry_url.grid(row=1, column=1, columnspan=3, pady=5, padx=5, sticky="w")

# Bot sayısı girişi
bot_count_label = ttk.Label(frame, text=languages[current_language]["bot_count"], font=("Arial", 12, "bold"), foreground="#ffffff")
bot_count_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_count = ttk.Entry(frame, width=10, font=("Arial", 11), style="Custom.TEntry")
entry_count.grid(row=2, column=1, sticky="w", pady=5, padx=5)

# Proxy seçeneği
proxy_var = tk.BooleanVar(value=False)
proxy_check = ttk.Checkbutton(frame, text=languages[current_language]["use_proxy"], variable=proxy_var, style="Custom.TCheckbutton", command=lambda: toggle_proxy_file_button(proxy_var, btn_select_proxy))
proxy_check.grid(row=2, column=2, sticky="w", pady=5, padx=5)

# Proxy dosya seç butonu
btn_select_proxy = ttk.Button(frame, text=languages[current_language]["select_proxy_file"], style="info.Custom.TButton", command=lambda: select_proxy_file(log_box), state="disabled")
btn_select_proxy.grid(row=2, column=3, sticky="w", pady=5, padx=5)

# Chrome yolu seç butonu
btn_select_chrome = ttk.Button(frame, text=languages[current_language]["select_chromedriver"], style="info.Custom.TButton", command=lambda: select_chrome_path(log_box, entry_url, entry_count, proxy_check, btn_select_proxy, btn_start, btn_stop, btn_clear_log))
btn_select_chrome.grid(row=3, column=0, columnspan=2, sticky="w", pady=5, padx=5)

# Gönderilen bot sayısı
sent_bots_label = ttk.Label(frame, text=languages[current_language]["sent_bots"], font=("Arial", 12, "bold"), foreground="#ffffff")
sent_bots_label.grid(row=4, column=0, sticky="w", pady=5, padx=5)
count_var = tk.StringVar(value="0")
label_count = ttk.Label(
    frame,
    textvariable=count_var,
    style="Count.TLabel",
    relief="solid",
    borderwidth=2,
    width=10
)
label_count.grid(row=4, column=1, sticky="w", pady=5, padx=5)

# İzleyici sayısı
viewer_var = tk.StringVar(value="0")
viewer_count_label = ttk.Label(frame, text=languages[current_language]["viewer_count"], font=("Arial", 12, "bold"), foreground="#ffffff")
viewer_count_label.grid(row=5, column=0, sticky="w", pady=5, padx=5)
label_viewer = ttk.Label(
    frame,
    textvariable=viewer_var,
    style="Viewer.TLabel",
    relief="solid",
    borderwidth=2,
    width=10
)
label_viewer.grid(row=5, column=1, sticky="w", pady=5, padx=5)

# Proxy istatistikleri
proxy_stats_label = ttk.Label(frame, text=languages[current_language]["proxy_stats"], font=("Arial", 12, "bold"), foreground="#ffffff")
proxy_stats_label.grid(row=6, column=0, sticky="w", pady=5, padx=5)
stats_label = ttk.Label(frame, text=f"{languages[current_language]['proxy_stats']} Toplam: 0, Çalışan: 0, Hatalı: 0", style="Stats.TLabel")
stats_label.grid(row=6, column=1, columnspan=3, sticky="w", pady=5, padx=5)

# Botları Başlat ve Durdur butonları (yan yana, büyük)
btn_start = ttk.Button(
    frame,
    text=languages[current_language]["start_bots"],
    style="success.Large.TButton",
    command=lambda: start_bots(entry_url, entry_count, log_box, count_var, viewer_var, status_frame, progress_bar, root, btn_start, btn_stop, btn_select_chrome, proxy_var, proxy_check, btn_select_proxy, stats_label)
)
btn_start.grid(row=8, column=0, pady=10, padx=5, sticky="w")

btn_stop = ttk.Button(
    frame,
    text=languages[current_language]["stop_bots"],
    style="danger.Large.TButton",
    command=lambda: stop_bots(log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, int(entry_count.get())),
    state="disabled"
)
btn_stop.grid(row=8, column=1, pady=10, padx=5, sticky="w")

# Logları Temizle butonu
btn_clear_log = ttk.Button(
    frame,
    text=languages[current_language]["clear_logs"],
    style="warning.Custom.TButton",
    command=lambda: clear_log(log_box)
)
btn_clear_log.grid(row=8, column=2, pady=10, padx=5, sticky="w")

# İlerleme çubuğu
progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=700, style="success.Horizontal.TProgressbar")
progress_bar.grid(row=9, column=0, columnspan=4, pady=10)

# Bot durumları
bot_status_label = ttk.Label(frame, text=languages[current_language]["bot_status"], font=("Arial", 12, "bold"), foreground="#ffffff")
bot_status_label.grid(row=10, column=0, columnspan=4, sticky="w", pady=5, padx=5)
status_frame = ttk.Frame(frame, style="dark.TFrame")
status_frame.grid(row=11, column=0, columnspan=4, pady=5, sticky="w")

# CPU ve RAM göstergeleri (Meter widget’ı ile)
system_usage_label = ttk.Label(frame, text=languages[current_language]["system_usage"], font=("Arial", 12, "bold"), foreground="#ffffff")
system_usage_label.grid(row=12, column=0, sticky="w", pady=5, padx=5)

cpu_meter = Meter(
    frame,
    metersize=150,
    amounttotal=100,
    amountused=0,
    metertype="semi",
    subtext=languages[current_language]["cpu_usage"].split(":")[0],
    stripethickness=10,
    bootstyle="success",  # meterstyle yerine bootstyle kullanıldı
    textfont=("Arial", 10, "bold"),
    subtextfont=("Arial", 8)
)
cpu_meter.grid(row=12, column=1, sticky="w", pady=5, padx=5)

ram_meter = Meter(
    frame,
    metersize=150,
    amounttotal=100,
    amountused=0,
    metertype="semi",
    subtext=languages[current_language]["ram_usage"].split(":")[0],
    stripethickness=10,
    bootstyle="success",  # meterstyle yerine bootstyle kullanıldı
    textfont=("Arial", 10, "bold"),
    subtextfont=("Arial", 8)
)
ram_meter.grid(row=12, column=2, sticky="w", pady=5, padx=5)

# İşlem günlüğü
log_title_label = ttk.Label(frame, text=languages[current_language]["log_title"], font=("Arial", 12, "bold"), foreground="#ffffff")
log_title_label.grid(row=13, column=0, columnspan=4, sticky="w", pady=5, padx=5)
log_frame = ttk.Frame(frame)
log_frame.grid(row=14, column=0, columnspan=4, pady=5, sticky="w")
log_box = tk.Text(log_frame, width=100, height=10, wrap=tk.WORD, font=("Arial", 10), bg="#1e1e1e", fg="#ffffff", state="disabled")
log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_box.yview, style="Custom.Scrollbar")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box.config(yscrollcommand=scrollbar.set)

# Copyright ve versiyon bilgisi (sağ alt köşe)
copyright_label = ttk.Label(frame, text=languages[current_language]["copyright"], font=("Arial", 10), foreground="#ffffff")
copyright_label.grid(row=15, column=3, sticky="se", pady=5, padx=5)

# ChromeDriver kontrolü
if not os.path.exists(chrome_path):
    log_box.config(state="normal")
    log_box.insert(tk.END, f"[UYARI] {languages[current_language]['chromedriver_not_found'].format(chrome_path)}\n")
    log_box.yview(tk.END)
    log_box.config(state="disabled")
    # Tüm alanları devre dışı bırak
    entry_url.config(state="disabled")
    entry_count.config(state="disabled")
    proxy_check.config(state="disabled")
    btn_select_proxy.config(state="disabled")
    btn_start.config(state="disabled")
    btn_stop.config(state="disabled")
    btn_clear_log.config(state="disabled")
else:
    log_box.config(state="normal")
    log_box.insert(tk.END, f"[BILGI] {languages[current_language]['chromedriver_found'].format(chrome_path)}\n")
    log_box.yview(tk.END)
    log_box.config(state="disabled")

# Sistem kullanımını güncelle
update_system_stats(cpu_meter, ram_meter)

# Dil değişimini bağla
language_combobox.bind("<<ComboboxSelected>>", lambda event: update_language(event, root, title_label, url_label, bot_count_label, proxy_check, btn_select_proxy, btn_select_chrome, btn_start, btn_stop, btn_clear_log, sent_bots_label, viewer_count_label, proxy_stats_label, stats_label, bot_status_label, system_usage_label, theme_label, log_title_label))

# Tema değişimini bağla
theme_combobox.bind("<<ComboboxSelected>>", lambda event: update_theme(event, root))

# Kapatma olayını bağla
root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, log_box, btn_start, btn_stop, btn_select_chrome, entry_url, entry_count, proxy_check, btn_select_proxy, status_frame, int(entry_count.get()) if entry_count.get().isdigit() else 0))

root.mainloop()
