#!/usr/bin/env python3
"""
Read two differnt promts form the terminal, then rate their similarity using the TF-IDF vectorization.
"""
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Read the prompt from the terminal. Continue as long no empty line is inserted.
def read_prompt(label: str) -> str:
    print(f"Enter {label} (end input with a single '.' on its own line):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines)

# Comptute Cosine-Similarity between a pair of texts.
def compare_prompts(text1: str, text2: str) -> float:
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(sim_matrix[0][0])


def main():
    prompt1 = read_prompt("first prompt")
    if not prompt1:
        print("First prompt is empty.")
        sys.exit(1)
    prompt2 = read_prompt("second prompt")
    if not prompt2:
        print("Second prompt is empty.")
        sys.exit(1)

    # Compute similarity
    score = compare_prompts(prompt1, prompt2)
    print(f"\n The Cosine similarity between the two prompts is: {score:.4f}")

if __name__ == '__main__':
    main()

