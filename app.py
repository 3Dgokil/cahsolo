import os
import json
import random
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Global Shorts Subscriber Studio", page_icon="🌎", layout="wide")
st.title("🌎 Global Shorts Subscriber Studio")
st.caption("LOKALISASI BUDAYA OTOMATIS: HOOK → RESPON → TUDUHAN CTA → SKAKMAT PUNCHLINE")

# Database Lokalisasi Visual & Karakter Berdasarkan Bahasa/Target Negara
CULTURAL_PRESETS = {
    "English": {
        "region_label": "United States / Global Western",
        "creatures": "Classic Hollywood Zombie, Creepy Attic Ghost, Horror Clown, or Suburban Shadow Monster",
        "protagonist": "Suburban teenager or young adult in casual hoodie/t-shirt",
        "setting": "Suburban bedroom, dark garage, or basement with neon gamer lighting",
        "slang_tone": "Sharp conversational slang (e.g., 'Bro', 'Dude', 'Caught red-handed')",
        "default_hook": "STOP! DON'T SCROLL!"
    },
    "Español (Spanish)": {
        "region_label": "Latin America / Spain",
        "creatures": "La Llorona, dramatic shrouded ghost, or gothic vampire",
        "protagonist": "Expressive young man/woman with exaggerated hand gestures",
        "setting": "Colonial corridor, rustic courtyard, or dimly lit urban living room",
        "slang_tone": "Expressive, rhythmic Spanish comedic banter ('¡Oye tú!', '¡Párate ahí!')",
        "default_hook": "¡ALTO AHÍ! ¡NO HAGAS SCROLL!"
    },
    "日本語 (Japanese)": {
        "region_label": "Japan",
        "creatures": "Classic Yūrei (Sadako-style pale spirit), Oni, or bizarre urban legend apparition",
        "protagonist": "Overworked salaryman or expressive Japanese student",
        "setting": "Cramped Tokyo 1R tatami apartment or dim convenience store alley",
        "slang_tone": "Manzai style boke-tsukkomi rapid dynamic dialogue ('おい！', 'ちょっと待って！')",
        "default_hook": "待って！スクロールするな！"
    },
    "한국어 (Korean)": {
        "region_label": "South Korea",
        "creatures": "Gwisin (pale ghost in white hanbok or school uniform) or creepy modern apparition",
        "protagonist": "Trendy young Korean in oversized streetwear",
        "setting": "Gosiwon room, rooftop room (oktapbang), or neon-lit stairwell",
        "slang_tone": "Punchy modern Seoul comedic banter ('야!', '잠깐만!')",
        "default_hook": "잠깐! 넘기지 마!"
    },
    "Português (Portuguese)": {
        "region_label": "Brazil / Portugal",
        "creatures": "Urban phantom, exaggerated zombie, or humorous haunting entity",
        "protagonist": "High-energy Brazilian reacting with loud theatrical expressions",
        "setting": "Warm-toned urban living room or backyard with fairy lights",
        "slang_tone": "Lively, colloquial Brazilian energy ('Ei você!', 'Para tudo!')",
        "default_hook": "PARA TUDO! NÃO PASSA O VÍDEO!"
    },
    "Bahasa Indonesia": {
        "region_label": "Indonesia",
        "creatures": "Sosok kuntilanak pucat, pocong komedi, atau hantu rumah tua",
        "protagonist": "Pemuda lokal berkaus santai dengan ekspresi kocak",
        "setting": "Rumah kayu tua, teras kontrakan malam hari, atau kamar kos",
        "slang_tone": "Bahasa gaul tongkrongan santai ('Woi!', 'Diem dulu!', 'Ketahuan lu!')",
        "default_hook": "STOP! JANGAN SCROLL!"
    }
}

DEFAULT_GLOBAL_PRESET = {
    "region_label": "Global Universal",
    "creatures": "Universal expressive monster, comic zombie, or hooded phantom",
    "protagonist": "Relatable everyday young person in modern casual wear",
    "setting": "Dimly lit modern apartment room",
    "slang_tone": "Punchy native colloquial expressions",
    "default_hook": "WAIT! DON'T SWIPE!"
}

