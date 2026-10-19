import os
import json
import random
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Shorts Subscriber Studio", page_icon="🔥", layout="wide")
st.title("🔥 Shorts Subscriber Studio")
st.caption("HOOK MENGGELEGAR → RESPON → TUDUHAN CTA → SKAKMAT PUNCHLINE")

LANGUAGES = [
    "Bahasa Indonesia", "English", "Español (Spanish)", "Português (Portuguese)",
    "Français (French)", "Deutsch (German)", "Italiano (Italian)", "日本語 (Japanese)",
    "한국어 (Korean)", "中文简体 (Chinese Simplified)", "中文繁體 (Chinese Traditional)",
    "العربية (Arabic)", "हिन्दी (Hindi)", "বাংলা (Bengali)", "اردو (Urdu)",
    "Русский (Russian)", "Türkçe (Turkish)", "ไทย (Thai)", "Tiếng Việt (Vietnamese)",
    "Filipino", "Bahasa Melayu (Malay)", "Nederlands (Dutch)", "Polski (Polish)",
    "Українська (Ukrainian)", "فارسی (Persian)", "עברית (Hebrew)", "Kiswahili (Swahili)",
    "Bahasa lain (isi sendiri)"
]

BASE_URL = "https://clariohub.id/v1"

def api_key():
    try:
        value = st.secrets.get("CLARIOHUB_API_KEY", "")
        if value:
            return str(value).strip()
    except Exception:
        pass
    return os.getenv("CLARIOHUB_API_KEY", "").strip()

def call_gemini(key, model, prompt):
    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=90.0, max_retries=1)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": (
                "You are an expert YouTube Shorts comedy writer. "
                "Write punchy 8-10 second 4-beat skits: aggressive hook -> confused reaction -> "
                "fourth-wall subscribe accusation -> savage punchline roast. Return valid JSON only."
            )},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        max_tokens=1800,
    )
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("API tidak mengembalikan teks.")
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start:end + 1])
        else:
            raise RuntimeError("Respons model bukan JSON valid. Coba lagi.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Format respons model tidak sesuai.")
    return data

def prompts(x, style, duration, language):
    """Menyusun prompt Flow dan thumbnail dengan tempo fast cuts (shot-reverse-shot)."""
    dialogue_items = [d for d in x.get("dialogue", []) if isinstance(d, dict)]
    dialogue = "\n".join(
        f'{d.get("time", "")} | {d.get("speaker", "KARAKTER")}: "{d.get("line", "")}"'
        for d in dialogue_items
    )

    x["flow_prompt"] = f"""Create ONE coherent, photorealistic {duration} vertical 9:16 {style} YouTube Short skit with rapid shot-reverse-shot comedic pacing.

TITLE: {x.get('title', '')}
HOOK (0-1s): {x.get('hook', '')}
STORY & PREMISE: {x.get('story', '')}
PUNCHLINE: {x.get('punchline', '')}
ENDING: {x.get('ending', '')}

DIALOGUE SCRIPT (PRESERVE EXACT TIMING & ACTORS):
{dialogue}

EDITING & SHOT BREAKDOWN:
- Shot 1 (0–1s) [Extreme Close-Up]: Character A aggressively breaks the 4th wall, shouting/pointing straight into the lens. Instant high energy.
- Shot 2 (1–3s) [Medium Shot Cut]: Character B flinches back in utter confusion/defensiveness.
- Shot 3 (3–6s) [Close-Up Cut]: Character A points aggressively, delivering the funny subscribe accusation directly to camera with animated CTA energy.
- Shot 4 (6–9s) [Two-Shot / Medium-Wide Cut]: Character B roasts Character A with the reality check punchline, bursting into laughter while Character A freezes in awkward shock.

ACTING & AUDIO:
- Precise lip-sync for the active speaker. The listening character reacts with silent, expressive body language.
- Natural {language} colloquial delivery with comic timing.
- Crisp audio, sudden jump in energy on the hook, and clean audio cut on the laugh punchline.

CINEMATOGRAPHY & RESTRICTIONS:
- Seamless wardrobe, face, and atmospheric continuity across cuts.
- Photorealistic textures, cinematic horror-comedy lighting, vertical 9:16 framing.
- No watermark, no subtitles, no AI artifacts."""

    x["thumbnail_prompt"] = f"""Create a viral, high-contrast vertical 9:16 YouTube Shorts thumbnail for: {x.get('title', '')}. Split-second confrontation: {x.get('hook', '')}. Extreme expressive face pointing straight into the camera lens with wide eyes, dramatic lighting, sharp details readable on mobile screens. Clean space at bottom. Cinematic, no text watermark."""
    x.setdefault("hashtags", "#Shorts #KomediHoror #HororLucu #SkitLucu")
    return x

