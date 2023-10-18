import sqlite3
from transformers import AutoTokenizer, AutoModel
from torch.nn import functional as F
import torch
import json
import psycopg2

tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-small")
model = AutoModel.from_pretrained("thenlper/gte-small")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def classify_titles_from_db(db_path, classes, threshold=0.8, increment_func=None):
    conn = psycopg2.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'rss_entries_%';")
    tables = [table[0] for table in cursor.fetchall()]
    class_embeddings = [model(tokenizer.encode(text, return_tensors='pt').to(device))[0].mean(1).squeeze().detach().cpu() for text in classes]

    # classified_count = 0  # Counter to track the number of classified entries

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [column[1] for column in cursor.fetchall()]
        if 'Class' not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN Class TEXT;")
        if 'Similarity' not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN Similarity REAL;")
        if 'Embedding' not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN Embedding TEXT;")  # Column to store serialized embedding
        cursor.execute(f"SELECT rowid, Title FROM {table} WHERE Class IS NULL OR Class = '';")
        titles = cursor.fetchall()
        
        for rowid, title in titles:
            classification, similarity, title_embedding_tensor = get_most_similar_class(title, class_embeddings, classes, threshold)
            serialized_embedding = json.dumps(title_embedding_tensor.detach().cpu().numpy().tolist())  # Convert tensor to numpy array and then to list, followed by serialization
            cursor.execute(f"UPDATE {table} SET Class = ?, Similarity = ?, Embedding = ? WHERE rowid = ?", (classification, similarity, serialized_embedding, rowid))
            
            if increment_func:
                increment_func()
        
        conn.commit()
    conn.close()

    # return classified_count  # Return the total number of classified entries

def get_most_similar_class(title, class_embeddings, classes, threshold):
    if not title or not isinstance(title, str):
        return "None", 0, torch.tensor([])
    title_embedding_tensor = model(tokenizer.encode(title, return_tensors='pt').to(device))[0].mean(1).squeeze()
    similarities = [F.cosine_similarity(title_embedding_tensor, class_emb, dim=0).item() for class_emb in class_embeddings]
    max_similarity = max(similarities)
    classification = "None" if max_similarity < threshold else classes[similarities.index(max_similarity)]
    return classification, round(max_similarity, 2), title_embedding_tensor