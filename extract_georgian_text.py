import os
import time
import threading
from trafilatura import fetch_url, extract
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_georgian(text, threshold=0.3):
    georgian_chars = sum(1 for ch in text if '\u10A0' <= ch <= '\u10FF')
    total_chars = len(text)
    return (georgian_chars / total_chars) > threshold if total_chars > 0 else False

input_file = "possibly_georgian_urls.txt"
output_dir = "extracted_texts"
os.makedirs(output_dir, exist_ok=True)

start_index = 1
max_workers = 10 

counters = {
    "total": 0,
    "saved": 0,
    "short": 0,
    "non_geo": 0,
    "download_fail": 0
}
lock = threading.Lock()

def process_url(idx_url):
    idx, url = idx_url
    with lock:
        counters["total"] += 1
    print(f"[{idx}] Fetching: {url}")

    downloaded = fetch_url(url)
    if not downloaded:
        print(f"  Skipped: download failed")
        with lock:
            counters["download_fail"] += 1
        return

    text = extract(downloaded)
    if not text or len(text.strip()) < 100:
        print(f"  Skipped: empty or too short")
        with lock:
            counters["short"] += 1
        return

    if not is_georgian(text):
        print(f"  Skipped: not enough Georgian characters")
        with lock:
            counters["non_geo"] += 1
        return

    with lock:
        file_index = start_index + counters["saved"]
        counters["saved"] += 1

    file_name = f"text_{file_index:05d}.txt"
    out_path = os.path.join(output_dir, file_name)
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(text)
    print(f"  Saved as: {file_name}")
    time.sleep(0.1)

with open(input_file, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Started processing URLs from: {input_file}")
print(f"Extracted texts will be saved to: {output_dir}")
print(f"Starting file index: {start_index}")
print(f"Thread pool size: {max_workers}\n")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(process_url, (i, url)) for i, url in enumerate(urls, 1)]
    for future in as_completed(futures):
        pass 

print("\nSummary:")
print(f"  Total URLs processed: {counters['total']}")
print(f"  Skipped (download fail): {counters['download_fail']}")
print(f"  Skipped (empty/short): {counters['short']}")
print(f"  Skipped (not Georgian enough): {counters['non_geo']}")
print(f"  Saved Georgian texts: {counters['saved']}")
