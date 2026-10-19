import os
import json
import random
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Global Shorts Studio", page_icon="🌎", layout="wide")
st.title("🌎 Global Shorts Studio (Anti-Repetisi & Auto Subtitles)")
st.caption("LOKALISASI BUDAYA OTOMATIS: HOOK → RESPON → TUDUHAN CTA → SKAKMAT PUNCHLINE")

CULTURAL_PRESETS = {
    "English": {
        "region_label": "United States / Global Western",
        "creatures": "Classic Hollywood Zombie, Horror Clown, Attic Phantom, or Alien Invader",
        "protagonist": "Suburban youth or gamer in casual hoodie/t-shirt",
        "setting": "Suburban bedroom, dark garage, basement with neon gamer lighting",
        "slang_tone": "Sharp internet slang ('Bro', 'Dude', 'Caught in 4K', 'Ain't no way')",
        "default_hook": "STOP! DON'T SCROLL!"
    },
    "Español (Spanish)": {
        "region_label": "Latin America / Spain",
        "creatures": "La Llorona, dramatic shrouded ghost, or gothic vampire",
        "protagonist": "Expressive young adult with animated hand gestures",
        "setting": "Colonial corridor, rustic courtyard, dim urban apartment",
        "slang_tone": "Rhythmic Spanish banter ('¡Oye tú!', '¡Párate ahí!', '¡No manches!')",
        "default_hook": "¡ALTO AHÍ! ¡NO HAGAS SCROLL!"
    },
    "日本語 (Japanese)": {
        "region_label": "Japan",
        "creatures": "Classic Yūrei (pale long-haired spirit) or urban legend ghost",
        "protagonist": "Expressive salaryman or university student",
        "setting": "Cramped Tokyo 1R tatami room or dim convenience store alley",
        "slang_tone": "Rapid dynamic banter ('おい！', 'ちょっと待って！', '嘘だろ？！')",
        "default_hook": "待って！スクロールするな！"
    },
    "한국어 (Korean)": {
        "region_label": "South Korea",
        "creatures": "Gwisin (pale ghost in white dress) or rooftop shadow entity",
        "protagonist": "Trendy young Korean in oversized streetwear",
        "setting": "Gosiwon room, rooftop room (oktapbang), stairwell",
        "slang_tone": "Punchy Seoul comedic banter ('야!', '잠깐만!', '대박')",
        "default_hook": "잠깐! 넘기지 마!"
    },
    "Português (Portuguese)": {
        "region_label": "Brazil / Portugal",
        "creatures": "Urban phantom, expressive zombie, humorous ghost",
        "protagonist": "High-energy youth with theatrical expressions",
        "setting": "Warm-toned urban living room or apartment balcony",
        "slang_tone": "Lively Brazilian slang ('Ei você!', 'Para tudo!', 'Qual é, mano!')",
        "default_hook": "PARA TUDO! NÃO PASSA O VÍDEO!"
    },
    "Bahasa Indonesia": {
        "region_label": "Indonesia",
        "creatures": "Sosok kuntilanak pucat, pocong komedi, atau hantu rumah tua",
        "protagonist": "Pemuda lokal berkaus santai dengan ekspresi kocak",
        "setting": "Rumah kayu tua, teras kontrakan malam hari, kamar kos",
        "slang_tone": "Bahasa gaul tongkrongan santai ('Woi!', 'Diem dulu!', 'Ketahuan lu!')",
        "default_hook": "STOP! JANGAN SCROLL!"
    }
}

DEFAULT_GLOBAL_PRESET = {
    "region_label": "Global Universal",
    "creatures": "Universal expressive monster or hooded phantom",
    "protagonist": "Relatable everyday person in modern casual wear",
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
        val = st.secrets.get("CLARIOHUB_API_KEY", "")
        if val:
            return str(val).strip()
    except Exception:
        pass
    return os.getenv("CLARIOHUB_API_KEY", "").strip()

def call_gemini(key, model, prompt):
    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=90.0, max_retries=1)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": (
                "You are an expert YouTube Shorts director specializing in globally viral comedy skits. "
                "Always generate unique, creative, non-repetitive premises tailored to target regions. "
                "Return valid JSON only."
            )},
            {"role": "user", "content": prompt},
        ],
        temperature=0.95,
        max_tokens=1800,
    )
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("API tidak mengembalikan respons.")
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        s, e = text.find("{"), text.rfind("}")
        if s >= 0 and e > s:
            data = json.loads(text[s:e + 1])
        else:
            raise RuntimeError("Respons model bukan format JSON valid.") from exc
    return data

