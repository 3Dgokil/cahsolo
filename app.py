import os
import json
import random
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Global Shorts Studio", page_icon="🌎", layout="wide")
st.title("🌎 Global Shorts Studio (Dynamic CTA & Creative Plots)")
st.caption("PREMIS BEBAS VARIATIF → HOOK 1 DETIK → KONFLIK 4-BEAT → CTA DINAMIS")

CULTURAL_PRESETS = {
    "English": {
        "region_label": "United States / Global Western",
        "creatures": "Classic Hollywood Zombie, Horror Clown, Attic Phantom, Alien Invader, or Creepy Neighbor",
        "protagonist": "Suburban teenager, gamer, or night-shift worker",
        "setting": "Suburban bedroom, dark basement, 24/7 convenience store, or misty garage",
        "slang_tone": "Sharp internet slang ('Bro', 'Dude', 'Caught in 4K', 'Ain't no way', 'Lock in')",
        "default_hook": "STOP! DON'T SCROLL!"
    },
    "Español (Spanish)": {
        "region_label": "Latin America / Spain",
        "creatures": "La Llorona, dramatic shrouded ghost, mischievous goblin, or gothic vampire",
        "protagonist": "Expressive young adult with animated body language",
        "setting": "Colonial corridor, rustic kitchen at midnight, or dim apartment hallway",
        "slang_tone": "Rhythmic Spanish comedic banter ('¡Oye tú!', '¡Párate ahí!', '¡No manches!', '¡Qué susto!')",
        "default_hook": "¡ALTO AHÍ! ¡NO HAGAS SCROLL!"
    },
    "日本語 (Japanese)": {
        "region_label": "Japan",
        "creatures": "Classic Yūrei, Oni, mischievous Yokai, or bizarre urban entity",
        "protagonist": "Tired salaryman, anime fan, or university student",
        "setting": "Cramped Tokyo 1R tatami room, dark train platform, or narrow back alley",
        "slang_tone": "Manzai boke-tsukkomi rapid comedic timing ('おい！', 'ちょっと待って！', '嘘だろ？！')",
        "default_hook": "待って！スクロールするな！"
    },
    "한국어 (Korean)": {
        "region_label": "South Korea",
        "creatures": "Gwisin in white dress, rooftop shadow creature, or bizarre ghost",
        "protagonist": "Trendy young Korean in oversized streetwear or internet cafe gamer",
        "setting": "PC bang, rooftop room (oktapbang), gosiwon, or dimly lit stairwell",
        "slang_tone": "Punchy Seoul conversational slang ('야!', '잠깐만!', '대박', '헐')",
        "default_hook": "잠깐! 넘기지 마!"
    },
    "Português (Portuguese)": {
        "region_label": "Brazil / Portugal",
        "creatures": "Urban phantom, expressive zombie, or funny mythical creature",
        "protagonist": "High-energy youth with loud theatrical gestures",
        "setting": "Warm-toned living room, messy bedroom, or urban backyard",
        "slang_tone": "Lively Brazilian slang ('Ei você!', 'Para tudo!', 'Qual é, mano!', 'Caramba')",
        "default_hook": "PARA TUDO! NÃO PASSA O VÍDEO!"
    },
    "Bahasa Indonesia": {
        "region_label": "Indonesia",
        "creatures": "Kuntilanak, pocong absurd, genderuwo nyasar, atau hantu kosan",
        "protagonist": "Anak kosan, pemuda tongkrongan santai, atau gamer malam",
        "setting": "Kamar kos remang, teras kontrakan malam hari, atau pos ronda",
        "slang_tone": "Bahasa gaul tongkrongan ('Woi!', 'Diem dulu!', 'Gokil', 'Kena lu!')",
        "default_hook": "STOP! JANGAN SCROLL!"
    }
}

