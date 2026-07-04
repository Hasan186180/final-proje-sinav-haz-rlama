"""
ai_service.py — Gemini & Groq API entegrasyonu
JSON şemalı prompt ile sınav içeriği üretir.
"""

import json
import os
import re
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
#  Prompt şablonu                                                               #
# --------------------------------------------------------------------------- #

PROMPT_TEMPLATE = """
Sen bir eğitim uzmanı ve sınav hazırlama asistanısın.
Konu: '{konu}'
Zorluk Seviyesi: '{zorluk}'
Dil: Türkçe

Aşağıdaki JSON şemasına TAM UYGUN bir sınav içeriği üret.
Test sorusu sayısı: {soru_sayisi} adet (tam olarak bu kadar olmalı).
Klasik soru sayısı: 5 adet (sabit).

JSON ŞEMASI (başka hiçbir şey yazma, sadece JSON döndür):
{{
  "ozet": "Konunun 3-5 cümlelik açık ve anlaşılır özeti",
  "test_sorulari": [
    {{
      "soru": "Soru metni buraya",
      "secenekler": {{
        "A": "Birinci seçenek",
        "B": "İkinci seçenek",
        "C": "Üçüncü seçenek",
        "D": "Dördüncü seçenek"
      }},
      "dogru": "A"
    }}
  ],
  "klasik_sorular": [
    "Açık uçlu soru 1",
    "Açık uçlu soru 2",
    "Açık uçlu soru 3",
    "Açık uçlu soru 4",
    "Açık uçlu soru 5"
  ],
  "calisma_onerisi": "Konuyu etkili öğrenmek için pratik ve uygulanabilir çalışma tavsiyesi"
}}

Zorluk seviyesine göre soru zorluğunu ayarla:
- Kolay: Temel kavramlar, tanımlar, basit uygulamalar
- Orta: Orta düzey kavramlar, karşılaştırmalar, analizler
- Zor: İleri düzey kavramlar, problem çözme, sentez

ÖNEMLİ: Sadece geçerli JSON döndür, markdown kod bloğu veya açıklama ekleme.
""".strip()

# --------------------------------------------------------------------------- #
#  Gemini servisi                                                               #
# --------------------------------------------------------------------------- #

def _get_gemini_model(model_name: str = "gemini-2.0-flash"):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
            top_p=0.9,
        ),
    )


def generate_with_gemini(
    konu: str,
    soru_sayisi: int,
    zorluk: str,
    model_name: str = "gemini-2.0-flash",
) -> dict:
    """Gemini API ile sınav içeriği üretir."""
    model = _get_gemini_model(model_name)
    prompt = PROMPT_TEMPLATE.format(
        konu=konu, zorluk=zorluk, soru_sayisi=soru_sayisi
    )
    response = model.generate_content(prompt)
    return _parse_response(response.text)


# --------------------------------------------------------------------------- #
#  Groq servisi (bonus)                                                         #
# --------------------------------------------------------------------------- #

