import pickle
import faiss

from sentence_transformers import SentenceTransformer
from api_interface import return_requests


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


original_text = "bij het vergaan van de Gouden Leeuw  , ibid. p. 114, is /. 7390.2.8 gered, voor f. 37069.4.1 ging verloren;"
year = 1633

request_results = return_requests("Gouden AND Leeuw", get_inv_numbers(year))
texts = [result['text'] for result in request_results if 'text' in result]


model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
text_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

dimension = text_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(text_embeddings)

query_embedding = model.encode([original_text], convert_to_numpy=True)

# === Step 5: Search and Display ===
top_k = 5
distances, indices = index.search(query_embedding, top_k)

print("\nTop Matching Snippets:\n")
for rank, idx in enumerate(indices[0]):
    print(f"=>  Rank {rank+1}")
    print(f"    Text: {texts[idx]}")
    print(f"    Score: {1 - distances[0][rank]:.4f} (higher is better)\n")