DEFAULT_GLOBAL_PRESET = {
    "region_label": "Global Universal",
    "creatures": "Universal expressive monster, alien, or hooded phantom",
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

CTA_STYLE_DESCRIPTIONS = {
    "🎲 Acak Otomatis (Random)": "Pilih secara acak dari variasi taruhan, panik, suap, tuduhan, atau cliffhanger agar cerita selalu berganti.",
    "🏆 Taruhan / Syarat": "Karakter menantang penonton (misal: 'Kalau lu kaget atau ketawa, wajib pencet subscribe!').",
    "😱 Ancaman Lucu / Panik": "Karakter ketakutan atau heboh minta bantuan (misal: 'Pencet subscribe cepetan biar pintunya kekunci!').",
    "🤝 Permintaan Maaf / Suap": "Karakter ketahuan berbuat konyol/salah (misal: 'Ampun bro! Sebagai gantinya subscribe channel ini deh!').",
    "⏳ Gantung / Cliffhanger": "Karakter menghentikan momen kritis di akhir (misal: 'Mau liat kelanjutannya? Subscribe buat Part 2!').",
    "👀 Tuduhan Konyol": "Karakter menuduh penonton dengan fakta receh (misal: 'Ketahuan mantengin doang tapi tombol merahnya anggurin!')."
}

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
                "You are an elite YouTube Shorts director specializing in viral 4-beat comedy skits. "
                "You create highly original, unpredictable situations. "
                "Always follow cultural constraints and return valid JSON only."
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
        caption_rule = "- RESTRICTIONS: Clean visual footage, NO on-screen subtitles, NO text overlays, NO captions."
    else:
        caption_rule = (
            "- ON-SCREEN TEXT & CAPTIONS: Burn-in kinetic, centered word-by-word subtitles matching spoken dialogue in real-time. "
            "Font: Bold modern sans-serif, high-contrast bright yellow with solid black outline. "
            "Highlight the first hook word aggressively in red/yellow flash."
        )

    x["flow_prompt"] = f"""Create ONE coherent {duration} vertical 9:16 {style} YouTube Short for {cultural_info['region_label']}.

VISUALS & ENVIRONMENT:
- Setting: {cultural_info['setting']}
- Character A: {cultural_info['creatures']}
- Character B: {cultural_info['protagonist']}

TITLE: {x.get('title', '')}
HOOK (0-1s): {x.get('hook', '')}
PREMISE: {x.get('story', '')}
PUNCHLINE: {x.get('punchline', '')}
ENDING: {x.get('ending', '')}

SCRIPT (STRICT SHOT-REVERSE-SHOT PACING):
{dialogue}

EDITING & SHOT BREAKDOWN:
- Shot 1 (0–1s) [Close-Up]: Character A aggressively halts camera ({x.get('hook', '')}).
- Shot 2 (1–3s) [Medium]: Character B reacts defensively in native colloquial slang.
- Shot 3 (3–6s) [Close-Up]: Contextual subscribe callout tied organically to the plot.
- Shot 4 (6–9s) [Two-Shot / Medium-Wide]: Final roast or twist punchline, laughing or dramatic freeze.

{caption_rule}

RESTRICTIONS: Photorealistic cinematic grade, vertical 9:16 framing, seamless continuity across cuts."""

    x["thumbnail_prompt"] = f"""Viral 9:16 YouTube Shorts thumbnail for {cultural_info['region_label']}. Subject: {cultural_info['creatures']} staring into lens with extreme expression: {x.get('hook', '')}. Lighting: High-contrast chiaroscuro fitting {cultural_info['setting']}. Sharp mobile details, space left clean at bottom, no watermark."""
    x["srt_data"] = build_srt(dialogue_items)
    x.setdefault("hashtags", "#Shorts #Comedy #ViralSkit #Humor")
    return x

def local_idea(cultural_info, chosen_cta):
    pool = [
        {
            "title": "ZOMBIE STEALS WIFI PASSWORD?! 🧟‍♂️📡",
            "hook": "Zombie bangs on screen: 'HOLD UP! DON'T SWIPE!'",
            "story": "A zombie sneaks into a room not to eat brains, but to get the WiFi password and demand subscribers.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "ZOMBIE", "line": "HOLD UP! DON'T SWIPE!"},
                {"time": "00:01–00:03", "speaker": "GAMER", "line": "Bro, what are you doing in my room?!"},
                {"time": "00:03–00:06", "speaker": "ZOMBIE", "line": "Give me the WiFi password or hit subscribe right now!"},
                {"time": "00:06–00:09", "speaker": "GAMER", "line": "You've been buried for a century, why do you need 5G?! Hahaha!"}
            ],
            "punchline": "Gamer bursts out laughing as the zombie stares awkwardly at his decayed hands.",
            "ending": "Zombie slumps in defeat.",
            "hashtags": "#Shorts #ZombieComedy #GamingHumor"
        },
        {
            "title": "THE MIDNIGHT FRIDGE MONSTER 🍕👻",
            "hook": "Creature holding pizza slice shouts: 'CAUGHT IN 4K!'",
            "story": "A basement ghost gets caught eating leftover pizza and tries to bribe the homeowner.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "GHOST", "line": "CAUGHT IN 4K!"},
                {"time": "00:01–00:03", "speaker": "TENANT", "line": "Wait, you're the one eating my leftovers?!"},
                {"time": "00:03–00:06", "speaker": "GHOST", "line": "Don't evict me! Just subscribe to the channel and I'll buy more pizza!"},
                {"time": "00:06–00:09", "speaker": "TENANT", "line": "With what money? You've been dead since 1980! Hahaha!"}
            ],
            "punchline": "Tenant laughs while ghost hides the empty pizza box behind its back.",
            "ending": "Ghost floats away in embarrassment.",
            "hashtags": "#Shorts #GhostPrank #MidnightSnack"
        },
        {
            "title": "THE LAZY EXORCIST CHALLENGE 🕯️😂",
            "hook": "Vampire points at camera: 'BET YOU CAN'T SCROLL!'",
            "story": "A vampire makes a high-stakes comedy bet with the viewer.",
            "dialogue": [
                {"time": "00:00–00:01", "speaker": "VAMPIRE", "line": "BET YOU CAN'T SCROLL!"},
                {"time": "00:01–00:03", "speaker": "HUMAN", "line": "Are you trying to hypnotize me?!"},
                {"time": "00:03–00:06", "speaker": "VAMPIRE", "line": "If you laughed or flinched, you legally owe this channel a subscribe!"},
                {"time": "00:06–00:09", "speaker": "HUMAN", "line": "I'm not laughing, your plastic fangs are falling out! Hahaha!"}
            ],
            "punchline": "Human points and laughs while vampire frantically adjusts loose plastic fangs.",
            "ending": "Vampire hides his face in shame.",
            "hashtags": "#Shorts #VampireHumor #ComedyChallenge"
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
        "GPT 5.6 Sol": "clario/gpt-5.6-sol",
        "DeepSeek V4 Pro": "clario/deepseek-v4-pro",
        "DeepSeek V4 Flash": "clario/deepseek-v4-flash",
        "GLM 5.3 Flash": "clario/glm-5.3-flash"
    }
    model = model_options[st.selectbox("Model AI", list(model_options.keys()), index=0)]
    st.divider()

    st.header("🎯 Target Budaya & Bahasa")
    lang_choice = st.selectbox("🌎 Bahasa Target", LANGUAGES, index=0)
    target_language = st.text_input("Nama bahasa / Negara").strip() if lang_choice == "Bahasa lain (isi sendiri)" else lang_choice
    if not target_language:
        target_language = "English"

    cultural_info = CULTURAL_PRESETS.get(target_language, DEFAULT_GLOBAL_PRESET)

    st.info(f"**Target:** {cultural_info['region_label']}\n\n"
            f"**Karakter:** {cultural_info['creatures']}\n\n"
            f"**Setting:** {cultural_info['setting']}")

    st.header("💡 Format Ajakan Subscribe (CTA)")
    cta_choice = st.selectbox("Gaya Ajakan Subscribe:", list(CTA_STYLE_DESCRIPTIONS.keys()), index=0)
    st.caption(CTA_STYLE_DESCRIPTIONS[cta_choice])

    st.header("🎬 Output Teks Video")
    text_mode = st.radio(
        "Mode Teks untuk Flow:",
        ["Video Bersih (Tanpa Teks AI - Edit di CapCut)", "Teks Kuning Otomatis AI di Video"],
        index=0
    )

    style = st.selectbox("Gaya Visual", [
        "Horor-komedi realistis (Creature vs Human)",
        "Komedi absurd perkotaan",
        "Parodi sci-fi / alien kocak",
        "Karakter bebas"
    ])
    duration = st.selectbox("Durasi", ["8 detik", "10 detik"], index=1)

