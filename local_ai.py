"""Local AI inference engine using Hugging Face Transformers.

Provides:
- Chat responses (retention advice, churn insights)
- Retention recommendations (structured JSON)
- Multi-lingual support via translation pipeline
"""
import json
import logging
import os

logger = logging.getLogger("local_ai")

# Try to load transformers; if unavailable, run in fallback mode
try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        pipeline,
        set_seed,
    )
    _HF_AVAILABLE = True
except ImportError:
    _HF_AVAILABLE = False
    logger.warning("transformers/torch not installed — local AI will use rule-based fallback")

set_seed(42)

# ── Supported languages ──────────────────────────────────────
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

DEFAULT_LANG = "en"

# ── Translation maps for fallback / rule-based responses ─────

_CHAT_FALLBACKS = {
    "en": (
        "I'm RetainAI, your churn analytics assistant. "
        "The dataset shows key churn signals: age, balance, inactivity, and product count. "
        "Focus retention efforts on high-risk segments (age 50+, inactive members, Germany region). "
        "Would you like a specific KPI breakdown or retention strategy?"
    ),
    "hi": (
        "मैं RetainAI हूँ, आपका ग्राहक विश्लेषण सहायक। "
        "डेटासेट में मुख्य चर्न संकेत: आयु, शेष राशि, निष्क्रियता और उत्पाद गणना। "
        "उच्च जोखिम वाले वर्गों (50+ आयु, निष्क्रिय सदस्य, जर्मनी क्षेत्र) पर ध्यान केंद्रित करें। "
        "क्या आप कोई विशिष्ट KPI विश्लेषण या रिटेंशन रणनीति चाहते हैं?"
    ),
    "es": (
        "Soy RetainAI, tu asistente de análisis de churn. "
        "El conjunto de datos muestra señales clave de abandono: edad, saldo, inactividad y número de productos. "
        "Enfoca los esfuerzos de retención en segmentos de alto riesgo (mayores de 50 años, miembros inactivos, región de Alemania). "
        "¿Te gustaría un desglose específico de KPI o una estrategia de retención?"
    ),
    "fr": (
        "Je suis RetainAI, votre assistant d'analyse du churn. "
        "Le jeu de données montre les signaux clés de désabonnement : âge, solde, inactivité et nombre de produits. "
        "Concentrez vos efforts de rétention sur les segments à haut risque (50 ans et plus, membres inactifs, région Allemagne). "
        "Souhaitez-vous une analyse KPI spécifique ou une stratégie de rétention?"
    ),
    "de": (
        "Ich bin RetainAI, Ihr Churn-Analyse-Assistent. "
        "Der Datensatz zeigt wichtige Abwanderungssignale: Alter, Guthaben, Inaktivität und Produktanzahl. "
        "Konzentrieren Sie die Bindungsbemühungen auf Hochrisikosegmente (50+ Jahre, inaktive Mitglieder, Region Deutschland). "
        "Möchten Sie eine spezifische KPI-Aufschlüsselung oder eine Bindungsstrategie?"
    ),
}

_REC_FALLBACKS = {
    "en": {
        "offers": [
            "Special low-interest personal loan offer",
            "Waive monthly account maintenance charges",
            "Boost rewards & cashback on debit transactions",
            "Personalized banking advisor allocation",
            "Premium membership upgrade trial (3 months)",
        ],
        "explanation": "Customer shows {risk}-risk churn signals from the model. Engage proactively.",
        "priority_actions": [
            "Outreach call within 48 hours",
            "Send a tailored retention offer email",
            "Schedule a financial review meeting",
        ],
    },
    "hi": {
        "offers": [
            "विशेष कम-ब्याज व्यक्तिगत ऋण प्रस्ताव",
            "मासिक खाता रखरखाव शुल्क माफ करें",
            "डेबिट लेनदेन पर रिवॉर्ड और कैशबैक बढ़ाएं",
            "व्यक्तिगत बैंकिंग सलाहकार आवंटन",
            "प्रीमियम सदस्यता उन्नयन परीक्षण (3 महीने)",
        ],
        "explanation": "ग्राहक मॉडल से {risk}-जोखिम चर्न संकेत दिखाता है। सक्रिय रूप से संलग्न करें।",
        "priority_actions": [
            "48 घंटे के भीतर आउटरीच कॉल",
            "अनुकूलित रिटेंशन ऑफ़र ईमेल भेजें",
            "वित्तीय समीक्षा बैठक निर्धारित करें",
        ],
    },
    "es": {
        "offers": [
            "Oferta especial de préstamo personal a bajo interés",
            "Exención de cargos mensuales de mantenimiento de cuenta",
            "Aumento de recompensas y devolución de efectivo en transacciones de débito",
            "Asignación de asesor bancario personalizado",
            "Prueba de actualización de membresía premium (3 meses)",
        ],
        "explanation": "El cliente muestra señales de abandono de riesgo {risk} del modelo. Involucre proactivamente.",
        "priority_actions": [
            "Llamada de divulgación dentro de 48 horas",
            "Enviar un correo electrónico de oferta de retención personalizada",
            "Programar una reunión de revisión financiera",
        ],
    },
    "fr": {
        "offers": [
            "Offre spéciale de prêt personnel à faible intérêt",
            "Suppression des frais de tenue de compte mensuels",
            "Augmentation des récompenses et du cashback sur les transactions par débit",
            "Attribution d'un conseiller bancaire personnalisé",
            "Essai de mise à niveau d'adhésion Premium (3 mois)",
        ],
        "explanation": "Le client montre des signaux de churn à risque {risk} du modèle. Engagez-vous de manière proactive.",
        "priority_actions": [
            "Appel de sensibilisation dans les 48 heures",
            "Envoyer un e-mail d'offre de rétention personnalisée",
            "Planifier une réunion d'examen financier",
        ],
    },
    "de": {
        "offers": [
            "Spezielles Niedrigzins-Darlehensangebot",
            "Erlass monatlicher Kontoführungsgebühren",
            "Erhöhung von Prämien und Cashback bei Debit-Transaktionen",
            "Zuteilung eines persönlichen Bankberaters",
            "Premium-Mitgliedschafts-Upgrade-Test (3 Monate)",
        ],
        "explanation": "Der Kunde zeigt {risk}-Risiko-Abwanderungssignale aus dem Modell. Proaktiv einbinden.",
        "priority_actions": [
            "Kontaktaufnahme innerhalb von 48 Stunden",
            "Maßgeschneiderte Bindungsangebot-E-Mail senden",
            "Finanzprüfungsbesprechung planen",
        ],
    },
}


