import pickle
import faiss
import numpy as np
import re

from sentence_transformers import SentenceTransformer
from api_interface import return_requests
from entityRecognition import entity_recognition


dictionary = pickle.load(open('../data/inventory_dates.pkl', 'rb'))


def get_inv_numbers(year):
    """
    Get the inventory numbers for a range around the given year.
    """
    offsets = 1
    range_years = range(year - offsets, year + offsets)
    inv_numbers = set()

    for y in range_years:
        if y in dictionary:
            for inv_number in dictionary[y]:
                inv_numbers.add(inv_number)
        else:
            print(f"Year {y} not found in dictionary.")

    return list(inv_numbers)


def normalize(vecs):
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text)


if __name__ == "__main__":

    original_text = input("Enter the text to search for: ")
    original_text = clean_text(original_text)

    print()
    print(f"Original text: {original_text}")

    print()
    year = int(input("Enter the year: "))

    entities = entity_recognition(original_text)

    if entities:
        print("\nIdentified Entities:")
        for i, entity in enumerate(entities):
            print(f"{i + 1}: {entity['text']} (Type: {entity['entity']}, Score: {entity['score']:.4f})")
        print(f"{len(entities) + 1}: Enter a custom search term")

        choice = int(input("\nEnter the number of the entity you want to search on: ")) - 1
        if 0 <= choice < len(entities):
            selected_entity = entities[choice]['text']
            print(f"\nYou selected: {selected_entity}")
        elif choice == len(entities):
            selected_entity = input("\nEnter your custom search term: ").strip()
            print(f"You entered: {selected_entity}")
        else:
            print("\nInvalid choice. Exiting.")
            exit()
    else:
        print("\nNo entities found. Exiting.")
        exit()

    selected_entity = selected_entity.replace(" ", " AND ")

    print(f"\nSearching for: {selected_entity}")
    print(f"Year: {year}")
    print(f"Inventory Numbers: {get_inv_numbers(year)}\n")

    request_results = return_requests(
        selected_entity, get_inv_numbers(year), len(original_text))
    texts = [result['text'] for result in request_results if 'text' in result]

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    text_embeddings = normalize(model.encode(
        texts, convert_to_numpy=True, show_progress_bar=True))
    query_embedding = normalize(model.encode(
        [original_text], convert_to_numpy=True))

    index = faiss.IndexFlatIP(text_embeddings.shape[1])
    index.add(text_embeddings)

    top_k = 5
    distances, indices = index.search(query_embedding, top_k)

    print("\nTop Matching Snippets:\n")
    for rank, idx in enumerate(indices[0]):
        print(f"=>  Rank {rank + 1}")
        print(f"    Text: {texts[idx]}")
        print(f"    Cosine Similarity: {distances[0][rank]:.4f}\n")
