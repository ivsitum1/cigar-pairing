# Primjeri Koda za Poboljšanje Checker-a

## 1. Poboljšana Plagiarism Detekcija s TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_tfidf_similarity(text: str, reference_texts: List[str]) -> Dict:
    """
    TF-IDF based similarity check - bolje od SequenceMatcher za veće dokumente.
    """
    if not reference_texts:
        return {
            "status": "skipped",
            "message": "No reference texts provided",
            "tool": "tfidf_similarity"
        }
    
    try:
        # Koristimo 1-3 grams za bolje hvatanje parafraziranja
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            stop_words='english'  # Može se prilagoditi
        )
        
        # Vektoriziraj sve tekstove zajedno
        all_texts = [text] + reference_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Usporedi prvi tekst sa svim ostalim
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        max_similarity = float(np.max(similarities))
        matches = [(i, float(sim)) for i, sim in enumerate(similarities) if sim > 0.3]
        
        return {
            "status": "success",
            "similarity_score": max_similarity,
            "matches": len(matches),
            "match_details": matches[:10],  # Top 10
            "message": f"Found {len(matches)} similar sections",
            "tool": "tfidf_similarity"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in TF-IDF check: {str(e)}",
            "tool": "tfidf_similarity"
        }
```

## 2. Semantička Sličnost s Sentence Transformers

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Inicijaliziraj model jednom (može se cache-ati)
_embedding_model = None

def get_embedding_model():
    """Lazy loading modela - učita se samo jednom."""
    global _embedding_model
    if _embedding_model is None:
        # Koristimo mali brzi model - može se zamijeniti većim za bolju točnost
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

def check_semantic_similarity(text: str, reference_texts: List[str], 
                              chunk_size: int = 512) -> Dict:
    """
    Semantička sličnost - detektira slično značenje iako je tekst drugačije formuliran.
    """
    if not reference_texts:
        return {
            "status": "skipped",
            "message": "No reference texts provided",
            "tool": "semantic_similarity"
        }
    
    try:
        model = get_embedding_model()
        
        # Podijeli tekst u chunkove ako je previše dug
        def chunk_text(txt, size=chunk_size):
            words = txt.split()
            chunks = []
            for i in range(0, len(words), size):
                chunks.append(' '.join(words[i:i+size]))
            return chunks
        
        text_chunks = chunk_text(text)
        all_ref_chunks = []
        chunk_to_ref = []  # Mapiranje chunk -> reference index
        
        for ref_idx, ref_text in enumerate(reference_texts):
            chunks = chunk_text(ref_text)
            all_ref_chunks.extend(chunks)
            chunk_to_ref.extend([ref_idx] * len(chunks))
        
        # Generiraj embeddings
        text_embeddings = model.encode(text_chunks, show_progress_bar=False)
        ref_embeddings = model.encode(all_ref_chunks, show_progress_bar=False)
        
        # Pronađi najveću sličnost između bilo koja dva chunka
        max_similarity = 0.0
        matches = []
        
        for text_emb in text_embeddings:
            similarities = cosine_similarity([text_emb], ref_embeddings).flatten()
            max_idx = np.argmax(similarities)
            max_sim = float(similarities[max_idx])
            
            if max_sim > max_similarity:
                max_similarity = max_sim
            
            if max_sim > 0.7:  # Prag za semantičku sličnost
                matches.append({
                    "reference_index": chunk_to_ref[max_idx],
                    "similarity": max_sim
                })
        
        return {
            "status": "success",
            "similarity_score": max_similarity,
            "matches": len(matches),
            "match_details": matches[:10],
            "message": f"Found {len(matches)} semantically similar sections",
            "tool": "semantic_similarity"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in semantic similarity check: {str(e)}",
            "tool": "semantic_similarity"
        }
```

## 3. Kombinirana Sličnost (TF-IDF + Semantic)