def detect_language(headers: dict | None = None) -> str:
    """Detect user language from request headers, defaulting to English."""
    if headers is None:
        return DEFAULT_LANG
    accept_lang = headers.get("accept-language", headers.get("Accept-Language", "en"))
    if not accept_lang:
        return DEFAULT_LANG
    # Parse first locale from Accept-Language header
    primary = accept_lang.split(",")[0].strip().split(";")[0].split("-")[0].lower()
    return primary if primary in LANGUAGES else DEFAULT_LANG


def get_language_name(lang: str) -> str:
    return LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANG])


# ── Model loading (lazy, single-instance) ──────────────────
_model = None
_tokenizer = None


def _load_model():
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer
    if not _HF_AVAILABLE:
        return None, None
    model_name = os.environ.get("LOCAL_AI_MODEL", "microsoft/DialoGPT-small")
    try:
        logger.info("Loading local AI model: %s", model_name)
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True,
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        logger.info("Local AI model loaded successfully")
    except Exception as exc:
        logger.exception("Failed to load local AI model: %s", exc)
        _model = None
        _tokenizer = None
    return _model, _tokenizer


def _generate_text(prompt: str, max_new_tokens: int = 200) -> str:
    """Generate text using the local model."""
    model, tokenizer = _load_model()
    if model is None:
        return ""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Return only the new part (after the prompt)
    response = generated[len(prompt):].strip().split("\n")[0].strip()
    return response if response else "I'm not sure how to answer that. Can you rephrase?"


def _translate(text: str, target_lang: str, source_lang: str = "en") -> str:
    """Translate text using translation pipeline if available."""
    if target_lang == source_lang:
        return text
    if not _HF_AVAILABLE:
        return text
    try:
        translator = pipeline(
            "translation",
            model=f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}",
            device=-1,  # CPU
        )
        result = translator(text, max_length=512)
        return result[0]["translation_text"]
    except Exception:
        # Translation model not available for this pair - return original
        logger.debug("Translation %s->%s not available", source_lang, target_lang)
        return text


# ── Public API for chat ─────────────────────────────────────
async def chat_response(user_message: str, kpis: dict, lang: str = "en") -> str:
    """Generate a chat response in the requested language."""
    if not _HF_AVAILABLE:
        return _CHAT_FALLBACKS.get(lang, _CHAT_FALLBACKS["en"])

    # Build a context-aware prompt
    kpi_summary = (
        f"Total customers: {kpis.get('total_customers', 'N/A')}, "
        f"Churn rate: {kpis.get('churn_rate', 'N/A')}%, "
        f"Retention rate: {kpis.get('retention_rate', 'N/A')}%"
    )
    prompt = (
        f"You are a helpful banking retention assistant. "
        f"Current KPIs: {kpi_summary}. "
        f"User asked in {LANGUAGES.get(lang, 'English')}: {user_message}\n"
        f"Answer concisely (2-4 sentences) about churn or retention strategies:"
    )
    response = _generate_text(prompt, max_new_tokens=150)

    # If model returns empty or irrelevant, use fallback in the target language
    if not response or len(response) < 10:
        response = _CHAT_FALLBACKS.get(lang, _CHAT_FALLBACKS["en"])

    return response


async def recommendations_response(
    profile: dict, prediction: dict, lang: str = "en"
) -> dict:
    """Generate retention recommendations in the requested language."""
    risk = prediction.get("risk_level", "Medium")

    if not _HF_AVAILABLE:
        fallback = _REC_FALLBACKS.get(lang, _REC_FALLBACKS["en"])
        result = dict(fallback)
        result["explanation"] = fallback["explanation"].format(risk=risk)
        return result

    prompt = (
        f"Given a customer with profile: {profile} "
        f"and churn prediction: {prediction}, "
        f"provide a retention plan as JSON with keys: offers (list of 5), "
        f"explanation (2-3 sentences), priority_actions (list of 3). "
        f"Language: {LANGUAGES.get(lang, 'English')}."
    )
    response = _generate_text(prompt, max_new_tokens=300)

    # Try to parse JSON from response
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "offers" in data:
            return data
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback
    fallback = _REC_FALLBACKS.get(lang, _REC_FALLBACKS["en"])
    result = dict(fallback)
    result["explanation"] = fallback["explanation"].format(risk=risk)
    return result