def build_srt(dialogue_list):
    """Menghasilkan file subtitle standar SubRip (.srt) sesuai durasi 10 detik."""
    time_map = [
        ("00:00:00,000", "00:00:01,200"),
        ("00:00:01,200", "00:00:03,000"),
        ("00:00:03,000", "00:00:06,000"),
        ("00:00:06,000", "00:00:09,200")
    ]
    srt_lines = []
    for idx, d in enumerate(dialogue_list[:4], 1):
        start, end = time_map[idx - 1]
        line = d.get("line", "")
        speaker = d.get("speaker", "SPEAKER")
        srt_lines.append(f"{idx}\n{start} --> {end}\n{speaker}: {line}\n")
    return "\n".join(srt_lines)

def prompts(x, style, duration, language, cultural_info, text_mode):
    dialogue_items = [d for d in x.get("dialogue", []) if isinstance(d, dict)]
    dialogue = "\n".join(
        f'{d.get("time", "")} | {d.get("speaker", "CHAR")}: "{d.get("line", "")}"'
        for d in dialogue_items
    )

    if text_mode == "Video Bersih (Tanpa Teks AI - Edit di CapCut)":
        caption_rule = "- RESTRICTIONS: Clean visual footage, NO on-screen subtitles, NO text overlays, NO captions (captions will be added in post-production)."
    else:
        caption_rule = (
            "- ON-SCREEN TEXT & CAPTIONS: Burn-in kinetic, centered word-by-word subtitles matching spoken dialogue in real-time. "
            "Font: Bold modern sans-serif, high-contrast bright yellow with solid black outline. "
            "Highlight the first hook word aggressively in red/yellow flash."
        )

    x["flow_prompt"] = f"""Create ONE coherent {duration} vertical 9:16 {style} YouTube Short for {cultural_info['region_label']}.

VISUALS & ENVIRONMENT:
- Setting: {cultural_info['setting']}
- Character A (Instigator/Creature): {cultural_info['creatures']}
- Character B (Reactor): {cultural_info['protagonist']}

TITLE: {x.get('title', '')}
HOOK (0-1s): {x.get('hook', '')}
PREMISE: {x.get('story', '')}
PUNCHLINE: {x.get('punchline', '')}
ENDING: {x.get('ending', '')}

SCRIPT (STRICT SHOT-REVERSE-SHOT PACING):
{dialogue}

EDITING & SHOT BREAKDOWN:
- Shot 1 (0–1s) [Close-Up]: Character A aggressively addresses camera ({x.get('hook', '')}).
- Shot 2 (1–3s) [Medium]: Character B reacts defensively in native colloquial slang.
- Shot 3 (3–6s) [Close-Up]: Character A delivers the subscribe accusation straight into the lens.
- Shot 4 (6–9s) [Two-Shot / Medium-Wide]: Character B roasts Character A, laughing while Character A freezes in awkward embarrassment.

{caption_rule}

RESTRICTIONS: Photorealistic cinematic grade, natural lighting, sharp mobile readability, vertical 9:16 composition, seamless continuity across cuts."""

    x["thumbnail_prompt"] = f"""Viral 9:16 YouTube Shorts thumbnail for {cultural_info['region_label']}. Subject: {cultural_info['creatures']} staring into lens with extreme expression: {x.get('hook', '')}. Lighting: High-contrast chiaroscuro fitting {cultural_info['setting']}. Sharp mobile details, space left clean at bottom, no watermark."""
    x["srt_data"] = build_srt(dialogue_items)
    x.setdefault("hashtags", "#Shorts #Comedy #ViralSkit #Humor")
    return x