```python
def check_combined_similarity(text: str, reference_texts: List[str],
                              tfidf_weight: float = 0.6,
                              semantic_weight: float = 0.4) -> Dict:
    """
    Kombinira TF-IDF i semantičku sličnost za najbolje rezultate.
    """
    tfidf_result = check_tfidf_similarity(text, reference_texts)
    semantic_result = check_semantic_similarity(text, reference_texts)
    
    if tfidf_result["status"] != "success" or semantic_result["status"] != "success":
        # Fallback na onaj koji radi
        return tfidf_result if tfidf_result["status"] == "success" else semantic_result
    
    # Kombiniraj rezultate
    combined_score = (
        tfidf_result["similarity_score"] * tfidf_weight +
        semantic_result["similarity_score"] * semantic_weight
    )
    
    # Kombiniraj matches
    all_matches = []
    if "match_details" in tfidf_result:
        all_matches.extend([(m, "tfidf") for m in tfidf_result["match_details"]])
    if "match_details" in semantic_result:
        all_matches.extend([(m, "semantic") for m in semantic_result["match_details"]])
    
    return {
        "status": "success",
        "similarity_score": combined_score,
        "tfidf_score": tfidf_result["similarity_score"],
        "semantic_score": semantic_result["similarity_score"],
        "matches": len(all_matches),
        "message": f"Combined analysis: TF-IDF {tfidf_result['similarity_score']:.2%}, "
                  f"Semantic {semantic_result['similarity_score']:.2%}",
        "tool": "combined_similarity"
    }
```

## 4. AI Detekcija s Transformers Modelom

```python
from transformers import pipeline
import torch

_ai_detector = None

def get_ai_detector():
    """Lazy loading AI detector modela."""
    global _ai_detector
    if _ai_detector is None:
        try:
            # Koristimo roberta-base-openai-detector model
            _ai_detector = pipeline(
                "text-classification",
                model="roberta-base-openai-detector",
                device=0 if torch.cuda.is_available() else -1  # GPU ako je dostupan
            )
        except Exception as e:
            print(f"Warning: Could not load AI detector model: {e}")
            return None
    return _ai_detector

def check_ai_with_transformers(text: str, chunk_size: int = 512) -> Dict:
    """
    AI detekcija koristeći transformers model.
    """
    detector = get_ai_detector()
    
    if detector is None:
        return {
            "status": "error",
            "message": "AI detector model not available",
            "tool": "transformers_ai_detector"
        }
    
    try:
        # Model radi bolje sa kraćim tekstovima, podijelimo ako je potrebno
        words = text.split()
        if len(words) > chunk_size:
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunks.append(' '.join(words[i:i+chunk_size]))
        else:
            chunks = [text]
        
        # Provjeri svaki chunk
        ai_scores = []
        for chunk in chunks:
            try:
                result = detector(chunk, truncation=True, max_length=512)
                # Model vraća label i score
                # Pretpostavljamo format: {"label": "AI"/"Human", "score": 0.0-1.0}
                if isinstance(result, list):
                    result = result[0]
                
                # Konvertiraj u AI probability
                if result["label"].upper() in ["AI", "FAKE", "GENERATED"]:
                    ai_score = result["score"]
                else:
                    ai_score = 1.0 - result["score"]
                
                ai_scores.append(ai_score)
            except Exception as e:
                print(f"Error processing chunk: {e}")
                continue
        
        if not ai_scores:
            return {
                "status": "error",
                "message": "Could not process any chunks",
                "tool": "transformers_ai_detector"
            }
        
        avg_score = sum(ai_scores) / len(ai_scores)
        max_score = max(ai_scores)
        
        return {
            "status": "success",
            "score": avg_score,
            "max_score": max_score,
            "chunks_analyzed": len(chunks),
            "message": f"Average AI probability: {avg_score:.2%}",
            "tool": "transformers_ai_detector"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in transformers AI detection: {str(e)}",
            "tool": "transformers_ai_detector"
        }
```

## 5. Napredna Stilometrija za AI Detekciju

