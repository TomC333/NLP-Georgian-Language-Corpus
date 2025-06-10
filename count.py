import json
from collections import Counter

def is_georgian_char(ch):
    return '\u10A0' <= ch <= '\u10FF'

jsonl_file = "corpus.jsonl"

char_counter = Counter()
total_lines = 0
total_chars = 0

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            text = data.get("text", "")
            total_lines += 1
            for ch in text:
                if is_georgian_char(ch):
                    char_counter[ch] += 1
                    total_chars += 1
        except json.JSONDecodeError:
            continue

sorted_chars = char_counter.most_common()

print(f"Processed {total_lines} lines with {total_chars} Georgian characters.\n")
print(f"{'Char':^6} | {'Count':^8} | {'Frequency (%)':^14}")
print("-" * 32)
for ch, count in sorted_chars:
    freq = (count / total_chars) * 100
    print(f"  {ch}   | {count:8} | {freq:13.4f}")