def generate_with_groq(
    konu: str,
    soru_sayisi: int,
    zorluk: str,
    model_name: str = "llama-3.3-70b-versatile",
) -> dict:
    """Groq API ile sınav içeriği üretir."""
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("groq paketi yüklü değil: pip install groq")

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin.")

    client = Groq(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(
        konu=konu, zorluk=zorluk, soru_sayisi=soru_sayisi
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Sen bir eğitim uzmanısın. Her zaman geçerli JSON formatında yanıt ver.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    return _parse_response(response.choices[0].message.content)


# --------------------------------------------------------------------------- #
#  Yardımcı fonksiyonlar                                                        #
# --------------------------------------------------------------------------- #

def _parse_response(raw_text: str) -> dict:
    """API yanıtını JSON'a çevirir, hatalı formatları düzeltmeye çalışır."""
    text = raw_text.strip()

    # Markdown kod bloğunu temizle
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Son çare: regex ile JSON nesnesini bul
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(
                f"API'den geçerli JSON alınamadı:\n{text[:500]}"
            )

    _validate_schema(data)
    return data


def _validate_schema(data: dict) -> None:
    """Temel şema kontrolü yapar; eksik alan varsa hata fırlatır."""
    required_keys = {"ozet", "test_sorulari", "klasik_sorular", "calisma_onerisi"}
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"API yanıtında eksik alanlar: {missing}")

    if not isinstance(data["test_sorulari"], list) or len(data["test_sorulari"]) == 0:
        raise ValueError("test_sorulari boş veya liste değil.")

    if not isinstance(data["klasik_sorular"], list) or len(data["klasik_sorular"]) == 0:
        raise ValueError("klasik_sorular boş veya liste değil.")


def generate_exam(
    konu: str,
    soru_sayisi: int,
    zorluk: str,
    ai_provider: str = "Gemini",
    model_name: Optional[str] = None,
) -> dict:
    """
    Ortak giriş noktası. ai_provider'a göre ilgili servisi çağırır.

    Args:
        konu: Sınav konusu
        soru_sayisi: Test sorusu sayısı
        zorluk: Kolay / Orta / Zor
        ai_provider: "Gemini" veya "Groq"
        model_name: Kullanılacak model adı (None ise varsayılan)

    Returns:
        Sınav içeriği dict'i
    """
    if ai_provider == "Groq":
        _model = model_name or "llama-3.3-70b-versatile"
        return generate_with_groq(konu, soru_sayisi, zorluk, _model)
    else:
        _model = model_name or "gemini-2.0-flash"
        return generate_with_gemini(konu, soru_sayisi, zorluk, _model)


# --------------------------------------------------------------------------- #
#  İnteraktif Sınav Modu Fonksiyonları                                        #
# --------------------------------------------------------------------------- #

PROMPT_SINGLE_QUESTION = """
Sen bir eğitim uzmanı ve sınav hazırlama asistanısın.
Konu: '{konu}'
Zorluk Seviyesi: '{zorluk}'
Dil: Türkçe

Kullanıcının seviyesine uygun, yukarıdaki konudan ve zorluk seviyesinden TAM OLARAK 1 ADET çoktan seçmeli soru üret.
Zorluk seviyesine göre soru kalitesini ve derinliğini ayarla:
- Kolay: Temel kavramlar, basit tanımlar, doğrudan bilgi.
- Orta: Karşılaştırmalar, analiz gerektiren durumlar, mantık yürütme.
- Zor: İleri düzey mantık yürütme, sentez, problem çözme ve derin kavrayış gerektiren sorular.

Aşağıdaki JSON şemasına tamamen uygun bir yanıt ver (başka hiçbir şey yazma, sadece JSON):
{{
  "soru": "Soru metni buraya",
  "secenekler": {{
    "A": "Birinci seçenek",
    "B": "İkinci seçenek",
    "C": "Üçüncü seçenek",
    "D": "Dördüncü seçenek"
  }},
  "dogru": "A"
}}
""".strip()

PROMPT_QUIZ_RECOMMENDATION = """
Bir öğrenci '{konu}' konulu interaktif bir sınava girdi.
Sınav Sonucu:
- Toplam Soru: {toplam_soru}
- Doğru Sayısı: {dogru_sayisi}
- Yanlış Sayısı: {yanlis_sayisi}

Öğrencinin cevapladığı sorular ve verdiği yanıtlar:
{soru_cevap_ozeti}

Öğrencinin bu konudaki performansını detaylıca analiz et.
Ona özel, motivasyonunu artırıcı, eksik olduğu konuları kapatmasını sağlayacak pratik ve samimi bir çalışma tavsiyesi ve öğrenme planı raporu üret.
""".strip()


def _parse_single_question(raw_text: str) -> dict:
    """Tek bir soru içeren JSON yanıtını ayrıştırır ve doğrular."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"Geçersiz JSON yanıtı: {text[:300]}")

    for key in ["soru", "secenekler", "dogru"]:
        if key not in data:
            raise ValueError(f"Soru JSON şemasında eksik alan: '{key}'")
    
    if not isinstance(data["secenekler"], dict) or len(data["secenekler"]) != 4:
        raise ValueError("Seçenekler 4 adet (A, B, C, D) olmalıdır.")
        
    return data


def generate_single_question(
    konu: str,
    zorluk: str,
    ai_provider: str = "Gemini",
    model_name: Optional[str] = None,
) -> dict:
    """İnteraktif mod için zorluk seviyesine göre tek bir soru üretir."""
    prompt = PROMPT_SINGLE_QUESTION.format(konu=konu, zorluk=zorluk)
    
    if ai_provider == "Groq":
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq paketi yüklü değil.")
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        _model = model_name or "llama-3.3-70b-versatile"
        
        response = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": "Sadece geçerli JSON formatında yanıt veren bir eğitim asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return _parse_single_question(response.choices[0].message.content)
        
    else:
        # Gemini
        _model = model_name or "gemini-2.0-flash"
        model = _get_gemini_model(_model)
        response = model.generate_content(prompt)
        return _parse_single_question(response.text)


def generate_quiz_recommendation(
    konu: str,
    toplam_soru: int,
    dogru_sayisi: int,
    yanlis_sayisi: int,
    soru_cevap_ozeti: str,
    ai_provider: str = "Gemini",
    model_name: Optional[str] = None,
) -> str:
    """Tüm sınav bittiğinde öğrenci performansına göre tavsiye metni üretir."""
    prompt = PROMPT_QUIZ_RECOMMENDATION.format(
        konu=konu,
        toplam_soru=toplam_soru,
        dogru_sayisi=dogru_sayisi,
        yanlis_sayisi=yanlis_sayisi,
        soru_cevap_ozeti=soru_cevap_ozeti
    )
    
    if ai_provider == "Groq":
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq paketi yüklü değil.")
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        _model = model_name or "llama-3.3-70b-versatile"
        
        response = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": "Samimi ve faydalı eğitim tavsiyeleri üreten bir uzmansın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
        
    else:
        # Gemini
        # Tavsiye metni JSON olmak zorunda olmadığı için normal GenerativeModel kullanalım
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY bulunamadı.")
        genai.configure(api_key=api_key)
        _model = model_name or "gemini-2.0-flash"
        model = genai.GenerativeModel(_model)
        response = model.generate_content(prompt)
        return response.text