def local_idea():
    pool = [
      {
        "title": "HANTU GAK PUNYA CHANNEL! 👻😂",
        "hook": "Hantu berteriak melotot ke arah kamera: 'WOI!'",
        "story": "Hantu memarahi penonton karena nonton tanpa subscribe, tapi malah diskakmat manusia.",
        "dialogue": [
          {"time": "00:00–00:01", "speaker": "HANTU", "line": "WOI!"},
          {"time": "00:01–00:03", "speaker": "MANUSIA", "line": "Kenapa gue?!"},
          {"time": "00:03–00:06", "speaker": "HANTU", "line": "Gue tahu kebiasaan lu... nonton terus tapi gak subscribe!"},
          {"time": "00:06–00:09", "speaker": "MANUSIA", "line": "Lah, lu aja gak punya channel! Hahaha!"}
        ],
        "punchline": "Manusia tertawa terbahak-bahak mengejek hantu yang melongo malu.",
        "ending": "Hantu terdiam syok menyadari kekonyolannya.",
        "hashtags": "#Shorts #KomediHoror #HororLucu"
      },
      {
        "title": "NAGIH UTANG ATAU SUBSCRIBE?! 💸🤣",
        "hook": "Tukang tagih melotot menunjuk kamera: 'HEI KAMU!'",
        "story": "Debt collector mendatangi pria tapi dialognya melenceng ke urusan subscribe.",
        "dialogue": [
          {"time": "00:00–00:01", "speaker": "PENAGIH", "line": "HEI KAMU!"},
          {"time": "00:01–00:03", "speaker": "WARGA", "line": "Gue belum gajian, Bang!"},
          {"time": "00:03–00:06", "speaker": "PENAGIH", "line": "Bukan duit! Lu nonton tiap hari tapi kenapa gak subscribe?!"},
          {"time": "00:06–00:09", "speaker": "WARGA", "line": "Dih, lu penagih utang apa YouTuber pemula?!"}
        ],
        "punchline": "Warga ngakak sambil menunjuk balik penagih utang yang salah tingkah.",
        "ending": "Penagih utang garuk-garuk kepala kebingungan.",
        "hashtags": "#Shorts #KomediAbsurd #NgakakKocak"
      }
    ]
    return random.choice(pool)

with st.sidebar:
    st.header("Pengaturan API")
    key = api_key()
    if not key:
        key = st.text_input(
            "API Key ClarioHub",
            type="password",
            help="Key ini disimpan sementara untuk sesi ini."
        ).strip()
    st.write("ClarioHub API:", "✅ Key tersedia" if key else "⚠️ Masukkan API key")
    st.caption(f"Endpoint: {BASE_URL}")

    model_options = {
        "Gemini 3.7 Flash": "clario/gemini-3.7-flash",
        "DeepSeek V4 Pro": "clario/deepseek-v4-pro",
        "DeepSeek V4 Flash": "clario/deepseek-v4-flash",
        "GLM 5.3 Flash": "clario/glm-5.3-flash",
        "GPT 5.6 Sol": "clario/gpt-5.6-sol"
    }
    selected_model_label = st.selectbox("Model AI", list(model_options.keys()), index=0)
    model = model_options[selected_model_label]
    st.divider()

    st.header("Pengaturan Konten")
    language_choice = st.selectbox("🌎 Bahasa Cerita & Dialog", LANGUAGES, index=0)
    if language_choice == "Bahasa lain (isi sendiri)":
        custom_language = st.text_input("Nama bahasa", placeholder="Contoh: Sunda, Javanese")
        target_language = custom_language.strip() or "Bahasa Indonesia"
    else:
        target_language = language_choice

    style = st.selectbox("Gaya visual", [
        "Horor-komedi realistis (Hantu vs Manusia)",
        "Komedi absurd realistis",
        "Parodi kriminal kocak",
        "Karakter bebas"
    ])
    duration = st.selectbox("Durasi (Google Flow)", ["8 detik", "10 detik"], index=1)
    humor = st.selectbox("Jenis Punchline", [
        "Skakmat logika / Reality check roast",
        "Kena mental sendiri",
        "Salah paham absurd",
        "Peran tertukar"
    ])
    avoid = st.text_input("Hindari topik/karakter (opsional)")

if "idea" not in st.session_state:
    st.session_state.idea = None

