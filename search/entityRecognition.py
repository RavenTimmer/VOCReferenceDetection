from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch


def clean_ner_output(ner_output):
    entities = []
    current_entity = None

    for token in ner_output:
        label = token['entity']
        word = token['word']
        score = token['score']

        if label.startswith('B-'):
            if current_entity:
                entities.append(current_entity)
            current_entity = {
                'entity': label[2:],
                'text': word.replace('▁', ' ').strip(),
                'score': score
            }
        elif label.startswith('I-') and current_entity:

            current_entity['text'] += word.strip().replace('▁', ' ')
            current_entity['score'] = (
                current_entity['score'] + score) / 2  # average
        else:
            # Handle case where the token isn't part of any entity
            if current_entity:
                entities.append(current_entity)
                current_entity = None

    if current_entity:
        entities.append(current_entity)

    return entities


def entity_recognition(text):
    device = 0 if torch.cuda.is_available() else -1

    tokenizer = AutoTokenizer.from_pretrained("CLTL/gm-ner-xlmrbase")
    model = AutoModelForTokenClassification.from_pretrained(
        "CLTL/gm-ner-xlmrbase").to(device)

    nlp = pipeline("ner", model=model, tokenizer=tokenizer, device=device)
    return clean_ner_output(nlp(text))
