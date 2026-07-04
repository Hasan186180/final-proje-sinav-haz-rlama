"""
app.py — AI Destekli Akıllı Sınav Hazırlama Sistemi
Ana Streamlit uygulaması
Sorumlu: Hasan Yiğit Çontar
"""

import json
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

import database as db
import ai_service
import pdf_export

load_dotenv()

# =========================================================================== #
#  Sayfa yapılandırması                                                         #
# =========================================================================== #

st.set_page_config(
    page_title="AI Sınav Hazırlayıcı",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================== #
#  Custom CSS — Premium karanlık tema                                           #
# =========================================================================== #

st.markdown(
    """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Streamlit ana arka plan ── */
.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── Kenar çubuğu ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid rgba(67, 97, 238, 0.3);
}

section[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}

/* ── Başlık bölümü ── */
.hero-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #1e2a4a 50%, #1a1f2e 100%);
    border: 1px solid rgba(67, 97, 238, 0.4);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(67, 97, 238, 0.15);
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(67, 97, 238, 0.08) 0%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4361ee, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    position: relative;
}

.hero-subtitle {
    color: #8b949e;
    font-size: 1.1rem;
    font-weight: 400;
    position: relative;
}

/* ── Kart bileşeni ── */
.exam-card {
    background: linear-gradient(145deg, #161b22, #1c2333);
    border: 1px solid rgba(67, 97, 238, 0.25);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.exam-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(67, 97, 238, 0.2);
    border-color: rgba(67, 97, 238, 0.5);
}

/* ── Soru kartı ── */
.question-card {
    background: linear-gradient(145deg, #1c2333, #1a2035);
    border: 1px solid rgba(67, 97, 238, 0.2);
    border-left: 4px solid #4361ee;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.question-card:hover {
    border-left-color: #7c3aed;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.15);
}

.question-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #4361ee, #7c3aed);
    color: white;
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 0.8rem;
    flex-shrink: 0;
}

.question-text {
    color: #e6edf3;
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.6;
}

.option-item {
    display: flex;
    align-items: flex-start;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: #c9d1d9;
    font-size: 0.95rem;
    transition: all 0.2s ease;
}

.option-item:hover {
    background: rgba(67, 97, 238, 0.08);
    border-color: rgba(67, 97, 238, 0.3);
}

.option-correct {
    background: rgba(16, 185, 129, 0.12) !important;
    border-color: rgba(16, 185, 129, 0.4) !important;
    color: #10b981 !important;
    font-weight: 600 !important;
}

.option-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    font-weight: 700;
    font-size: 0.8rem;
    margin-right: 0.7rem;
    flex-shrink: 0;
}

/* ── Rozet ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-easy   { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-medium { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-hard   { background: rgba(239, 68, 68, 0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-ai     { background: rgba(67, 97, 238, 0.15);  color: #4361ee; border: 1px solid rgba(67,97,238,0.3); }

/* ── İstatistik kartı ── */
.stat-card {
    background: linear-gradient(145deg, #1c2333, #1a2035);
    border: 1px solid rgba(67, 97, 238, 0.2);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4361ee, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: #8b949e;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.3rem;
}

/* ── Streamlit widget özelleştirmeleri ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #1c2333 !important;
    border: 1px solid rgba(67, 97, 238, 0.3) !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #4361ee !important;
    box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15) !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: #1c2333 !important;
    border: 1px solid rgba(67, 97, 238, 0.3) !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
}

/* Butonlar */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4361ee, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(67, 97, 238, 0.3) !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(67, 97, 238, 0.4) !important;
}

/* Download butonları */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1c2333, #1e2a4a) !important;
    color: #4361ee !important;
    border: 1px solid rgba(67, 97, 238, 0.4) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, #4361ee, #7c3aed) !important;
    color: white !important;
}

/* Expander */
div[data-testid="stExpander"] {
    background: linear-gradient(145deg, #161b22, #1c2333) !important;
    border: 1px solid rgba(67, 97, 238, 0.2) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

div[data-testid="stExpander"] summary {
    color: #e6edf3 !important;
    font-weight: 600 !important;
    padding: 1rem !important;
}

/* Radio butonları */
div[data-testid="stRadio"] label {
    color: #c9d1d9 !important;
}

/* Slider */
div[data-testid="stSlider"] * { color: #e6edf3 !important; }

/* Metin renkleri */
.stMarkdown, .stMarkdown p, .stMarkdown li {
    color: #c9d1d9 !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #e6edf3 !important;
}

/* Uyarı/bilgi kutuları */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* Tablo */
div[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
}

/* Divider */
hr {
    border-color: rgba(67, 97, 238, 0.2) !important;
}

/* Spinner */
div[data-testid="stSpinner"] {
    color: #4361ee !important;
}

/* Klasik soru item */
.classic-item {
    background: rgba(67, 97, 238, 0.06);
    border: 1px solid rgba(67, 97, 238, 0.15);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #c9d1d9;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Çalışma tavsiyesi */
.study-tip {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(67, 97, 238, 0.08));
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 12px;
    padding: 1.5rem;
    color: #c9d1d9;
    font-size: 1rem;
    line-height: 1.7;
}

/* Cevap anahtarı grid */
.answer-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    padding: 0.5rem 0;
}

.answer-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    color: #10b981;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Geçmiş sınav satırı */
.history-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(145deg, #1c2333, #1a2035);
    border: 1px solid rgba(67, 97, 238, 0.15);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s ease;
}

.history-row:hover {
    border-color: rgba(67, 97, 238, 0.4);
    box-shadow: 0 4px 15px rgba(67, 97, 238, 0.1);
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================================== #
#  Session state başlatma                                                       #
# =========================================================================== #

for key, default in {
    "sinav": None,
    "sinav_meta": None,
    "aktif_sekme": "olustur",
    "goruntulenecek_sinav_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================================== #
#  Yardımcı fonksiyonlar                                                        #
# =========================================================================== #

ZORLUK_RENK = {"Kolay": "badge-easy", "Orta": "badge-medium", "Zor": "badge-hard"}
MODEL_SECENEKLER = {
    "Gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    "Groq": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
}


def zorluk_badge(zorluk: str) -> str:
    cls = ZORLUK_RENK.get(zorluk, "badge-ai")
    return f'<span class="badge {cls}">{zorluk}</span>'


def render_sinav(sinav: dict, show_answers: bool = False) -> None:
    """Sınav içeriğini zengin formatta render eder."""

    # ── 1. Konu Özeti ──────────────────────────────────────────────────────── #
    with st.expander("📖 Konu Özeti", expanded=True):
        st.markdown(
            f'<div class="exam-card">'
            f'<p style="color:#c9d1d9;font-size:1rem;line-height:1.8;margin:0">'
            f'{sinav.get("ozet", "")}'
            f"</p></div>",
            unsafe_allow_html=True,
        )

    # ── 2. Test Soruları ───────────────────────────────────────────────────── #
    with st.expander("📝 Test Soruları", expanded=True):
        for i, soru_obj in enumerate(sinav.get("test_sorulari", []), 1):
            soru_metni = soru_obj.get("soru", "")
            secenekler = soru_obj.get("secenekler", {})
            dogru = soru_obj.get("dogru", "")

            st.markdown(
                f'<div class="question-card">'
                f'<div style="display:flex;align-items:flex-start;margin-bottom:1rem">'
                f'<span class="question-number">{i}</span>'
                f'<span class="question-text">{soru_metni}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

            if isinstance(secenekler, dict):
                for harf, metin in secenekler.items():
                    is_correct = show_answers and harf == dogru
                    extra_cls = "option-correct" if is_correct else ""
                    check = " ✓" if is_correct else ""
                    st.markdown(
                        f'<div class="option-item {extra_cls}">'
                        f'<span class="option-badge">{harf}</span>'
                        f"{metin}{check}</div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Cevap Anahtarı ─────────────────────────────────────────────────── #
    with st.expander("🔑 Cevap Anahtarı"):
        chips = ""
        for i, soru_obj in enumerate(sinav.get("test_sorulari", []), 1):
            dogru = soru_obj.get("dogru", "?")
            chips += f'<span class="answer-chip">S{i}: {dogru}</span>'
        st.markdown(
            f'<div class="answer-grid">{chips}</div>', unsafe_allow_html=True
        )

    # ── 4. Klasik Sorular ─────────────────────────────────────────────────── #
    with st.expander("✍️ Klasik Sorular"):
        for i, soru in enumerate(sinav.get("klasik_sorular", []), 1):
            st.markdown(
                f'<div class="classic-item"><strong style="color:#4361ee">Soru {i}:</strong> {soru}</div>',
                unsafe_allow_html=True,
            )

    # ── 5. Çalışma Önerisi ────────────────────────────────────────────────── #
    with st.expander("💡 Çalışma Tavsiyesi", expanded=True):
        st.markdown(
            f'<div class="study-tip">💡 {sinav.get("calisma_onerisi", "")}</div>',
            unsafe_allow_html=True,
        )


def render_export_buttons(sinav: dict, meta: dict) -> None:
    """PDF, Word ve CSV indirme düğmelerini gösterir."""
    st.markdown("### 📤 Dışa Aktar")
    col1, col2, col3 = st.columns(3)

    tarih_str = meta.get("tarih", datetime.now().strftime("%Y-%m-%d_%H-%M"))
    konu_slug = meta.get("konu", "sinav").replace(" ", "_")[:30]
    dosya_adi = f"{konu_slug}_{tarih_str}"

    with col1:
        try:
            pdf_bytes = pdf_export.generate_pdf(sinav, meta)
            st.download_button(
                label="📄 PDF İndir",
                data=pdf_bytes,
                file_name=f"{dosya_adi}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_{dosya_adi}",
            )
        except Exception as e:
            st.warning(f"PDF: {e}")

    with col2:
        try:
            word_bytes = pdf_export.generate_word(sinav, meta)
            st.download_button(
                label="📝 Word İndir",
                data=word_bytes,
                file_name=f"{dosya_adi}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"word_{dosya_adi}",
            )
        except Exception as e:
            st.warning(f"Word: {e}")

    with col3:
        try:
            csv_str = pdf_export.generate_csv(sinav, meta)
            st.download_button(
                label="📊 CSV İndir",
                data=csv_str.encode("utf-8-sig"),
                file_name=f"{dosya_adi}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"csv_{dosya_adi}",
            )
        except Exception as e:
            st.warning(f"CSV: {e}")


# =========================================================================== #
#  Kenar çubuğu                                                                 #
# =========================================================================== #

with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=250)
    else:
        st.markdown(
            """
            <div style="text-align:center;padding:1.5rem 0 1rem">
                <div style="font-size:3rem">🎓</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown(
        """
        <div style="text-align:center;padding:0 0 1rem">
            <div style="font-size:1.3rem;font-weight:800;
                background:linear-gradient(135deg,#4361ee,#7c3aed);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin-top:0.3rem">
                AI Sınav
            </div>
            <div style="color:#8b949e;font-size:0.8rem;margin-top:0.2rem">
                Hazırlayıcı v1.0
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # İstatistikler
    stats = db.get_stats()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-number">{stats["toplam_sinav"]}</div>'
            f'<div class="stat-label">Toplam Sınav</div></div>',
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-number">{stats["toplam_soru"]}</div>'
            f'<div class="stat-label">Toplam Soru</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Navigasyon
    st.markdown(
        '<div style="color:#8b949e;font-size:0.75rem;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem">'
        "MENÜ</div>",
        unsafe_allow_html=True,
    )

    if st.button("➕ Yeni Sınav Oluştur", use_container_width=True, key="nav_olustur"):
        st.session_state.aktif_sekme = "olustur"
        st.session_state.goruntulenecek_sinav_id = None
        st.rerun()

    if st.button("🧠 İnteraktif Sınav", use_container_width=True, key="nav_interactive"):
        st.session_state.aktif_sekme = "interactive"
        st.session_state.goruntulenecek_sinav_id = None
        st.rerun()

    if st.button("📚 Geçmiş Sınavlar", use_container_width=True, key="nav_gecmis"):
        st.session_state.aktif_sekme = "gecmis"
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="color:#8b949e;font-size:0.75rem;text-align:center">'
        "Hasan Yiğit Çontar<br>AI Sınav Hazırlama Sistemi</div>",
        unsafe_allow_html=True,
    )

# =========================================================================== #
#  Ana içerik                                                                   #
# =========================================================================== #

# ── Hero başlık ─────────────────────────────────────────────────────────── #
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">🎓 AI Sınav Hazırlayıcı</div>
        <div class="hero-subtitle">
            Yapay Zekâ destekli otomatik sınav ve çalışma materyali üretim sistemi
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================================== #
#  SEKME: Yeni Sınav Oluştur                                                    #
# =========================================================================== #

if st.session_state.aktif_sekme == "olustur":

    st.markdown("## ✏️ Sınav Parametrelerini Belirle")

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            konu = st.text_input(
                "📌 Konu Adı",
                placeholder="örn: Python Döngüler, Osmanlı Tarihi, Fotosentez…",
                help="Sınav hazırlanacak konuyu girin.",
                key="konu_input",
            )

        with col2:
            ai_provider = st.selectbox(
                "🤖 AI Modeli",
                options=["Gemini", "Groq"],
                index=0,
                key="ai_provider",
                help="Kullanılacak yapay zekâ sağlayıcısını seçin.",
            )

        col3, col4, col5 = st.columns([1, 1, 1])

        with col3:
            soru_sayisi = st.slider(
                "🔢 Test Sorusu Sayısı",
                min_value=3,
                max_value=20,
                value=10,
                step=1,
                key="soru_sayisi",
            )

        with col4:
            zorluk = st.radio(
                "⚡ Zorluk Seviyesi",
                options=["Kolay", "Orta", "Zor"],
                index=1,
                key="zorluk",
                horizontal=True,
            )

        with col5:
            model_list = MODEL_SECENEKLER.get(ai_provider, ["gemini-2.0-flash"])
            secili_model = st.selectbox(
                "🧠 Model Versiyonu",
                options=model_list,
                key="model_version",
            )

    st.markdown("---")

    # API anahtarları sadece .env veya Streamlit Secrets üzerinden yüklenir.

    # Hazırla butonu
    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 2])
    with btn_col1:
        hazirla_btn = st.button(
            "🚀 Sınavı Hazırla",
            use_container_width=True,
            key="hazirla_btn",
            type="primary",
        )
    with btn_col2:
        demo_btn = st.button(
            "🧪 Demo Sınav Oluştur",
            use_container_width=True,
            key="demo_btn",
        )

    if demo_btn:
        demo_sinav = {
            "ozet": "Python döngüleri, belirli bir kod bloğunun belirli koşullar altında tekrar tekrar çalıştırılmasını sağlar. En sık kullanılan döngüler 'for' ve 'while' döngüleridir. 'for' döngüsü genellikle belirli elemanlar üzerinde dönmek için tercih edilirken, 'while' döngüsü bir koşul doğru olduğu sürece çalışmaya devam eder. Döngülerin kontrolü için 'break' ve 'continue' ifadeleri de kullanılır.",
            "test_sorulari": [
                {
                    "soru": "Python'da bir döngüyü tamamen sonlandırmak için hangi anahtar kelime kullanılır?",
                    "secenekler": {
                        "A": "continue",
                        "B": "break",
                        "C": "pass",
                        "D": "exit"
                    },
                    "dogru": "B"
                },
                {
                    "soru": "Aşağıdaki döngülerden hangisi bir listenin elemanlarını tek tek dönmek için en uygundur?",
                    "secenekler": {
                        "A": "while döngüsü",
                        "B": "for döngüsü",
                        "C": "if-else yapısı",
                        "D": "try-except bloğu"
                    },
                    "dogru": "B"
                }
            ],
            "klasik_sorular": [
                "Python'daki 'for' ve 'while' döngüleri arasındaki fark nedir?",
                "'break' ve 'continue' ifadelerinin döngü içindeki işlevlerini açıklayın.",
                "Sonsuz döngü nedir ve nasıl önlenir?",
                "Python'da iç içe döngülerin (nested loops) performans üzerindeki etkisi nedir?",
                "range() fonksiyonunun döngülerde kullanımını bir örnekle açıklayın."
            ],
            "calisma_onerisi": "Döngüleri daha iyi anlamak için listenin elemanlarını filtreleme ve sayı tahmin oyunu gibi küçük uygulamalar geliştirebilirsiniz."
        }
        
        exam_id = db.save_exam(
            konu="Python Döngüler (Demo)",
            soru_sayisi=len(demo_sinav["test_sorulari"]),
            zorluk="Orta",
            sinav_icerigi=demo_sinav,
            ai_model="Demo / Mock",
        )
        
        st.session_state.sinav = demo_sinav
        st.session_state.sinav_meta = {
            "konu": "Python Döngüler (Demo)",
            "zorluk": "Orta",
            "soru_sayisi": len(demo_sinav["test_sorulari"]),
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ai_model": "Demo / Mock",
            "db_id": exam_id,
        }
        st.success(f"✅ Demo sınav başarıyla oluşturuldu! (ID: #{exam_id})")
        st.rerun()

    if hazirla_btn:
        if not konu.strip():
            st.error("⚠️ Lütfen bir konu adı girin!")
        else:
            with st.spinner(
                f"🤖 {ai_provider} ({secili_model}) ile **{konu}** konusunda "
                f"{soru_sayisi} soruluk **{zorluk}** seviye sınav hazırlanıyor…"
            ):
                try:
                    sinav_verisi = ai_service.generate_exam(
                        konu=konu.strip(),
                        soru_sayisi=soru_sayisi,
                        zorluk=zorluk,
                        ai_provider=ai_provider,
                        model_name=secili_model,
                    )

                    # Veritabanına kaydet
                    exam_id = db.save_exam(
                        konu=konu.strip(),
                        soru_sayisi=len(sinav_verisi.get("test_sorulari", [])),
                        zorluk=zorluk,
                        sinav_icerigi=sinav_verisi,
                        ai_model=f"{ai_provider}/{secili_model}",
                    )

                    st.session_state.sinav = sinav_verisi
                    st.session_state.sinav_meta = {
                        "konu": konu.strip(),
                        "zorluk": zorluk,
                        "soru_sayisi": len(sinav_verisi.get("test_sorulari", [])),
                        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "ai_model": f"{ai_provider}/{secili_model}",
                        "db_id": exam_id,
                    }
                    st.success(
                        f"✅ Sınav başarıyla oluşturuldu! (ID: #{exam_id})"
                    )

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        st.error("❌ Hata (Limit Aşıldı - 429): Yapay zekâ modelinin ücretsiz kullanım kotası (Rate Limit / Quota) dolmuştur. Lütfen 1 dakika bekleyip tekrar deneyin ya da farklı bir AI model sağlayıcısı (örn: Groq) seçin.")
                    elif "api" in error_msg.lower() or "key" in error_msg.lower():
                        st.error("❌ Hata (API Anahtarı): Geçersiz veya eksik API anahtarı. Lütfen Streamlit Cloud Secrets ayarlarınızı veya yerel .env dosyasını kontrol edin.")
                    else:
                        st.error(f"❌ Hata oluştu: {error_msg}")

    # Mevcut sınav varsa göster
    if st.session_state.sinav:
        meta = st.session_state.sinav_meta or {}
        sinav = st.session_state.sinav

        st.markdown("---")
        st.markdown("## 📋 Oluşturulan Sınav")

        # Meta bilgi bandı
        badge_html = zorluk_badge(meta.get("zorluk", ""))
        st.markdown(
            f"""
            <div class="exam-card" style="margin-bottom:1.5rem">
                <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                    <div>
                        <span style="color:#8b949e;font-size:0.8rem">KONU</span><br>
                        <span style="color:#e6edf3;font-weight:700;font-size:1.1rem">
                            {meta.get("konu","")}
                        </span>
                    </div>
                    <div style="margin-left:auto;display:flex;gap:0.8rem;align-items:center;flex-wrap:wrap">
                        {badge_html}
                        <span class="badge badge-ai">🤖 {meta.get("ai_model","")}</span>
                        <span class="badge badge-ai">📝 {meta.get("soru_sayisi","")} Soru</span>
                        <span style="color:#8b949e;font-size:0.85rem">
                            🕐 {meta.get("tarih","")}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Cevapları göster/gizle
        show_ans = st.toggle(
            "👁️ Cevapları Test Sorularında Göster",
            value=False,
            key="show_answers",
        )

        render_sinav(sinav, show_answers=show_ans)

        st.markdown("---")
        render_export_buttons(sinav, meta)


# =========================================================================== #
#  SEKME: Geçmiş Sınavlar                                                       #
# =========================================================================== #

elif st.session_state.aktif_sekme == "gecmis":

    st.markdown("## 📚 Geçmiş Sınavlar")

    # Arama
    search_col, _ = st.columns([2, 3])
    with search_col:
        arama = st.text_input(
            "🔍 Konu Ara",
            placeholder="Konu adını yazın…",
            key="arama_input",
        )

    sinav_listesi = db.list_exams(search_query=arama or None)

    if not sinav_listesi:
        st.markdown(
            """
            <div style="text-align:center;padding:4rem 2rem;color:#8b949e">
                <div style="font-size:3rem;margin-bottom:1rem">📭</div>
                <div style="font-size:1.1rem;font-weight:500">Henüz sınav oluşturulmadı</div>
                <div style="font-size:0.9rem;margin-top:0.5rem">
                    Yeni bir sınav oluşturmak için sol menüden "Yeni Sınav Oluştur"a tıklayın.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="color:#8b949e;font-size:0.9rem;margin-bottom:1rem">'
            f"Toplam {len(sinav_listesi)} sınav bulundu.</div>",
            unsafe_allow_html=True,
        )

        for exam in sinav_listesi:
            col_info, col_btn1, col_btn2 = st.columns([5, 1, 1])

            with col_info:
                badge_html = zorluk_badge(exam["zorluk"])
                st.markdown(
                    f"""
                    <div class="history-row">
                        <div>
                            <span style="color:#e6edf3;font-weight:600;font-size:1rem">
                                #{exam["id"]} — {exam["konu"]}
                            </span><br>
                            <span style="color:#8b949e;font-size:0.82rem">
                                🕐 {exam["tarih"]}  |  
                                📝 {exam["soru_sayisi"]} soru  |  
                                🤖 {exam["ai_model"]}
                            </span>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_btn1:
                if st.button(
                    "👁️ Görüntüle",
                    key=f"view_{exam['id']}",
                    use_container_width=True,
                ):
                    st.session_state.goruntulenecek_sinav_id = exam["id"]
                    st.rerun()

            with col_btn2:
                if st.button(
                    "🗑️ Sil",
                    key=f"del_{exam['id']}",
                    use_container_width=True,
                ):
                    db.delete_exam(exam["id"])
                    if st.session_state.goruntulenecek_sinav_id == exam["id"]:
                        st.session_state.goruntulenecek_sinav_id = None
                    st.rerun()

    # Seçili sınavı görüntüle
    if st.session_state.goruntulenecek_sinav_id:
        selected = db.get_exam_by_id(st.session_state.goruntulenecek_sinav_id)
        if selected:
            st.markdown("---")
            st.markdown(
                f"## 📋 Sınav #{selected['id']}: {selected['konu']}"
            )

            meta_view = {
                "konu": selected["konu"],
                "zorluk": selected["zorluk"],
                "soru_sayisi": selected["soru_sayisi"],
                "tarih": selected["tarih"],
                "ai_model": selected["ai_model"],
            }

            show_ans_hist = st.toggle(
                "👁️ Cevapları Göster",
                value=False,
                key=f"show_ans_hist_{selected['id']}",
            )

            render_sinav(selected["olusturulan_sinav"], show_answers=show_ans_hist)

            st.markdown("---")
            render_export_buttons(selected["olusturulan_sinav"], meta_view)

            if st.button("← Listeye Dön", key="back_to_list"):
                st.session_state.goruntulenecek_sinav_id = None
                st.rerun()


# =========================================================================== #
#  SEKME: İnteraktif Sınav Modu                                                 #
# =========================================================================== #

elif st.session_state.aktif_sekme == "interactive":
    st.markdown("## 🧠 İnteraktif Sınav Modu (Dinamik Zorluk)")
    st.markdown(
        "Bu modda sorular tek tek üretilir. Doğru bilirseniz bir sonraki sorunun "
        "zorluğu artar, yanlış bilirseniz aynı zorluk seviyesinde kalır."
    )

    # State değişkenlerini ilklendir
    quiz_keys = {
        "quiz_aktif": False,
        "quiz_konu": "",
        "quiz_toplam_soru": 5,
        "quiz_mevcut_soru_no": 1,
        "quiz_zorluk": "Kolay",
        "quiz_sorular": [],
        "quiz_mevcut_soru": None,
        "quiz_dogru_sayisi": 0,
        "quiz_yanlis_sayisi": 0,
        "quiz_bitti": False,
        "quiz_tavsiye": "",
        "quiz_secilen_cevap": None,
        "quiz_cevaplandi": False,
        "quiz_sonuc_db_id": None
    }
    for qkey, qval in quiz_keys.items():
        if qkey not in st.session_state:
            st.session_state[qkey] = qval

    # 1. QUIZ BAŞLAMAMIŞSA: Parametre Giriş Ekranı
    if not st.session_state.quiz_aktif and not st.session_state.quiz_bitti:
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                konu_secilen = st.text_input(
                    "📌 Sınav Konusu",
                    placeholder="örn: Python Listeler, İklim Değişikliği...",
                    key="quiz_konu_input"
                )
            with col2:
                toplam_soru_secilen = st.slider(
                    "🔢 Soru Sayısı",
                    min_value=3,
                    max_value=15,
                    value=5,
                    step=1,
                    key="quiz_soru_slider"
                )

            col3, col4 = st.columns(2)
            with col3:
                baslangic_zorluk = st.selectbox(
                    "⚡ Başlangıç Zorluğu",
                    options=["Kolay", "Orta", "Zor"],
                    index=0,
                    key="quiz_baslangic_zorluk"
                )
            with col4:
                ai_provider_quiz = st.selectbox(
                    "🤖 Yapay Zekâ Sağlayıcısı",
                    options=["Gemini", "Groq"],
                    index=0,
                    key="quiz_ai_provider"
                )

            # Model seçimi
            model_list_quiz = MODEL_SECENEKLER.get(ai_provider_quiz, ["gemini-2.0-flash"])
            model_secilen_quiz = st.selectbox(
                "🧠 Model Sürümü",
                options=model_list_quiz,
                key="quiz_model_version"
            )

        st.markdown("---")

        # Butonlar
        col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 2])
        with col_btn1:
            quiz_baslat = st.button("🚀 Sınavı Başlat", type="primary", use_container_width=True, key="start_quiz_btn")
        with col_btn2:
            quiz_demo = st.button("🧪 Demo Sınav Başlat", use_container_width=True, key="start_demo_quiz_btn")

        if quiz_baslat:
            if not konu_secilen.strip():
                st.error("⚠️ Lütfen bir konu adı girin!")
            else:
                st.session_state.quiz_konu = konu_secilen.strip()
                st.session_state.quiz_toplam_soru = toplam_soru_secilen
                st.session_state.quiz_zorluk = baslangic_zorluk
                st.session_state.quiz_aktif = True
                st.session_state.quiz_mevcut_soru_no = 1
                st.session_state.quiz_sorular = []
                st.session_state.quiz_dogru_sayisi = 0
                st.session_state.quiz_yanlis_sayisi = 0
                st.session_state.quiz_bitti = False
                st.session_state.quiz_cevaplandi = False
                st.session_state.quiz_secilen_cevap = None

                with st.spinner("İlk soru hazırlanıyor..."):
                    try:
                        soru_obj = ai_service.generate_single_question(
                            konu=st.session_state.quiz_konu,
                            zorluk=st.session_state.quiz_zorluk,
                            ai_provider=ai_provider_quiz,
                            model_name=model_secilen_quiz
                        )
                        st.session_state.quiz_mevcut_soru = soru_obj
                        st.rerun()
                    except Exception as e:
                        st.session_state.quiz_aktif = False
                        error_msg = str(e)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            st.error("❌ Hata (Limit Aşıldı - 429): Yapay zekâ modelinin ücretsiz kullanım kotası (Rate Limit / Quota) dolmuştur. Lütfen 1 dakika bekleyip tekrar deneyin ya da farklı bir AI model sağlayıcısı (örn: Groq) seçin.")
                        elif "api" in error_msg.lower() or "key" in error_msg.lower():
                            st.error("❌ Hata (API Anahtarı): Geçersiz veya eksik API anahtarı. Lütfen Streamlit Cloud Secrets ayarlarınızı veya yerel .env dosyasını kontrol edin.")
                        else:
                            st.error(f"Soru üretilirken hata oluştu: {error_msg}")

        if quiz_demo:
            st.session_state.quiz_konu = "Python Listeler (Demo)"
            st.session_state.quiz_toplam_soru = 3
            st.session_state.quiz_zorluk = "Kolay"
            st.session_state.quiz_aktif = True
            st.session_state.quiz_mevcut_soru_no = 1
            st.session_state.quiz_sorular = []
            st.session_state.quiz_dogru_sayisi = 0
            st.session_state.quiz_yanlis_sayisi = 0
            st.session_state.quiz_bitti = False
            st.session_state.quiz_cevaplandi = False
            st.session_state.quiz_secilen_cevap = None
            
            # Mock ilk soru
            st.session_state.quiz_mevcut_soru = {
                "soru": "Python'da boş bir liste oluşturmak için hangisi kullanılır?",
                "secenekler": {
                    "A": "list = {}",
                    "B": "list = []",
                    "C": "list = ()",
                    "D": "list = empty()"
                },
                "dogru": "B"
            }
            st.rerun()

    # 2. QUIZ AKTİFSE: Soru Gösterim ve Cevaplama Ekranı
    elif st.session_state.quiz_aktif and st.session_state.quiz_mevcut_soru:
        konu = st.session_state.quiz_konu
        soru_no = st.session_state.quiz_mevcut_soru_no
        toplam = st.session_state.quiz_toplam_soru
        zorluk = st.session_state.quiz_zorluk
        soru_obj = st.session_state.quiz_mevcut_soru

        # Durum bandı
        badge_html = zorluk_badge(zorluk)
        st.markdown(
            f"""
            <div class="exam-card" style="margin-bottom:1.5rem">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap">
                    <div>
                        <span style="color:#8b949e;font-size:0.8rem">KONU</span><br>
                        <span style="color:#e6edf3;font-weight:700;font-size:1.1rem">{konu}</span>
                    </div>
                    <div style="display:flex;gap:0.8rem;align-items:center">
                        <span class="badge badge-ai">Soru: {soru_no} / {toplam}</span>
                        {badge_html}
                        <span class="badge badge-easy" style="background:rgba(16,185,129,0.1);color:#10b981">
                            ✓ Doğru: {st.session_state.quiz_dogru_sayisi}
                        </span>
                        <span class="badge badge-hard" style="background:rgba(239,68,68,0.1);color:#ef4444">
                            &nbsp;Yanlış: {st.session_state.quiz_yanlis_sayisi}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Soru Kartı
        st.markdown(
            f'<div class="question-card">'
            f'<div style="display:flex;align-items:flex-start;margin-bottom:1rem">'
            f'<span class="question-number">{soru_no}</span>'
            f'<span class="question-text">{soru_obj.get("soru")}</span>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # Seçenekler
        secenekler = soru_obj.get("secenekler", {})
        dogru_cevap = soru_obj.get("dogru", "")

        # Kullanıcı cevap seçimi
        secim = st.radio(
            "Cevabınızı seçin:",
            options=["A", "B", "C", "D"],
            format_func=lambda x: f"{x}) {secenekler.get(x, '')}",
            key=f"quiz_radio_s{soru_no}",
            index=None if not st.session_state.quiz_cevaplandi else ["A", "B", "C", "D"].index(st.session_state.quiz_secilen_cevap)
        )

        if not st.session_state.quiz_cevaplandi:
            if st.button("Cevabı Gönder", type="primary", key=f"submit_ans_{soru_no}"):
                if secim is None:
                    st.warning("⚠️ Lütfen bir seçeneği işaretleyin!")
                else:
                    st.session_state.quiz_secilen_cevap = secim
                    st.session_state.quiz_cevaplandi = True
                    st.rerun()
        else:
            # Cevap verildi, sonucu göster
            secilen = st.session_state.quiz_secilen_cevap
            is_correct = secilen == dogru_cevap

            if is_correct:
                st.success(f"🎉 Doğru Cevap! Tebrikler. (Doğru seçenek: {dogru_cevap})")
            else:
                st.error(f"❌ Yanlış Cevap. Sizin cevabınız: {secilen} | Doğru cevap: {dogru_cevap}")

            # Sonraki soruya geçiş butonu
            if st.button("Sonraki Soru →" if soru_no < toplam else "Sınavı Bitir ve Sonuçları Gör", key=f"next_question_{soru_no}"):
                
                # Soru geçmişine kaydet
                st.session_state.quiz_sorular.append({
                    "soru": soru_obj.get("soru"),
                    "secenekler": secenekler,
                    "dogru": dogru_cevap,
                    "kullanici_cevabi": secilen,
                    "zorluk": zorluk
                })

                if is_correct:
                    st.session_state.quiz_dogru_sayisi += 1
                    # Zorluğu artır
                    if zorluk == "Kolay":
                        st.session_state.quiz_zorluk = "Orta"
                    elif zorluk == "Orta":
                        st.session_state.quiz_zorluk = "Zor"
                else:
                    st.session_state.quiz_yanlis_sayisi += 1
                    # Bilemezse zorluk aynı kalır

                # Sınav bitti mi kontrol et
                if soru_no >= toplam:
                    st.session_state.quiz_aktif = False
                    st.session_state.quiz_bitti = True
                    
                    # Tavsiye raporu üret
                    with st.spinner("Çalışma önerileriniz yapay zekâ tarafından hazırlanıyor..."):
                        if "Demo" in konu:
                            st.session_state.quiz_tavsiye = (
                                "Harika bir denemeydi! Python Listeler konusunda listelerin "
                                "tanımlanması, eleman ekleme (append) ve çıkarma (remove/pop) "
                                "gibi temel metotları tekrar etmeniz yararlı olacaktır. Bol pratik yapın!"
                            )
                            # Demo sınavı veritabanına kaydet
                            mock_sinav_db = {
                                "ozet": f"İnteraktif {konu} sınav özeti.",
                                "test_sorulari": st.session_state.quiz_sorular,
                                "klasik_sorular": ["İnteraktif sınavda klasik sorular bulunmamaktadır."],
                                "calisma_onerisi": st.session_state.quiz_tavsiye
                            }
                            db_id = db.save_exam(
                                konu=konu,
                                soru_sayisi=toplam,
                                zorluk="Dinamik",
                                sinav_icerigi=mock_sinav_db,
                                ai_model="Demo / Mock Quiz"
                            )
                            st.session_state.quiz_sonuc_db_id = db_id
                        else:
                            try:
                                # Soru cevap özeti oluştur
                                ozet_lines = []
                                for idx, q in enumerate(st.session_state.quiz_sorular, 1):
                                    ozet_lines.append(
                                        f"Soru {idx} [{q['zorluk']}]: {q['soru']}\n"
                                        f"Doğru Cevap: {q['dogru']} | Öğrencinin Cevabı: {q['kullanici_cevabi']}\n"
                                        f"Sonuç: {'Doğru' if q['dogru'] == q['kullanici_cevabi'] else 'Yanlış'}\n"
                                    )
                                ozet_str = "\n".join(ozet_lines)

                                tavsiye = ai_service.generate_quiz_recommendation(
                                    konu=konu,
                                    toplam_soru=toplam,
                                    dogru_sayisi=st.session_state.quiz_dogru_sayisi,
                                    yanlis_sayisi=st.session_state.quiz_yanlis_sayisi,
                                    soru_cevap_ozeti=ozet_str,
                                    ai_provider=st.session_state.quiz_ai_provider,
                                    model_name=st.session_state.quiz_model_version
                                )
                                st.session_state.quiz_tavsiye = tavsiye
                                
                                # Sınavı veritabanına kaydet
                                sinav_db_data = {
                                    "ozet": f"İnteraktif {konu} konusu dinamik sınav özeti.",
                                    "test_sorulari": st.session_state.quiz_sorular,
                                    "klasik_sorular": ["İnteraktif sınav modunda açık uçlu klasik soru sorulmamıştır."],
                                    "calisma_onerisi": tavsiye
                                }
                                db_id = db.save_exam(
                                    konu=konu,
                                    soru_sayisi=toplam,
                                    zorluk="Dinamik",
                                    sinav_icerigi=sinav_db_data,
                                    ai_model=f"{st.session_state.quiz_ai_provider}/{st.session_state.quiz_model_version}"
                                )
                                st.session_state.quiz_sonuc_db_id = db_id
                            except Exception as ex:
                                st.session_state.quiz_tavsiye = f"Tavsiye oluşturulurken hata: {ex}"
                else:
                    # Sıradaki soruyu getir
                    st.session_state.quiz_mevcut_soru_no += 1
                    st.session_state.quiz_cevaplandi = False
                    st.session_state.quiz_secilen_cevap = None

                    if "Demo" in konu:
                        # Demo için bir sonraki mock soruları koyalım
                        s_no = st.session_state.quiz_mevcut_soru_no
                        if s_no == 2:
                            st.session_state.quiz_mevcut_soru = {
                                "soru": "Bir listenin sonuna yeni bir eleman eklemek için hangi metot kullanılır?",
                                "secenekler": {
                                    "A": "add()",
                                    "B": "insert()",
                                    "C": "append()",
                                    "D": "extend()"
                                },
                                "dogru": "C"
                            }
                        elif s_no == 3:
                            st.session_state.quiz_mevcut_soru = {
                                "soru": "my_list = [10, 20, 30] listesinde my_list[-1] ifadesinin çıktısı nedir?",
                                "secenekler": {
                                    "A": "10",
                                    "B": "20",
                                    "C": "30",
                                    "D": "Hata verir"
                                },
                                "dogru": "C"
                            }
                    else:
                        with st.spinner(f"{st.session_state.quiz_mevcut_soru_no}. soru hazırlanıyor..."):
                            try:
                                next_soru = ai_service.generate_single_question(
                                    konu=st.session_state.quiz_konu,
                                    zorluk=st.session_state.quiz_zorluk,
                                    ai_provider=st.session_state.quiz_ai_provider,
                                    model_name=st.session_state.quiz_model_version
                                )
                                st.session_state.quiz_mevcut_soru = next_soru
                            except Exception as ex:
                                error_msg = str(ex)
                                if "429" in error_msg or "quota" in error_msg.lower():
                                    st.error("❌ Hata (Limit Aşıldı - 429): Yapay zekâ modelinin ücretsiz kullanım kotası (Rate Limit / Quota) dolmuştur. Lütfen 1 dakika bekleyip tekrar deneyin ya da farklı bir AI model sağlayıcısı (örn: Groq) seçin.")
                                elif "api" in error_msg.lower() or "key" in error_msg.lower():
                                    st.error("❌ Hata (API Anahtarı): Geçersiz veya eksik API anahtarı. Lütfen Streamlit Cloud Secrets ayarlarınızı veya yerel .env dosyasını kontrol edin.")
                                else:
                                    st.error(f"Soru üretilemedi: {error_msg}")
                st.rerun()

    # 3. QUIZ BİTTİYSE: Sonuç ve Tavsiye Raporu Ekranı
    elif st.session_state.quiz_bitti:
        st.markdown("### 🏆 Sınav Sonuçları")
        
        # Sonuç Paneli
        dogru = st.session_state.quiz_dogru_sayisi
        yanlis = st.session_state.quiz_yanlis_sayisi
        toplam = st.session_state.quiz_toplam_soru
        basari_orani = int((dogru / toplam) * 100) if toplam > 0 else 0

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown(
                f'<div class="stat-card" style="border-color:#10b981">'
                f'<div class="stat-number" style="color:#10b981">{dogru}</div>'
                f'<div class="stat-label">Doğru Sayısı</div></div>',
                unsafe_allow_html=True
            )
        with col_r2:
            st.markdown(
                f'<div class="stat-card" style="border-color:#ef4444">'
                f'<div class="stat-number" style="color:#ef4444">{yanlis}</div>'
                f'<div class="stat-label">Yanlış Sayısı</div></div>',
                unsafe_allow_html=True
            )
        with col_r3:
            st.markdown(
                f'<div class="stat-card" style="border-color:#7c3aed">'
                f'<div class="stat-number" style="color:#7c3aed">%{basari_orani}</div>'
                f'<div class="stat-label">Başarı Oranı</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        
        # Sorter Detayları
        st.markdown("### 📋 Soru ve Cevap Detayları")
        for i, q in enumerate(st.session_state.quiz_sorular, 1):
            is_correct = q["dogru"] == q["kullanici_cevabi"]
            bg_color = "rgba(16,185,129,0.06)" if is_correct else "rgba(239,68,68,0.06)"
            border_color = "#10b981" if is_correct else "#ef4444"
            status_text = "✅ Doğru" if is_correct else "❌ Yanlış"

            st.markdown(
                f'<div class="question-card" style="background:{bg_color};border-left-color:{border_color}">'
                f'<div style="display:flex;justify-content:space-between">'
                f'<div><span class="question-number">{i}</span><span class="question-text">{q["soru"]}</span></div>'
                f'<div><span class="badge" style="background:{border_color}22;color:{border_color}">{status_text}</span></div>'
                f'</div>'
                f'<div style="margin-top:0.8rem;padding-left:2.5rem;font-size:0.9rem;color:#8b949e">'
                f'Zorluk Seviyesi: <strong>{q["zorluk"]}</strong> | '
                f'Verdiğiniz Cevap: <strong>{q["kullanici_cevabi"]}</strong> | '
                f'Doğru Cevap: <strong>{q["dogru"]}</strong>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Çalışma Tavsiyesi
        st.markdown("### 💡 Yapay Zekâ Çalışma Önerisi")
        st.markdown(
            f'<div class="study-tip">💡 {st.session_state.quiz_tavsiye}</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Sınavı Dışa Aktarma
        if st.session_state.quiz_sonuc_db_id:
            meta_quiz_export = {
                "konu": st.session_state.quiz_konu,
                "zorluk": "Dinamik",
                "soru_sayisi": toplam,
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ai_model": "İnteraktif Sınav Modu"
            }
            sinav_quiz_export = {
                "ozet": f"İnteraktif {st.session_state.quiz_konu} Sınavı Raporu",
                "test_sorulari": st.session_state.quiz_sorular,
                "klasik_sorular": ["İnteraktif Sınav Modunda klasik soru sorulmamıştır."],
                "calisma_onerisi": st.session_state.quiz_tavsiye
            }
            render_export_buttons(sinav_quiz_export, meta_quiz_export)

        st.markdown("---")

        # Yeni Sınav Başlat Butonu
        if st.button("🔄 Yeni İnteraktif Sınav Başlat", key="restart_quiz_btn"):
            st.session_state.quiz_aktif = False
            st.session_state.quiz_bitti = False
            st.session_state.quiz_sorular = []
            st.session_state.quiz_dogru_sayisi = 0
            st.session_state.quiz_yanlis_sayisi = 0
            st.session_state.quiz_tavsiye = ""
            st.session_state.quiz_sonuc_db_id = None
            st.rerun()