LANGUAGES = list(CULTURAL_PRESETS.keys()) + [
    "Français (French)", "Deutsch (German)", "Italiano (Italian)", "العربية (Arabic)",
    "हिन्दी (Hindi)", "Русский (Russian)", "Türkçe (Turkish)", "ไทย (Thai)",
    "Tiếng Việt (Vietnamese)", "Bahasa Melayu (Malay)", "Bahasa lain (isi sendiri)"
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
                "You are an elite YouTube Shorts director specializing in globally viral, "
                "culturally authentic comedy skits. You adapt visuals, characters, folklore, "
                "and slang strictly to the viewer's target culture. Return valid JSON only."
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

def prompts(x, style, duration, language, cultural_info):
    """Menyusun prompt Flow & Thumbnail yang dikunci ke elemen visual target negara."""
    dialogue_items = [d for d in x.get("dialogue", []) if isinstance(d, dict)]
    dialogue = "\n".join(
        f'{d.get("time", "")} | {d.get("speaker", "CHARACTER")}: "{d.get("line", "")}"'
        for d in dialogue_items
    )

    x["flow_prompt"] = f"""Create ONE coherent, photorealistic {duration} vertical 9:16 YouTube Short skit tailored for {cultural_info['region_label']} audiences.

VISUAL STYLE & CULTURAL CONTEXT:
- Genre: {style}
- Target Setting: {cultural_info['setting']}
- Character A (Instigator/Creature): {cultural_info['creatures']}
- Character B (Reactor): {cultural_info['protagonist']}

TITLE: {x.get('title', '')}
HOOK (0-1s): {x.get('hook', '')}
PREMISE: {x.get('story', '')}
PUNCHLINE: {x.get('punchline', '')}
ENDING: {x.get('ending', '')}

DIALOGUE SCRIPT (STRICT TIMING & LIP-SYNC):
{dialogue}

EDITING & SHOT BREAKDOWN (PUNCHY GLOBAL SKIT PACING):
- Shot 1 (0–1s) [Extreme Close-Up]: Character A aggressively halts the viewer, staring directly into the lens. Instant universal pattern interrupt.
- Shot 2 (1–3s) [Medium Shot Cut]: Character B flinches back in confusion, matching culturally natural gestures.
- Shot 3 (3–6s) [Close-Up Cut]: Character A points into the camera, delivering the viral subscribe callout with dynamic comedic intensity.
- Shot 4 (6–9s) [Two-Shot / Medium-Wide Cut]: Character B delivers the reality-check roast punchline, laughing loudly while Character A freezes in awkward defeat.

CINEMATOGRAPHY & RESTRICTIONS:
- Authentic cultural styling (wardrobe, architecture, lighting) fitting {cultural_info['region_label']}.
- Photorealistic cinematic grade, vertical 9:16 composition.
- Seamless character continuity across cuts. No subtitles, no watermarks, no glitchy artifacts."""

    x["thumbnail_prompt"] = f"""Create a viral, high-contrast vertical 9:16 YouTube Shorts thumbnail targeting {cultural_info['region_label']}. Subject: {cultural_info['creatures']} breaking the 4th wall, staring directly into lens with extreme expression: {x.get('hook', '')}. Lighting: Cinematic high-contrast chiaroscuro fitting {cultural_info['setting']}. Sharp mobile-screen readability. Space left clean at bottom. No text overlays, no watermarks."""
    x.setdefault("hashtags", "#Shorts #Comedy #ViralSkit #Humor")
    return x

def local_idea(cultural_info):
    return {
        "title": "NO CHANNEL, NO EXCUSE! 😂",
        "hook": f"Creature confronts camera: '{cultural_info['default_hook']}'",
        "story": "Creature confronts the viewer for watching without subscribing, but gets roasted instantly.",
        "dialogue": [
            {"time": "00:00–00:01", "speaker": "CREATURE", "line": cultural_info['default_hook']},
            {"time": "00:01–00:03", "speaker": "HUMAN", "line": "Why you screaming at me?!"},
            {"time": "00:03–00:06", "speaker": "CREATURE", "line": "I know your dirty secret... watching everyday without subscribing!"},
            {"time": "00:06–00:09", "speaker": "HUMAN", "line": "Bro, you don't even have a YouTube channel! Hahaha!"}
        ],
        "punchline": "Human bursts into mocking laughter while the creature freezes in sheer embarrassment.",
        "ending": "Creature lowers head in awkward silence.",
        "hashtags": "#Shorts #Comedy #FunnySkit"
    }

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

    st.header("🎯 Target Negara & Audiens")
    language_choice = st.selectbox("🌎 Bahasa & Budaya Target", LANGUAGES, index=0)
    if language_choice == "Bahasa lain (isi sendiri)":
        custom_language = st.text_input("Nama bahasa / Negara", placeholder="Contoh: German, Thai, Italian")
        target_language = custom_language.strip() or "English"
    else:
        target_language = language_choice

    # Ambil data kultur otomatis berdasarkan bahasa yang dipilih
    cultural_info = CULTURAL_PRESETS.get(target_language, DEFAULT_GLOBAL_PRESET)

    st.info(f"**Target Wilayah:** {cultural_info['region_label']}\n\n"
            f"**Karakter AI:** {cultural_info['creatures']}\n\n"
            f"**Setting:** {cultural_info['setting']}")

    style = st.selectbox("Gaya Visual", [
        "Horor-komedi realistis (Universal Creature vs Human)",
        "Komedi absurd perkotaan realistis",
        "Parodi bioskop horor Barat",
        "Karakter bebas"
    ])
    duration = st.selectbox("Durasi (Google Flow)", ["8 detik", "10 detik"], index=1)
    avoid = st.text_input("Hindari topik/karakter (opsional)")

if "idea" not in st.session_state:
    st.session_state.idea = None

if st.button("🔥 GENERATE GLOBAL SKIT 4-BEAT", type="primary", use_container_width=True):
    prompt = f"""Create ONE original 8-10 second vertical YouTube Shorts comedy skit tailored for {cultural_info['region_label']} audiences.
OUTPUT LANGUAGE: {target_language}. All dialogue, title, hook, story, punchline, ending, and notes must be in natural colloquial {target_language}.

CULTURAL & VISUAL LOCALIZATION MANDATE:
- Target Region: {cultural_info['region_label']}
- Creature/Instigator: {cultural_info['creatures']}
- Protagonist: {cultural_info['protagonist']}
- Setting: {cultural_info['setting']}
- Dialogue Tone: {cultural_info['slang_tone']} (MUST sound like native internet humor, NOT translated text).

STRUCTURAL BLUEPRINT (Strict 4-beat pacing):
1. BEAT 1 - THE HOOK (00:00–00:01): Creature aggressively confronts camera directly with a sudden, punchy command/shout (1-3 words max, e.g., similar to '{cultural_info['default_hook']}'). Do NOT repeat the exact same word every time.
2. BEAT 2 - THE REACTION (00:01–00:03): Human reacts with defensive, confused colloquial slang.
3. BEAT 3 - THE CTA ACCUSATION (00:03–00:06): Creature breaks fourth-wall, pointing at screen and accusing the viewer/human of binge-watching without hitting subscribe.
4. BEAT 4 - THE PUNCHLINE ROAST (00:06–00:09): Human roasts creature back with an undeniable logic twist (e.g. creature having no channel, dead internet, etc.), bursting into laughter while creature freezes in shame.

DIALOGUE REQUIREMENTS:
- Exactly 4 rapid dialogue lines for the 4 beats.
- Highly authentic native slang and comedic cadence.

Return valid JSON only with keys: title, hook, story, dialogue (array of 4 objects with time, speaker, line), punchline, ending, hashtags, cta_note."""

    try:
        if not key:
            raise RuntimeError("Masukkan API Key ClarioHub di sidebar.")
        result = call_gemini(key, model.strip(), prompt)
        st.session_state.idea = prompts(result, style, duration, target_language, cultural_info)
    except Exception as e:
        st.error(f"Gagal generate via API: {e}")
        st.warning("Memuat template cadangan global...")
        st.session_state.idea = prompts(local_idea(cultural_info), style, duration, target_language, cultural_info)

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title", "Ide Shorts Global"))
    st.code(x.get("hashtags", "#Shorts #Comedy #Funny"))

    t1, t2, t3, t4 = st.tabs(["Struktur Skit Terlokalisasi", "Prompt Google Flow (Visual Target)", "Prompt Thumbnail", "Evaluasi Subscriber"])

    with t1:
        st.markdown("**1. HOOK BUDAYA TARGET (0–1s)**")
        st.write(x.get("hook", ""))

        st.markdown("**2. SETTING & PREMIS LOKAL**")
        st.write(x.get("story", ""))

        st.markdown("**3. DIALOG ASLI NATIVE**")
        for d in x.get("dialogue", []):
            if isinstance(d, dict):
                st.write(f"⏱️ **{d.get('time', '')} | {d.get('speaker', '')}** : \"{d.get('line', '')}\"")

        st.markdown("**4. PUNCHLINE SKAKMAT (6–9s)**")
        st.write(x.get("punchline", ""))

        st.markdown("**5. REAKSI ENDING**")
        st.write(x.get("ending", ""))

    with t2:
        st.caption("Prompt Google Flow (otomatis mengunci karakter, kostum, dan setting negara target):")
        st.text_area("Salin Prompt Video Flow", x.get("flow_prompt", ""), height=350)

    with t3:
        st.caption("Prompt Thumbnail yang disesuaikan dengan estetika visual global:")
        st.text_area("Salin Prompt Thumbnail", x.get("thumbnail_prompt", ""), height=220)

    with t4:
        col1, col2, col3 = st.columns(3)
        views = col1.number_input("Views Video Global", min_value=0, step=100)
        subs = col2.number_input("Subscriber Baru", min_value=0, step=1)
        retention = col3.number_input("Average Percentage Viewed (%)", 0.0, 100.0, step=0.5)
        if views > 0:
            cr = (subs / views) * 100
            st.metric("Tingkat Konversi Subscriber (CR)", f"{cr:.2f}%")
        st.caption("Untuk audiens global, pastikan retensi detik 0–1 di atas 80% agar algoritma mendorong ke negara target.")

    data = {k: x.get(k) for k in ["title", "hashtags", "hook", "story", "dialogue", "punchline", "ending", "flow_prompt", "thumbnail_prompt"]}
    st.download_button(
        "⬇️ Unduh Paket Ide Terlokalisasi JSON",
        json.dumps(data, ensure_ascii=False, indent=2),
        "global_shorts_localized.json",
        "application/json"
    )