def local_idea(cultural_info):
    """Kumpulan template beragam agar judul dan cerita tidak macet di satu tema jika API offline."""
    pool = [
        {
            "title": "CAUGHT IN 4K NOT SUBSCRIBING! 😂",
            "hook": f"Creature blocks camera: '{cultural_info['default_hook']}'",
            "story": "Creature confronts viewer for binge-watching without subscribing, but gets roasted.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "CREATURE", "line": cultural_info['default_hook']},
                {"time": "00:01–00:03", "speaker": "HUMAN", "line": "Why are you screaming at me?!"},
                {"time": "00:03–00:06", "speaker": "CREATURE", "line": "I know your secret... watching daily without hitting subscribe!"},
                {"time": "00:06–00:09", "speaker": "HUMAN", "line": "Bro, you don't even have a channel! Hahaha!"}
            ],
            "punchline": "Human bursts into mocking laughter while creature freezes in shame.",
            "ending": "Creature lowers head in awkward silence.",
            "hashtags": "#Shorts #Comedy #FunnySkit"
        },
        {
            "title": "ZOMBIE WANTS SUBSCRIBERS?! 🧟‍♂️💀",
            "hook": "Zombie bangs screen: 'DON'T SWIPE AWAY!'",
            "story": "Zombie breaks into bedroom demanding subscribers instead of brains.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "ZOMBIE", "line": "DON'T SWIPE AWAY!"},
                {"time": "00:01–00:03", "speaker": "GAMER", "line": "Chill bro, don't eat my brain!"},
                {"time": "00:03–00:06", "speaker": "ZOMBIE", "line": "Forget brains! You watched 10 videos without subscribing!"},
                {"time": "00:06–00:09", "speaker": "GAMER", "line": "Bro, you've been dead for 200 years, why do you need an algorithm?!"}
            ],
            "punchline": "Gamer laughs uncontrollably as zombie looks down at his decayed hands.",
            "ending": "Zombie shrugs and shambles away.",
            "hashtags": "#Shorts #ZombieComedy #GamingHumor"
        },
        {
            "title": "ROBBER ASKS FOR SUBSCRIBE?! 💸🤣",
            "hook": "Intruder points aggressively: 'FREEZE! HANDS UP!'",
            "story": "A robber holds up a gamer but asks for YouTube subscribers instead of cash.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "ROBBER", "line": "FREEZE! HANDS UP!"},
                {"time": "00:01–00:03", "speaker": "VICTIM", "line": "Take my wallet, please!"},
                {"time": "00:03–00:06", "speaker": "ROBBER", "line": "Keep the cash! Hit the red subscribe button right now!"},
                {"time": "00:06–00:09", "speaker": "VICTIM", "line": "Wait, are you a burglar or an unpaid intern?! Hahaha!"}
            ],
            "punchline": "Victim laughs while robber frantically checks YouTube Studio on his phone.",
            "ending": "Robber sighs in defeat.",
            "hashtags": "#Shorts #Parody #ComedyShorts"
        }
    ]
    return random.choice(pool)

with st.sidebar:
    st.header("Pengaturan API")
    key = api_key()
    if not key:
        key = st.text_input("API Key ClarioHub", type="password").strip()
    st.write("ClarioHub API:", "✅ Key tersedia" if key else "⚠️ Masukkan API key")

    model_options = {
        "Gemini 3.7 Flash": "clario/gemini-3.7-flash",
        "DeepSeek V4 Pro": "clario/deepseek-v4-pro",
        "DeepSeek V4 Flash": "clario/deepseek-v4-flash",
        "GLM 5.3 Flash": "clario/glm-5.3-flash",
        "GPT 5.6 Sol": "clario/gpt-5.6-sol"
    }
    model = model_options[st.selectbox("Model AI", list(model_options.keys()), index=0)]
    st.divider()

    st.header("🎯 Target Negara & Audiens")
    lang_choice = st.selectbox("🌎 Bahasa & Budaya Target", LANGUAGES, index=0)
    target_language = st.text_input("Nama bahasa / Negara").strip() if lang_choice == "Bahasa lain (isi sendiri)" else lang_choice
    if not target_language:
        target_language = "English"

    cultural_info = CULTURAL_PRESETS.get(target_language, DEFAULT_GLOBAL_PRESET)

    st.info(f"**Target:** {cultural_info['region_label']}\n\n"
            f"**Karakter AI:** {cultural_info['creatures']}\n\n"
            f"**Setting:** {cultural_info['setting']}")

    st.header("🎬 Output Teks Video")
    text_mode = st.radio(
        "Mode Teks untuk Flow:",
        ["Video Bersih (Tanpa Teks AI - Edit di CapCut)", "Teks Kuning Otomatis AI di Video"],
        index=0,
        help="Pilih 'Video Bersih' jika ingin menempelkan subtitle via file .srt di CapCut agar teks tidak dobel."
    )

    style = st.selectbox("Gaya Visual", [
        "Horor-komedi realistis (Creature vs Human)",
        "Komedi absurd modern",
        "Parodi bioskop horor Barat",
        "Karakter bebas"
    ])
    duration = st.selectbox("Durasi", ["8 detik", "10 detik"], index=1)
    avoid = st.text_input("Hindari topik/karakter (opsional)")

if "idea" not in st.session_state:
    st.session_state.idea = None

if "history_titles" not in st.session_state:
    st.session_state.history_titles = []