# Area input ide cerita manual di layar utama
st.subheader("📝 Ide / Topik Cerita (Opsional)")
user_premise = st.text_input(
    "Masukkan tema atau situasi konyol yang Anda inginkan:",
    placeholder="Contoh: Hantu minjem charger HP, zombie numpang pesan gofood, alien kaget liat token listrik...",
    help="Jika dikosongkan, AI akan membuat situasi komedi acak yang segar secara otomatis."
)

if "idea" not in st.session_state:
    st.session_state.idea = None

if "history_titles" not in st.session_state:
    st.session_state.history_titles = []

if st.button("🔥 GENERATE SKRIP BARU & SEGAR", type="primary", use_container_width=True):
    history_context = ", ".join(f'"{t}"' for t in st.session_state.history_titles[-6:]) or "None"

    if cta_choice == "🎲 Acak Otomatis (Random)":
        selected_cta_instruction = random.choice([
            "CTA STYLE: BET / CHALLENGE ('If you laughed, you owe a subscribe!')",
            "CTA STYLE: PANIC / SUDDEN THREAT ('Hit subscribe quick before the door locks!')",
            "CTA STYLE: BRIBE / APOLOGY ('I'm sorry! Just subscribe and don't tell anyone!')",
            "CTA STYLE: CLIFFHANGER ('Subscribe now for Part 2 disaster!')",
            "CTA STYLE: CAUGHT IN THE ACT ('Binge-watching without clicking subscribe!')"
        ])
    else:
        selected_cta_instruction = f"CTA STYLE: {cta_choice.upper()} - {CTA_STYLE_DESCRIPTIONS[cta_choice]}"

    user_premise_instruction = f"MANDATORY USER PREMISE: {user_premise}" if user_premise.strip() else "USER PREMISE: Invent a fresh, unpredictable comedic confrontation."

    prompt = f"""Create ONE completely original, hilarious 8-10 second vertical YouTube Shorts comedy skit tailored for {cultural_info['region_label']}.
OUTPUT LANGUAGE: {target_language}. All dialogue, title, hook, and punchline must be in natural colloquial {target_language}.

PREMISE & UNIQUENESS MANDATE:
- {user_premise_instruction}
- RECENT TITLES GENERATED: [{history_context}]
- AVOID REPETITION: Do NOT repeat identical jokes, same roast lines, or identical setups.
- Tone: Punchy internet humor, viral pacing, memorable banter.

CULTURAL MANDATE:
- Region: {cultural_info['region_label']}
- Creature/Instigator: {cultural_info['creatures']}
- Protagonist: {cultural_info['protagonist']}
- Setting: {cultural_info['setting']}
- Slang: {cultural_info['slang_tone']}

CTA INTEGRATION RULE:
- {selected_cta_instruction}
- Weave the subscribe callout NATURALLY into Beat 3 or Beat 4 as part of the joke.

STRUCTURAL 4-BEAT PACING:
1. BEAT 1 - THE HOOK (00:00–00:01): Creature aggressively halts the camera (1-3 words max, e.g. 'STOP!', 'FREEZE!', 'HOLD UP!', 'DON'T SCROLL!').
2. BEAT 2 - THE REACTION (00:01–00:03): Human reacts defensively in native colloquial slang.
3. BEAT 3 - THE TWIST / CTA (00:03–00:06): The absurd request / subscribe callout emerges.
4. BEAT 4 - THE PUNCHLINE ROAST (00:06–00:09): The other character roasts back with hilarious reality check, ending in laughter or awkward shock.

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
        st.warning("Memuat ide cadangan...")
        st.session_state.idea = prompts(local_idea(cultural_info, cta_choice), style, duration, target_language, cultural_info, text_mode)

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title", "Ide Shorts"))
    st.code(x.get("hashtags", "#Shorts #Comedy #Funny"))

    t1, t2, t3, t4 = st.tabs(["Struktur Skit", "Prompt Video Flow", "File Subtitle (.SRT)", "Thumbnail"])

    with t1:
        st.markdown("**1. HOOK 1 DETIK**"); st.write(x.get("hook", ""))
        st.markdown("**2. PREMIS & ALUR**"); st.write(x.get("story", ""))
        st.markdown("**3. DIALOG LENGKAP**")
        for d in x.get("dialogue", []):
            if isinstance(d, dict):
                st.write(f"⏱️ **{d.get('time', '')} | {d.get('speaker', '')}** : \"{d.get('line', '')}\"")
        st.markdown("**4. PUNCHLINE SKAKMAT**"); st.write(x.get("punchline", ""))
        st.markdown("**5. REAKSI ENDING**"); st.write(x.get("ending", ""))

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
