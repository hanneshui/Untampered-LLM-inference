#!/usr/bin/env python3
"""
Prompt Generator built by Wendelin Stark & Hannes Hui. First gets the current bitcoin hash as a number, which is unpredictable in advance. Later, it uses a large corpus and deterministically generates an llm prompt based on the bitcoin hash from sentences from this corpus.
"""

import requests
import random
import os
import sys
import time

# Config
BITCOIN_HASH_API = "https://blockchain.info/q/latesthash"
CORPUS_URL = "https://norvig.com/big.txt"
CORPUS_PATH = "big_corpus.txt"
TARGET_WORDS = 300
MIN_SENTENCES = 10
MAX_SENTENCES = 40

# Download the preset Text Corpus
def download_corpus(url: str, path: str) -> None:
    print(f"Downloading corpus from {url}")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024*16):
            f.write(chunk)
    print(f"Saved corpus to {path}\n")

# Get the current Bitcoin-Hash via API Request
def get_latest_bitcoin_hash_api(timeout: float = 5.0) -> str:
    resp = requests.get(BITCOIN_HASH_API, timeout=timeout)
    resp.raise_for_status()
    return resp.text.strip()

# Split the sentences of the corpus
def load_sentences(path: str) -> list[str]:
    text = open(path, "r", encoding="utf-8").read()
    #Split the sentences on . ! ? 
    raw_sents = []
    for sep in ['.', '?', '!']:
        text = text.replace(sep, '.')
    for part in text.split('.'):
        s = part.strip()
        if s:
            raw_sents.append(s)
    return raw_sents


def hash_to_mixed_text(hash_str: str,
                       corpus_path: str,
                       target_words: int = TARGET_WORDS) -> str:
    if not os.path.isfile(corpus_path):
        raise FileNotFoundError(f"Corpus not found")

    sentences = load_sentences(corpus_path)
    if len(sentences) < MIN_SENTENCES:
        raise ValueError("Corpus too small")

    # Create an integer seed from the hash_str and create a random number using that seed.
    seed = int(hash_str, 16)
    rng = random.Random(seed)

    # Decide how many sentences to pick
    k = rng.randint(MIN_SENTENCES, min(MAX_SENTENCES, len(sentences)))
    chosen_idxs = rng.sample(range(len(sentences)), k)
    picked = [sentences[i] for i in chosen_idxs]

    # Shuffle the order of the picked sentences
    rng.shuffle(picked)

    # Add the chosen sentences togehter and truncate at targeted word count. 
    all_text = " ".join(picked)
    words = all_text.split()
    return " ".join(words[:target_words])

def main():
    print("=== Bitcoin Hash → LLM-Prompt ===\n")
    choice = input("1) Fetch current Bitcoin hash via API  2) Enter the hash manually  [1/2]: ").strip()
    if choice == "1":
        try:
            block_hash = get_latest_bitcoin_hash_api()
            print("Fetched current hash:", block_hash)
        except Exception as e:
            print("Error fetching hash:", e)
            block_hash = input("Enter the hash manually: ").strip()
    else:
        block_hash = input("Enter current hash manually: ").strip()

    if not os.path.isfile(CORPUS_PATH):
        try:
            download_corpus(CORPUS_URL, CORPUS_PATH)
        except Exception as e:
            print("Error downloading corpus:", e)
            sys.exit(1)

    # Generate prompt
    try:
        prompt = hash_to_mixed_text(block_hash, CORPUS_PATH, TARGET_WORDS)
    except Exception as e:
        print("Error generating prompt:", e)
        sys.exit(1)

    print("\n=== Generated LLM-Prompt ===\n")
    print(prompt)

if __name__ == "__main__":
    main()