```python
import textstat

def analyze_text_statistics(text: str) -> Dict:
    """
    Analizira stilističke obilježja teksta za AI detekciju.
    """
    try:
        stats = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "smog_index": textstat.smog_index(text),
            "lexicon_count": textstat.lexicon_count(text),
            "avg_sentence_length": textstat.avg_sentence_length(text),
            "avg_syllables_per_word": textstat.avg_syllables_per_word(text),
            "difficult_words": textstat.difficult_words(text),
        }
        
        # Heuristics for AI detection based on statistics
        ai_indicators = 0
        
        # AI texts often have uniform readability
        if 20 < stats["flesch_reading_ease"] < 60:
            ai_indicators += 0.1
        
        # Less variation in sentence length
        sentences = text.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            length_std = np.std(sentence_lengths)
            if length_std < 10:  # Low variation
                ai_indicators += 0.2
        
        # Fewer difficult words
        if stats["lexicon_count"] > 0:
            difficult_ratio = stats["difficult_words"] / stats["lexicon_count"]
            if difficult_ratio < 0.1:
                ai_indicators += 0.1
        
        return {
            "status": "success",
            "statistics": stats,
            "ai_indicators_score": min(ai_indicators, 1.0),
            "tool": "text_statistics"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in text statistics: {str(e)}",
            "tool": "text_statistics"
        }
```

## 6. Kombinirana AI Detekcija

```python
def check_ai_combined(text: str) -> Dict:
    """
    Kombinira više metoda za AI detekciju.
    """
    results = {}
    
    # 1. Transformers model (ako je dostupan)
    transformer_result = check_ai_with_transformers(text)
    if transformer_result["status"] == "success":
        results["transformers"] = transformer_result["score"]
    
    # 2. Stilometrija
    stats_result = analyze_text_statistics(text)
    if stats_result["status"] == "success":
        results["statistics"] = stats_result["ai_indicators_score"]
    
    # 3. Osnovna heuristika (fallback)
    basic_score = calculate_basic_ai_score(text)
    results["basic"] = basic_score
    
    # Kombiniraj rezultate (ponderirano)
    weights = {
        "transformers": 0.6,
        "statistics": 0.25,
        "basic": 0.15
    }
    
    combined_score = 0.0
    total_weight = 0.0
    
    for method, score in results.items():
        if method in weights:
            combined_score += score * weights[method]
            total_weight += weights[method]
    
    if total_weight > 0:
        combined_score /= total_weight
    
    return {
        "status": "success",
        "score": combined_score,
        "component_scores": results,
        "message": f"Combined AI probability: {combined_score:.2%}",
        "tool": "combined_ai_detector"
    }
```

## 7. Optimizacija za Velike Dokumente

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_embeddings(text_hash: str, model_name: str):
    """Cache embeddings za česte provjere."""
    # Implementacija cache-a (može koristiti pickle, redis, itd.)
    pass

def check_with_caching(text: str, reference_texts: List[str]) -> Dict:
    """
    Optimizirana provjera s caching-om za velike dokumente.
    """
    import hashlib
    
    # Generiraj hash za caching
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Provjeri cache (implementacija ovisno o storage backend-u)
    # ...
    
    # Inače, normalna provjera
    return check_combined_similarity(text, reference_texts)
```

## Instalacija Dependencies

```bash
# Osnovne biblioteke za poboljšanja
pip install scikit-learn sentence-transformers textdistance textstat

# Za AI detekciju (veliki paketi - opcionalno)
pip install transformers torch

# Alternativno, samo CPU verzija (manja):
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu
```

## Integracija u Postojeći Kod

### Korak 1: Dodati nove funkcije u `check_ai_plagiarism.py`

### Korak 2: Ažurirati `check_ai_plagiarism()` funkciju:

```python
# U main funkciji:
if "tfidf_similarity" in tools:
    print("  - TF-IDF similarity check...")
    results["plagiarism_detection"]["tfidf_similarity"] = check_tfidf_similarity(
        text, reference_texts if reference_texts else None
    )

if "semantic_similarity" in tools:
    print("  - Semantic similarity check...")
    results["plagiarism_detection"]["semantic_similarity"] = check_semantic_similarity(
        text, reference_texts if reference_texts else None
    )

if "combined_similarity" in tools:
    print("  - Combined similarity check...")
    results["plagiarism_detection"]["combined_similarity"] = check_combined_similarity(
        text, reference_texts if reference_texts else None
    )
```

### Korak 3: Dodati nove toolove u default listu:

```python
if not tools:
    tools = [
        "basic_ai",           # Osnovna AI detekcija
        "transformers_ai",    # ML AI detekcija (ako je dostupna)
        "tfidf_similarity",   # TF-IDF plagiarism
        "semantic_similarity" # Semantic plagiarism
    ]
```

---

**Version:** 1.0  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
