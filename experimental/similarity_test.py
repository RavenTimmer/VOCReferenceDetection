from sentence_transformers import SentenceTransformer

texts =

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
text_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
