import os
import pyarrow.parquet as pq
import pandas as pd

index_dir = "index_files"
output_file = "possibly_georgian_urls.txt"
georgian_lang_codes = {"ka", "ka-GE", "kat", "GE", "GEO", "ge", "geo"}

url_set = set()
all_files = sorted([f for f in os.listdir(index_dir) if f.endswith(".gz.parquet")])
print(f"Total files to process: {len(all_files)}")

for idx, filename in enumerate(all_files, 1):
    file_path = os.path.join(index_dir, filename)
    print(f"[{idx}/{len(all_files)}] Processing: {filename}")

    try:
        table = pq.read_table(file_path, columns=["url", "content_languages"])
        df = table.to_pandas()
    except Exception as e:
        print(f"Failed to read {filename}: {e}")
        continue

    df = df.dropna(subset=["url"])

    lang_mask = df["content_languages"].isin(georgian_lang_codes)

    filtered_df = df[lang_mask]

    new_urls = filtered_df["url"].unique()
    url_set.update(new_urls)

    print(f"  + Found {len(new_urls)} new URLs (Total: {len(url_set)})")

print(f"\nFinished. Total unique Georgian URLs collected: {len(url_set)}")

with open(output_file, "w", encoding="utf-8") as f:
    for url in sorted(url_set):
        f.write(url + "\n")

print(f"Saved to: {output_file}")