if st.button("🔥 GENERATE SKRIP BARU (ANTI-MONOTON)", type="primary", use_container_width=True):
    history_context = ", ".join(f'"{t}"' for t in st.session_state.history_titles[-6:]) or "None"

    prompt = f"""Create ONE completely original, brand-new 8-10 second vertical YouTube Shorts comedy skit tailored for {cultural_info['region_label']}.
OUTPUT LANGUAGE: {target_language}. All fields in natural colloquial {target_language}.

CREATIVE ANTI-REPETITION MANDATE:
- RECENT TITLES GENERATED: [{history_context}]
- You MUST create a DIFFERENT situation, setup, and catchy viral title every time. Do NOT repeat or slightly alter recent titles.
- Explore varied comic setups: midnight fridge raid, alien abduction, workout session, gamer rage, bank robbery parody, parking ticket, etc.

CULTURAL MANDATE:
- Region: {cultural_info['region_label']}
- Creature/Instigator: {cultural_info['creatures']}
- Protagonist: {cultural_info['protagonist']}
- Setting: {cultural_info['setting']}
- Slang: {cultural_info['slang_tone']}

BEAT PACING:
1. HOOK (00:00–00:01): Creature aggressively halts camera with a sharp command (e.g. 'STOP!', 'FREEZE!', 'HOLD UP!', 'DON'T SCROLL!'). Vary the opening word.
2. REACTION (00:01–00:03): Human reacts with defensive, confused native slang.
3. ACCUSATION (00:03–00:06): Creature points to camera, accusing viewer/human of watching without hitting subscribe.
4. ROAST PUNCHLINE (00:06–00:09): Human roasts creature back with a witty logic twist, laughing while creature freezes in embarrassment.

Return valid JSON only with keys: title, hook, story, dialogue (array of 4 objects with time, speaker, line), punchline, ending, hashtags, cta_note."""

    try:
        if not key:
            raise RuntimeError("Masukkan API Key ClarioHub di sidebar.")
        result = call_gemini(key, model.strip(), prompt)
        st.session_state.idea = prompts(result, style, duration, target_language, cultural_info, text_mode)
        title = result.get("title", "")
        if title:
            st.session_state.history_titles.append(title)
            st.session_state.history_titles = st.session_state.history_titles[-10:]
    except Exception as e:
        st.error(f"Gagal generate API: {e}")
        st.warning("Memuat template cadangan acak...")
        st.session_state.idea = prompts(local_idea(cultural_info), style, duration, target_language, cultural_info, text_mode)

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title", "Ide Shorts"))
    st.code(x.get("hashtags", "#Shorts #Comedy #Funny"))

    t1, t2, t3, t4 = st.tabs(["Struktur Skit", "Prompt Video Flow", "File Subtitle (.SRT)", "Thumbnail"])

    with t1:
        st.markdown("**1. HOOK 1 DETIK**"); st.write(x.get("hook", ""))
        st.markdown("**2. PREMIS & SETTING**"); st.write(x.get("story", ""))
        st.markdown("**3. DIALOG LENGKAP**")
        for d in x.get("dialogue", []):
            if isinstance(d, dict):
                st.write(f"⏱️ **{d.get('time', '')} | {d.get('speaker', '')}** : \"{d.get('line', '')}\"")
        st.markdown("**4. PUNCHLINE SKAKMAT**"); st.write(x.get("punchline", ""))
        st.markdown("**5. ENDING**"); st.write(x.get("ending", ""))

    with t2:
        st.caption(f"Prompt Google Flow (Mode: {text_mode}):")
        st.text_area("Prompt Video Flow", x.get("flow_prompt", ""), height=330)

    with t3:
        st.caption("File .SRT siap impor ke CapCut agar teks 100% presisi dan tidak typo:")
        st.text_area("Isi File Subtitle (.srt)", x.get("srt_data", ""), height=200)
        st.download_button(
            "⬇️ Unduh File Subtitle (.srt)",
            x.get("srt_data", ""),
            file_name="shorts_captions.srt",
            mime="text/plain"
        )

    with t4:
        st.caption("Prompt Thumbnail 9:16:")
        st.text_area("Prompt Thumbnail", x.get("thumbnail_prompt", ""), height=200)

    data = {k: x.get(k) for k in ["title", "hashtags", "hook", "story", "dialogue", "punchline", "ending", "flow_prompt", "srt_data", "thumbnail_prompt"]}
    st.download_button(
        "⬇️ Unduh Paket Lengkap JSON",
        json.dumps(data, ensure_ascii=False, indent=2),
        "global_shorts_package.json",
        "application/json"
    )
