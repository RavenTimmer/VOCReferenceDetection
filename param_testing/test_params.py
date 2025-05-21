import pickle
import faiss
import numpy as np
import re

import pandas as pd

from sentence_transformers import SentenceTransformer
import gc
import torch

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


def mean_reciprocal_rank(ranked_indices, correct_indices):
    """Compute Mean Reciprocal Rank (MRR) for the ranked indices."""
    for rank, idx in enumerate(ranked_indices, 1):
        if idx in correct_indices:
            return 1.0 / rank
    return 0.0


def mean_average_precision(ranked_indices, correct_indices):
    """Compute Mean Average Precision (MAP) for the ranked indices."""
    hits = 0
    sum_precisions = 0.0
    for i, idx in enumerate(ranked_indices, 1):
        if idx in correct_indices:
            hits += 1
            sum_precisions += hits / i
    if hits == 0:
        return 0.0
    return sum_precisions / hits


if __name__ == "__main__":
    source_texts = [
        "de Gouden Leeuw  is onbequaem bevonden omme met retouren naer ’t vaderlandt over te gaen, jaa is inwendich soo vergaen, dat, onaengesyen de handt daer extra-ordinaris aengehouden is, niet langer in ’t vaerwater sal connen continueren.",
        "zo is dat een en ander van die efficatie geweest dat de finale dispositie daarover is gesurcheert gebleven tot 30e daaraanvolgende , als wanneer Zijn Edelheyt desselvs zo even aangehaalde intentie wederom ten tapijte , en na het ingekomen advijs van den heere gouverneur-generaal Thedens de zake zooverre gebragt heeft , datter alsdoen g’arresteert is hem per het schip Amsterdam op den 6e november te laten vertrecken , en bij erlanginge van eenig favorabel berigt wegens den Javasen krijg (dog anders niet ) de Oude Zijp tot geselschap mede te geven , invoegen als den heere Valckenier op dien gestipuleerden dag dan ook met voormelte Amsterdam alleen de reyse van dese rheede ondernomen en het generalaat in behoorlijke forma aan desselvs successeur , den presenten heere gouverneur-generaal Johannes Thedens"
    ]

    inputs = [
        pd.read_csv('Gouden_Leeuw.csv'),
        pd.read_csv('Johannes_Thedens.csv')
    ]

    transformers = [
        'paraphrase-multilingual-MiniLM-L12-v2',
        'all-MiniLM-L6-v2',
        'distiluse-base-multilingual-cased-v2',
        'stsb-roberta-base',
        'LaBSE',
        'dbmdz/bert-base-historic-dutch-cased',
        'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        'distilbert-base-multilingual-cased',
        'GroNLP/bert-base-dutch-cased'
    ]

    model_ranking = {}
    for i, df in enumerate(inputs):
        print(f"\nProcessing file: {['Gouden_Leeuw.csv', 'Johannes_Thedens.csv'][i]}")
        texts = df['text'].tolist()
        correct_indices = set(df.index[df['correct'] == 1].tolist())
        original_text = source_texts[i]

        for model_name in transformers:
            print(f"\nEvaluating model: {model_name}")
            model = SentenceTransformer(model_name)
            text_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            query_embedding = model.encode([original_text], convert_to_numpy=True)

            index = faiss.IndexFlatIP(text_embeddings.shape[1])
            index.add(text_embeddings)
            top_k = min(5, len(texts))
            distances, indices = index.search(query_embedding, len(texts))
            ranked_indices = indices[0]

            mrr = mean_reciprocal_rank(ranked_indices, correct_indices)
            map_score = mean_average_precision(ranked_indices, correct_indices)
            print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
            print(f"Mean Average Precision (MAP): {map_score:.4f}")

            if model_name not in model_ranking:
                model_ranking[model_name] = []
            model_ranking[model_name].append({'file': ['Gouden_Leeuw.csv', 'Johannes_Thedens.csv'][i], 'MRR': mrr, 'MAP': map_score})

            del model
            torch.cuda.empty_cache()
            gc.collect()

    print("\nModel Ranking:")
    avg_scores = []
    for model_name, results in model_ranking.items():
        avg_mrr = np.mean([r['MRR'] for r in results])
        avg_map = np.mean([r['MAP'] for r in results])
        avg_scores.append((model_name, avg_mrr, avg_map, results))

    avg_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)

    for model_name, avg_mrr, avg_map, results in avg_scores:
        print(f"\nModel: {model_name}")
        for result in results:
            print(f"File: {result['file']}, MRR: {result['MRR']:.4f}, MAP: {result['MAP']:.4f}")
        print(f"Average MRR: {avg_mrr:.4f}, Average MAP: {avg_map:.4f}")