if st.button("🔥 GENERATE SKRIP 4-BEAT", type="primary", use_container_width=True):
    prompt = f"""Create ONE original 8-10 second vertical YouTube Shorts comedy skit designed to gain subscribers.
OUTPUT LANGUAGE: {target_language}. Write title, hook, story, dialogue, punchline, ending, hashtags, and cta_note in {target_language}.

STRUCTURAL BLUEPRINT (Strict 4-beat pacing):
1. BEAT 1 - THE HOOK (00:00–00:01): Karakter A mendadak menyerang/meneriaki kamera/penonton dengan satu seruan tegas (misal: "WOI!", "STOP!", atau tuduhan kaget).
2. BEAT 2 - THE REACTION (00:01–00:03): Karakter B merespons kaget atau bingung (misal: "Kenapa gue?!", "Ada apa nih?").
3. BEAT 3 - THE CTA ACCUSATION (00:03–00:06): Karakter A mendobrak fourth-wall dan menuduh penonton/Karakter B (misal: "Gue tahu kebiasaan lu... nonton doang tapi kagak subscribe!").
4. BEAT 4 - THE PUNCHLINE ROAST (00:06–00:09): Karakter B membalikkan keadaan dengan punchline skakmat yang mempermalukan Karakter A (misal: membalas fakta konyol sehingga Karakter A terdiam melongo), ditutup tawa.

DIALOGUE REQUIREMENTS:
- Tepat 4 baris dialog yang mewakili 4 beat di atas.
- Gunakan bahasa percakapan sehari-hari yang luwes, jangan kaku/formal.
- Beat 3 WAJIB berisi tuduhan subscribe. Beat 4 WAJIB berupa punchline balasan (roasting).

Visual style: {style}. Humor type: {humor}. Duration: {duration}. Avoid: {avoid or 'none'}.
Return valid JSON only with keys: title, hook, story, dialogue (array of 4 objects with time, speaker, line), punchline, ending, hashtags, cta_note."""

    try:
        if not key:
            raise RuntimeError("Masukkan API Key ClarioHub di sidebar.")
        result = call_gemini(key, model.strip(), prompt)
        st.session_state.idea = prompts(result, style, duration, target_language)
    except Exception as e:
        st.error(f"Gagal generate via API: {e}")
        st.warning("Memuat template cadangan berbasis video referensi...")
        st.session_state.idea = prompts(local_idea(), style, duration, target_language)

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title", "Ide Shorts"))
    st.code(x.get("hashtags", "#Shorts #Comedy #Funny"))

    t1, t2, t3, t4 = st.tabs(["Struktur Skit (4-Beat)", "Prompt Video Flow", "Prompt Thumbnail", "Evaluasi Subscriber"])

    with t1:
        st.markdown("**1. HOOK JUMPSCARE (0–1s)**")
        st.write(x.get("hook", ""))

        st.markdown("**2. CERITA & SETUP**")
        st.write(x.get("story", ""))

        st.markdown("**3. DIALOG LENGKAP**")
        for d in x.get("dialogue", []):
            if isinstance(d, dict):
                st.write(f"⏱️ **{d.get('time', '')} | {d.get('speaker', '')}** : \"{d.get('line', '')}\"")

        st.markdown("**4. PUNCHLINE SKAKMAT (6–9s)**")
        st.write(x.get("punchline", ""))

        st.markdown("**5. REAKSI ENDING**")
        st.write(x.get("ending", ""))

    with t2:
        st.caption("Prompt kamera multi-cut (shot-reverse-shot) untuk Google Flow:")
        st.text_area("Salin Prompt Video Flow", x.get("flow_prompt", ""), height=350)

    with t3:
        st.caption("Prompt thumbnail YouTube Shorts 9:16:")
        st.text_area("Salin Prompt Thumbnail", x.get("thumbnail_prompt", ""), height=220)

    with t4:
        col1, col2, col3 = st.columns(3)
        views = col1.number_input("Views Video", min_value=0, step=100)
        subs = col2.number_input("Subscriber Baru", min_value=0, step=1)
        retention = col3.number_input("Average Percentage Viewed (%)", 0.0, 100.0, step=0.5)
        if views > 0:
            cr = (subs / views) * 100
            st.metric("Tingkat Konversi Subscriber (CR)", f"{cr:.2f}%")
        st.caption("Fokuskan evaluasi pada retensi detik 0–1 dan lonjakan klik subscribe di detik 3–6.")

    data = {k: x.get(k) for k in ["title", "hashtags", "hook", "story", "dialogue", "punchline", "ending", "flow_prompt", "thumbnail_prompt"]}
    st.download_button(
        "⬇️ Unduh Skrip & Prompt JSON",
        json.dumps(data, ensure_ascii=False, indent=2),
        "skit_subscriber_4beat.json",
        "application/json"
    )
