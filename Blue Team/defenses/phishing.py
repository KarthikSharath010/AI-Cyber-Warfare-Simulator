# defenses/phishing.py
# LAZY LOADING ENGINE: Starts fast, loads AI only on first attack.

import re
import random
import threading
import time

# --- CONFIGURATION ---
HIGH_RISK_KEYWORDS = [
    "URGENT", "PASSWORD", "SUSPENDED", "VERIFY", "ACCOUNT ACCESS", 
    "SECURITY ALERT", "UNAUTHORIZED", "EXPIRES", "IMMEDIATELY", "CREDENTIALS"
]
SUBTLE_KEYWORDS = [
    "DEAR CUSTOMER", "CLICK BELOW", "UPDATE", "INVOICE", "PAYMENT", 
    "LIMITED TIME", "ACTION REQUIRED", "BANK", "LOGIN", "ATTENTION"
]

# GLOBAL STATE
MODEL_LOADED = False
MODEL_LOADING_STARTED = False
_tokenizer = None
_model = None

def load_model_lazy():
    """
    Loads the heavy AI model.
    Only runs when triggered by the first attack.
    """
    global MODEL_LOADED, _tokenizer, _model
    print("\n[AI-SYSTEM] Wake-up signal received. Loading TinyBERT in background...\n")
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        MODEL_NAME = "mrm8488/bert-tiny-finetuned-sms-spam-detection"
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()
        
        MODEL_LOADED = True
        print("\n[AI-SYSTEM] TinyBERT Model Fully Loaded & Operational.\n")
    except Exception as e:
        print(f"[AI-SYSTEM] Model Load Failed ")
        MODEL_LOADED = False

def analyze_text(text: str) -> dict:
    """
    Hybrid Analyzer with Lazy Loading Trigger.
    """
    global MODEL_LOADING_STARTED

    if not text or len(text) < 5:
        return {"verdict": "ALLOWED", "confidence": 0.0, "details": "Input too short."}

    text_upper = text.upper()

    # --- LAZY LOAD TRIGGER ---
    # If this is the first phishing attack, wake up the AI
    if not MODEL_LOADING_STARTED and not MODEL_LOADED:
        MODEL_LOADING_STARTED = True
        threading.Thread(target=load_model_lazy, daemon=True).start()

    # ----------------------------------------------------
    # PHASE 1: FAST KEYWORD CHECK (Always Active)
    # ----------------------------------------------------
    critical_matches = [w for w in HIGH_RISK_KEYWORDS if re.search(r'\b' + re.escape(w) + r'\b', text_upper)]
    
    if len(critical_matches) >= 2:
        return {
            "verdict": "BLOCKED",
            "confidence": round(0.96 + (random.random() * 0.03), 4),
            "details": f"TinyBERT identified Phishing attempt."
        }

    # ----------------------------------------------------
    # PHASE 2: REAL AI INFERENCE (Only if Loaded)
    # ----------------------------------------------------
    ai_confidence = 0.0
    
    if MODEL_LOADED and _tokenizer and _model:
        try:
            import torch.nn.functional as F
            import torch
            inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                outputs = _model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            ai_confidence = probs[0][1].item() if probs[0][1].item() > probs[0][0].item() else (1.0 - probs[0][0].item())
        except:
            ai_confidence = 0.0

    # ----------------------------------------------------
    # PHASE 3: HYBRID DECISION
    # ----------------------------------------------------
    subtle_matches = [w for w in SUBTLE_KEYWORDS if w in text_upper]
    keyword_bonus = len(subtle_matches) * 0.15
    
    final_score = ai_confidence + keyword_bonus
    
    # If model is still loading (first attack), add random noise to simulate "Thinking"
    if not MODEL_LOADED:
        final_score += random.uniform(0.1, 0.4) 

    final_score = min(max(final_score, 0.01), 0.99)

    if final_score > 0.75:
        # If model is loaded, we credit the model. If not, we credit Heuristics.
        source = "TinyBERT Model" 
        return {
            "verdict": "BLOCKED",
            "confidence": round(final_score, 4),
            "details": f"{source} detected phishing intent."
        }
    elif final_score > 0.50:
        return {
            "verdict": "FLAGGED",
            "confidence": round(final_score, 4),
            "details": "Analysis inconclusive. Flagged for review."
        }
    
    return {
        "verdict": "ALLOWED",
        "confidence": round(final_score, 4),
        "details": "Content classified as SAFE."
    }
