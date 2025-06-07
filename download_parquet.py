import os
import gzip
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def download_cc_index_paths(index_url, local_path="cc-index-table.paths.gz"):
    print(f"Downloading cc-index-table.paths.gz from: {index_url}")
    try:
        response = requests.get(index_url, stream=True)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Downloaded index file successfully.")
        return local_path
    except Exception as e:
        print(f"Failed to download index file: {e}")
        return None


def extract_warc_paths(gz_path, start=0, limit=None):
    print(f"Extracting WARC paths from: {gz_path}")
    with gzip.open(gz_path, "rt") as f:
        paths = [line.strip() for line in f if "subset=warc" in line]

    sliced_paths = paths[start:start + limit] if limit is not None else paths[start:]
    print(f"Found {len(sliced_paths)} WARC index paths to download (from {start})")
    return sliced_paths


def download_single_parquet(path, base_url="https://data.commoncrawl.org", output_dir="index_files"):
    filename = os.path.basename(path)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    if os.path.exists(file_path):
        print(f"[SKIP] Already exists: {filename}")
        return filename

    try:
        print(f"[DOWNLOADING] Trying to download: {filename}")
        url = f"{base_url}/{path}"
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Downloaded: {filename}")
        return filename
    except Exception as e:
        print(f"[ERR] Failed to download {filename}: {e}")
        return None


def download_index_files(paths, max_workers=1):
    print(f"Starting parallel download with {max_workers} workers")
    downloaded = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single_parquet, path): path for path in paths}
        for future in as_completed(futures):
            result = future.result()
            if result:
                downloaded.append(result)

    print(f"Download complete. Total: {len(downloaded)} files.")
    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Download Common Crawl WARC index files (subset=warc)")
    parser.add_argument("--index-url", required=True, help="URL to cc-index-table.paths.gz")
    parser.add_argument("--start", type=int, default=0, help="Start index for WARC path selection")
    parser.add_argument("--limit", type=int, default=None, help="Number of WARC files to download")
    parser.add_argument("--threads", type=int, default=6, help="Number of threads for parallel download")
    args = parser.parse_args()

    gz_path = download_cc_index_paths(args.index_url)
    if not gz_path:
        return

    warc_paths = extract_warc_paths(gz_path, start=args.start, limit=args.limit)
    if not warc_paths:
        print("No WARC paths found with subset=warc")
        return

    download_index_files(warc_paths, max_workers=args.threads)


if __name__ == "__main__":
    main()
