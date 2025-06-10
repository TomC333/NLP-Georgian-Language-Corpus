import os
import glob
import hashlib
import json
from collections import defaultdict
from trafilatura import extract
from datasketch import MinHash, MinHashLSH

def is_georgian(text, threshold=0.3):
    georgian_chars = sum(1 for ch in text if '\u10A0' <= ch <= '\u10FF')
    total_chars = len(text)
    return (georgian_chars / total_chars) > threshold if total_chars > 0 else False

def avg_word_length(words):
    if not words:
        return 0
    return sum(len(w) for w in words) / len(words)

def get_minhash(text, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for word in set(text.split()):
        m.update(word.encode("utf8"))
    return m

input_dir = "./extracted_texts"
output_jsonl = "corpus.jsonl"

stats = defaultdict(int)
lsh = MinHashLSH(threshold=0.9, num_perm=128)
minhashes = {}

print(f"Started processing from directory: {input_dir}")
print(f"Filtered, deduplicated sentences will be saved to: {output_jsonl}\n")

with open(output_jsonl, "w", encoding="utf-8") as out_f:
    for path in sorted(glob.glob(os.path.join(input_dir, "*.txt"))):
        stats["total"] += 1

        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()

        words = raw_text.split()

        if len(words) < 50 or len(words) > 10000:
            stats["length_fail"] += 1
            continue

        dot_ratio = raw_text.count(".") / len(raw_text) if len(raw_text) > 0 else 0
        if dot_ratio < 0.002:
            stats["dot_ratio_fail"] += 1
            continue

        awl = avg_word_length(words)
        if awl < 3.5 or awl > 8:
            stats["avg_word_len_fail"] += 1
            continue

        symbol_ratio = sum(1 for c in raw_text if not c.isalnum() and not c.isspace()) / len(raw_text)
        if symbol_ratio > 0.3:
            stats["symbol_ratio_fail"] += 1
            continue

        if not is_georgian(raw_text):
            stats["georgian_ratio_fail"] += 1
            continue

        mh = get_minhash(raw_text)
        if lsh.query(mh):
            stats["duplicates"] += 1
            continue

        sentences = [s.strip() for s in raw_text.split('.') if len(s.strip()) > 10]
        if len(sentences) < 3:
            stats["too_few_sentences"] += 1
            continue

        key = hashlib.md5(raw_text.encode("utf-8")).hexdigest()
        lsh.insert(key, mh)
        minhashes[key] = mh

        for sentence in sentences:
            if is_georgian(sentence):  # წინადადების დონეზეც გადავამოწმოთ
                out_f.write(json.dumps({"text": sentence}, ensure_ascii=False) + "\n")
                stats["kept"] += 1

        print(f"Accepted {os.path.basename(path)} with {len(sentences)} sentences")

print("\nSummary:")
for k, v in stats.items():
    print(f"  {k}: {v}")
