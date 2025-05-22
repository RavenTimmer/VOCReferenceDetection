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


def remove_stopwords(text, stopword_file="voc_stopwords.txt"):
    with open(stopword_file, "r", encoding="utf-8") as f:
        stopwords = set(line.strip() for line in f if line.strip())

    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)


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
        "zo is dat een en ander van die efficatie geweest dat de finale dispositie daarover is gesurcheert gebleven tot 30e daaraanvolgende , als wanneer Zijn Edelheyt desselvs zo even aangehaalde intentie wederom ten tapijte , en na het ingekomen advijs van den heere gouverneur-generaal Thedens de zake zooverre gebragt heeft , datter alsdoen g’arresteert is hem per het schip Amsterdam op den 6e november te laten vertrecken , en bij erlanginge van eenig favorabel berigt wegens den Javasen krijg (dog anders niet ) de Oude Zijp tot geselschap mede te geven , invoegen als den heere Valckenier op dien gestipuleerden dag dan ook met voormelte Amsterdam alleen de reyse van dese rheede ondernomen en het generalaat in behoorlijke forma aan desselvs successeur , den presenten heere gouverneur-generaal Johannes Thedens",
        "Naderhant hebben wij Bantam onder scheut ende doel van canon met verscheyde schepen , jachten ende chaloupen , die andersints alhier ter reede vruchteloos sonder dienst souden gelegen hebben , beset gehouden ende de dichte ende de naeuwe besettinge tot op den llen januarij gecontinueert , als wanneer onse gemelte schepen (willende schuwen ende eviteeren het groot perijckel der branders , die den vijant op verscheyde tijden",
        "Ende sal haer het verlies van Don Felipe Cobo 3 ) met sijne vier vollaeden Conincks roeyschepen vol Chinese waeren (die tot asschen sijn verbrant den 5enmeert lestleden bij Sincapura ,. ) overgroote verslaegentheyt toebrengen Ende sal haer het verlies van Don Felipe Cobo 3 ) met sijne vier vollaeden Conincks roeyschepen vol Chinese waeren (die tot asschen sijn verbrant den 5enmeert lestleden bij Sincapura ,. ) overgroote verslaegentheyt toebrengen",
        "de overwinning  van Farrukh-siyar deed de rust in Patna terugkeeren, zowel als in de Gangesdelta; 16 maart ging het V.O.C. personeel weer naar Kasimbazar, waar de duan Murshid Kulikhan het vriendelijk ontving, hij verwierf de naam Jafarkhan; Jacob Dijkhoff, opperhoofd van Patna, vertrok met zijn personeel 1 maart derwaarts, het vorige personeel"
    ]

    files = [
        'Gouden_Leeuw.csv',
        'Johannes_Thedens.csv',
        'Bantam.csv',
        'Don_Felipe.csv',
        'Patna.csv'
    ]

    transformers = [
        # 'emanjavacas/GysBERT-v2', # Mentioned in paper
        'paraphrase-multilingual-MiniLM-L12-v2',
        'all-MiniLM-L6-v2',
        'distiluse-base-multilingual-cased-v2',
        'LaBSE',
        'NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers'
    ]

    model_ranking = {}

    # Precumputing all the input texts so they do not have to be computed multiple times
    # Idk if it adds any speedup, but it looks better
    inputs = [pd.read_csv(file) for file in files]
    precomputed_inputs = []
    for i, data in enumerate(inputs):
        texts = data['text'].tolist()
        original_text = source_texts[i]

        texts_original = texts
        query_original = original_text

        texts_cleaned = [clean_text(t) for t in texts]
        query_cleaned = clean_text(original_text)

        texts_cleaned_stop = [clean_text(remove_stopwords(t)) for t in texts]
        query_cleaned_stop = clean_text(remove_stopwords(original_text))

        precomputed_inputs.append({
            'texts_original': texts_original,
            'query_original': query_original,
            'texts_cleaned': texts_cleaned,
            'query_cleaned': query_cleaned,
            'texts_cleaned_stop': texts_cleaned_stop,
            'query_cleaned_stop': query_cleaned_stop,
            'data': data
        })


    # Running all the actuall embeddings on the different inputs that were computed
    for i, file_inputs in enumerate(precomputed_inputs):
        print(f"\nProcessing file: {files[i]}")
        data = file_inputs['data']
        correct_indices = set(data.index[data['correct'] == 1].tolist())

        for model_name in transformers:
            for variant, label in [
                (('texts_original', 'query_original'), model_name),
                (('texts_cleaned', 'query_cleaned'), f"cleaned: {model_name}"),
                (('texts_cleaned_stop', 'query_cleaned_stop'), f"cleaned+stopwords: {model_name}")
            ]:
                print(f"\nEvaluating model: {label}")
                model = SentenceTransformer(model_name)

                proc_texts = file_inputs[variant[0]]
                proc_query = file_inputs[variant[1]]

                text_embeddings = model.encode(proc_texts, convert_to_numpy=True, show_progress_bar=False)
                query_embedding = model.encode([proc_query], convert_to_numpy=True)

                index = faiss.IndexFlatIP(text_embeddings.shape[1])
                index.add(text_embeddings)
                distances, indices = index.search(query_embedding, len(proc_texts))
                ranked_indices = indices[0]

                mrr = mean_reciprocal_rank(ranked_indices, correct_indices)
                map_score = mean_average_precision(ranked_indices, correct_indices)
                print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
                print(f"Mean Average Precision (MAP): {map_score:.4f}")

                if label not in model_ranking:
                    model_ranking[label] = []
                model_ranking[label].append({'file': files[i], 'MRR': mrr, 'MAP': map_score})

                del model
                torch.cuda.empty_cache()
                gc.collect()

    # Ranking all the models and printing them in order
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


    # Export the results to a CSV file
    csv_headers = ['model']
    for f in files:
        csv_headers.extend([f"{f}|MRR", f"{f}|MAP"])
    csv_headers.extend(['AverageMRR', 'AverageMAP'])

    csv_rows = []
    for model_name, avg_mrr, avg_map, results in avg_scores:
        row = [model_name]
        file_scores = {r['file']: r for r in results}
        for f in files:
            mrr = file_scores.get(f, {}).get('MRR', '')
            map_score = file_scores.get(f, {}).get('MAP', '')
            row.extend([f"{mrr:.4f}" if mrr != '' else '', f"{map_score:.4f}" if map_score != '' else ''])
        row.extend([f"{avg_mrr:.4f}", f"{avg_map:.4f}"])
        csv_rows.append(row)

    output_df = pd.DataFrame(csv_rows, columns=csv_headers)
    output_df.to_csv("model_ranking_results.csv", index=False)
    print("\nResults exported to model_ranking_results.csv")
