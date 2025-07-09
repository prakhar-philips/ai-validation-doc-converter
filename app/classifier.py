import os
import torch
import faiss
import numpy as np
import pickle
from transformers import BertTokenizer, BertModel
from app.pdf_reader import extract_text_from_pdf

# Paths for index and labels
INDEX_PATH = "app/faiss.index"
LABELS_PATH = "app/faiss_labels.pkl"

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

def chunk_text(text, max_len=250):
    """Split document into manageable chunks"""
    sentences = text.split('. ')
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_len:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return [c for c in chunks if len(c.strip()) > 50]

@torch.no_grad()
def get_embedding(text):
    """Convert a chunk into BERT [CLS] token embedding"""
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    except Exception as e:
        print(f"[Embedding Error] {e} in chunk:\n{text[:100]}...\n")
        return np.zeros(model.config.hidden_size)

def build_and_save_faiss_index(reference_folder):
    """Index reference documents into FAISS for classification"""
    all_embeddings, all_labels = [], []

    print("\n📚 Reference Files and Labels:")
    for filename in os.listdir(reference_folder):
        if filename.endswith(".pdf"):
            label = filename.split("_")[0].upper()  # e.g., URS_1.pdf → URS
            print(f"  ➤ {filename} => Label: {label}")
            text = extract_text_from_pdf(os.path.join(reference_folder, filename))
            chunks = chunk_text(text)
            for chunk in chunks:
                emb = get_embedding(chunk)
                all_embeddings.append(emb)
                all_labels.append(label)

    array = np.vstack(all_embeddings)
    index = faiss.IndexFlatL2(array.shape[1])
    index.add(array)

    faiss.write_index(index, INDEX_PATH)
    with open(LABELS_PATH, "wb") as f:
        pickle.dump(all_labels, f)

    print(f"\n✅ Saved FAISS index to {INDEX_PATH} and labels to {LABELS_PATH}")

def load_index_and_labels():
    """Load FAISS index and label list"""
    index = faiss.read_index(INDEX_PATH)
    with open(LABELS_PATH, "rb") as f:
        labels = pickle.load(f)
    return index, labels

def classify_text(text, index, labels, k=3):
    """Classify document by comparing chunks to reference embeddings"""
    chunks = chunk_text(text)
    print(f"\n📄 Document split into {len(chunks)} chunks.")

    scores = {}
    total_chunks = len(chunks)

    for chunk in chunks:
        emb = get_embedding(chunk)
        D, I = index.search(np.array([emb]), k)
        for i in I[0]:
            label = labels[i]
            scores[label] = scores.get(label, 0) + 1 / total_chunks

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    print("\n🔍 Top Predictions:")
    for label, score in sorted_scores[:3]:
        print(f"  - {label}: {round(score * 100, 2)}% vote share")

    return sorted_scores[0][0] if sorted_scores else "Unknown"
