import os
import json
import random
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Shorts Subscriber Studio", page_icon="🔥", layout="wide")
st.title("🔥 Shorts Subscriber Studio")
st.caption("DILIHAT → BERTAHAN → KEMBALI | Fokus: mencari subscriber")

LANGUAGES = [
    "Bahasa Indonesia", "English", "Español (Spanish)", "Português (Portuguese)",
    "Français (French)", "Deutsch (German)", "Italiano (Italian)", "日本語 (Japanese)",
    "한국어 (Korean)", "中文简体 (Chinese Simplified)", "中文繁體 (Chinese Traditional)",
    "العربية (Arabic)", "हिन्दी (Hindi)", "বাংলা (Bengali)", "اردو (Urdu)",
    "Русский (Russian)", "Türkçe (Turkish)", "ไทย (Thai)", "Tiếng Việt (Vietnamese)",
    "Filipino", "Bahasa Melayu (Malay)", "Nederlands (Dutch)", "Polski (Polish)",
    "Українська (Ukrainian)", "فارسی (Persian)", "עברית (Hebrew)", "Kiswahili (Swahili)",
    "ગુજરાતી (Gujarati)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "ಕನ್ನಡ (Kannada)",
    "മലയാളം (Malayalam)", "ਪੰਜਾਬੀ (Punjabi)", "मराठी (Marathi)", "नेपाली (Nepali)",
    "සිංහල (Sinhala)", "မြန်မာ (Burmese)", "ខ្មែរ (Khmer)", "ລາວ (Lao)",
    "Монгол (Mongolian)", "Қазақша (Kazakh)", "Oʻzbekcha (Uzbek)",
    "Azərbaycan dili (Azerbaijani)", "Română (Romanian)", "Magyar (Hungarian)",
    "Čeština (Czech)", "Ελληνικά (Greek)", "Svenska (Swedish)", "Norsk (Norwegian)",
    "Dansk (Danish)", "Suomi (Finnish)", "Bahasa lain (isi sendiri)"
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
                "Create original stories with strong hooks, escalating conflict, "
                "connected punchlines, and varied story-specific CTAs. Return valid JSON only."
            )},
            {"role": "user", "content": prompt},
        ],
        temperature=0.95,
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

def ensure_contextual_cta(x, language):
    dialogue = x.setdefault("dialogue", [])
    if not isinstance(dialogue, list):
        dialogue = []
        x["dialogue"] = dialogue
    all_text = " ".join(
        str(d.get("line", "")) for d in dialogue if isinstance(d, dict)
    ).lower()
    cta_words = (
        "subscribe", "subscribed", "suscríb", "suscríbete", "inscrev", "abonn",
        "abone", "登録", "구독", "اشترك", "सब्सक्राइब", "langganan", "ikuti channel"
    )
    if any(word in all_text for word in cta_words):
        return x

    language_name = str(language).lower()
    context = (
        str(x.get("title", "")) + " " + str(x.get("punchline", "")) + " " +
        str(x.get("story", "")
    )).lower()

    if "bahasa indonesia" in language_name or language_name == "indonesia":
        if any(w in context for w in ["utang", "debt", "dompet", "pinjol", "bangkrut", "duit", "uang"]):
            options = [
                "Bantu dompetku ikut bahagia—subscribe, gratis kok!",
                "Kalau tertawa, bayarnya cukup subscribe. Tidak bisa dicicil!",
                "Subscribe dulu, siapa tahu rezekiku ikut lancar!",
                "Aku miskin, tapi tombol subscribe masih gratis, kan?!"
            ]
        elif any(w in context for w in ["hantu", "neraka", "kuburan", "mati", "alam baka", "horor", "pocong", "arwah"]):
            options = [
                "Jangan bikin aku gentayangan—subscribe dulu!",
                "Kalau tidak subscribe, aku muncul lagi di video berikutnya!",
                "Biar arwahku tenang, pencet subscribe dulu!",
                "Takut sama aku? Buktikan dengan subscribe!"
            ]
        elif any(w in context for w in ["antre", "antrian", "antrean", "nomor"]):
            options = [
                "Subscribe sekarang, tidak perlu ambil nomor antrean!",
                "Yang ini tidak pakai antre—langsung subscribe saja!",
                "Biar tidak menunggu lagi, subscribe sekarang!",
                "Nomor antrean boleh jutaan, subscriber jangan nol!"
            ]
        else:
            options = [
                "Kalau punchline-ku bikin tertawa, traktir aku dengan subscribe!",
                "Subscribe dulu, gratis—tidak ada plot twist biaya!",
                "Jangan cuma tertawa, subscribe juga!",
                "Mau lihat kekacauan berikutnya? Subscribe dulu!",
                "Kasih aku satu kebahagiaan hari ini: subscribe!",
                "Tertawa boleh, lupa subscribe jangan!"
            ]
    elif "english" in language_name:
        options = [
            "If that twist got you, subscribe before the next disaster!",
            "Don't leave me alone with this mess—hit subscribe!",
            "Subscribe now. The next episode might be even worse!",
            "You witnessed that chaos. Make it official—subscribe!",
            "Save this character from another bad decision—subscribe!"
        ]
    else:
        options = [
            "If this story made you smile, subscribe for the next surprise!",
            "Want to see what happens next? Subscribe!",
            "That was only the beginning—subscribe for more!"
        ]

    dialogue.append({"time": "Akhir", "speaker": "KARAKTER", "line": random.choice(options)})
    x["cta_note"] = "CTA cadangan ditambahkan karena respons model belum menyertakan CTA."
    return x

def prompts(x, style, duration, language):
    x = ensure_contextual_cta(x, language)
    dialogue = "\\n".join(
        f'{d.get("time","")} {d.get("speaker","")}: "{d.get("line","")}"'
        for d in x.get("dialogue", []) if isinstance(d, dict)
    )
    x["flow_prompt"] = f"""Create a {duration} vertical 9:16 {style} YouTube Short.
GOAL: gain subscribers through funny, memorable entertainment.
MANDATORY EDITING ORDER: (1) immediate shock close-up/reveal, (2) direct conflict between characters, (3) reaction shot that creates comedy, (4) unexpected reversal/counterattack, (5) speaking character snaps gaze to lens and delivers the story-specific CTA, (6) strong ending; loop only if natural.
Do not begin with an establishing shot. Show the hook in the very first frame. Make the horror atmosphere genuinely eerie, then let comedy emerge from character reactions and reversal. Keep visual continuity between what is seen and what is spoken.
HOOK 0–2s: {x.get('hook','')}
STORY: {x.get('story','')}
DIALOGUE:
{dialogue}
PUNCHLINE: {x.get('punchline','')}
ENDING: {x.get('ending','')}
CTA CAMERA DIRECTION — CRITICAL:
At the CTA line, the speaking character MUST instantly snap their attention to the lens, lean slightly toward the camera, and hold direct eye contact for the entire line. Use a sudden but smooth comedic push-in / close-up and a bold, expressive facial reaction. The character speaks directly to the viewer, not to another character. Preserve the exact CTA words. The delivery should feel confident, surprising, cheeky, and funny—not polite, flat, or like an advertisement.

HOOK IMPACT — FIRST 1 SECOND:
Open in the middle of a startling event, not a setup. The first frame must show an unmistakable emotional reaction or impossible visual: a sudden close-up, a character already screaming, an object behaving impossibly, or a shocking reveal. Start with a short, punchy spoken line or a strong visual action immediately. No greeting, establishing shot, slow walk, explanation, or empty pause. The viewer should instantly think “WHAT?!”

CTA CAMERA DIRECTION — EMOTIONAL PAYOFF:
At the CTA line, the speaking character suddenly stops, turns straight to the lens, locks eyes with the viewer, and moves into a tight close-up. The change should feel startling but smooth. The expression must be intense and readable: wounded disbelief, desperate panic, smug triumph, mock betrayal, or absurd seriousness—chosen to match the story. Deliver the line directly to the viewer with a clear emotional shift, a tiny pause before the final key words, and strong lip-sync.

CTA IMPACT:
The CTA must be a second shock AND an emotional mini-punchline, not an ordinary request to subscribe. It should make the viewer laugh, feel caught, feel challenged, or be surprised by a sudden confession or absurd consequence. Connect it specifically to the story's final twist. Use a short, quotable line with a strong final phrase. Playfully dramatic, not genuinely threatening. Ban flat lines such as “Please subscribe,” “If you enjoyed this,” “Want more? Subscribe,” and “Don't forget to subscribe.” No extra dialogue.

SEAMLESS LOOP — IMPORTANT:
Design the opening and ending together before staging the action. The ending must flow back into the opening as if the action never stopped.
- Establish a clear opening composition: character positions, camera distance, background, lighting, and a simple ongoing motion.
- Use one continuous, physically plausible action that can lead naturally from the final moment back to the first moment.
- In the final 1–1.5 seconds, return the main character and camera to the same composition and pose as the opening frame. Match position, scale, direction of movement, lighting, and background.
- The last movement should trigger or continue the opening movement. Avoid introducing a new action in the final instant.
- Keep camera movement smooth and consistent. No sudden angle changes, teleporting characters, jump cuts, abrupt zooms, or background changes near the loop point.
- End dialogue before the loop point when possible. Avoid a sharp audio cut, sudden silence, or a new sound exactly at the restart. Use continuous ambience or a sound that naturally carries across the loop.
- Do not use fade-to-black. Do not fake a loop by simply cutting the ending to the beginning.
- Prioritize a smooth match between the final and opening frames over an extra ending gag. If the story cannot support a natural loop, use a clean ending instead of forcing a bad loop.

Start immediately in the middle of a startling event within the first frame. No long intro. Use expressive faces, clear body language, cinematic sharp visuals, fast but understandable timing. All spoken dialogue and voices must use {language}; use natural pronunciation and accurate lip-sync. No overlapping dialogue. No gore, subtitles, text overlays, logos or watermark. Keep all action in vertical 9:16."""
    x["thumbnail_prompt"] = f"""Create a bold, cinematic vertical 9:16 YouTube Shorts thumbnail for an international comedy audience. Target language for any optional title text: {language}. Video title: {x.get('title','')}. Main moment: {x.get('hook','')}. Exaggerated funny/shocked faces, one character close to camera, another reacting in the background, dramatic lighting, high contrast, sharp readable composition on a phone. Leave clear space at bottom for a short, readable title in {language}. No logos, no watermark, no gore."""
    x.setdefault("hashtags", "#Shorts #Comedy #Funny")
    return x

def local_idea():
    pool = [
      {"title":"HANTU GAK PUNYA CHANNEL! 👻😂","hook":"Hantu menerjang kamera dan menunjuk penonton: “WOI! KAMU YANG DI SITU!”","story":"Hantu menuduh penonton menonton sampai habis tetapi tidak subscribe. Manusia membalas dengan kejutan.","dialogue":[{"time":"0–2 detik","speaker":"HANTU","line":"WOI! KAMU YANG DI SITU!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"KENAPA AKU?!"},{"time":"4–7 detik","speaker":"HANTU","line":"NONTON TERUS, TAPI TIDAK SUBSCRIBE!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"KAMU SAJA TIDAK PUNYA CHANNEL!"}],"punchline":"Hantu terdiam malu, lalu menjerit dan kabur.","ending":"Manusia tertawa; gunakan loop hanya jika sambungannya alami."},
      {"title":"HANTU KENA ROAST! 🤣👻","hook":"Manusia malah menunjuk hantu yang bersiap menakut-nakuti.","story":"Hantu sok seram, tetapi manusia membalas dengan lelucon tentang subscriber.","dialogue":[{"time":"0–2 detik","speaker":"MANUSIA","line":"MAU MENAKUTI AKU?!"},{"time":"2–4 detik","speaker":"HANTU","line":"IYA! TAKUT TIDAK?!"},{"time":"4–7 detik","speaker":"MANUSIA","line":"AKU TAKUT KAMU TIDAK DAPAT SUBSCRIBER!"},{"time":"7–10 detik","speaker":"HANTU","line":"KOK AKU YANG SEDIH?!"}],"punchline":"Hantu menangis dramatis; manusia kebingungan.","ending":"Tutup dengan ekspresi hantu yang berlebihan."},
      {"title":"KETAHUAN GAK PUNYA CHANNEL! 😂","hook":"Hantu muncul mendadak dengan wajah seram tepat di depan kamera.","story":"Hantu mengancam manusia, tetapi malah ditanya soal channel miliknya.","dialogue":[{"time":"0–2 detik","speaker":"HANTU","line":"BERHENTI! AKU MAU MENAKUTIMU!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"MEMANG KAMU TERKENAL?!"},{"time":"4–7 detik","speaker":"HANTU","line":"BELUM, TAPI AKU MENAKUTKAN!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"BUAT CHANNEL DULU, BOS!"}],"punchline":"Hantu panik karena tidak tahu cara membuat channel.","ending":"Hantu menatap kamera dengan wajah bingung."}
    ]
    return random.choice(pool)

with st.sidebar:
    st.header("Pengaturan API")
    key = api_key()
    if not key:
        key = st.text_input(
            "API Key ClarioHub",
            type="password",
            help="Key yang dimasukkan di sini hanya untuk sesi ini. Untuk penggunaan permanen, simpan di Streamlit Secrets."
        ).strip()
    st.write("ClarioHub API:", "✅ Key tersedia" if key else "⚠️ Masukkan API key")
    st.caption(f"Endpoint: {BASE_URL}")
    model_options = {
        "Gemini 3.7 Flash": "clario/gemini-3.7-flash",
        "DeepSeek V4 Pro": "clario/deepseek-v4-pro",
        "DeepSeek V4 Flash": "clario/deepseek-v4-flash",
        "DeepSeek V4.1 Flash": "clario/deepseek-v4.1-flash",
        "GLM 5.3 Flash": "clario/glm-5.3-flash",
        "GLM 5.3": "clario/glm-5.3",
        "MiniMax M3": "clario/minimax-m3",
        "GPT 5.6 Sol": "clario/gpt-5.6-sol",
        "Opus 5": "clario/opus-5",
    }
    selected_model_label = st.selectbox(
        "Model AI",
        list(model_options.keys()),
        index=0,
        help="Pilihan diambil dari katalog key standar pada dokumentasi ClarioHub."
    )
    model = model_options[selected_model_label]
    st.caption(f"ID model: {model}")
    st.divider()
    st.header("Pengaturan konten")
    language_choice = st.selectbox("🌎 Bahasa cerita & dialog", LANGUAGES, index=0)
    if language_choice == "Bahasa lain (isi sendiri)":
        custom_language = st.text_input("Nama bahasa", placeholder="Contoh: Yoruba, Icelandic, Amharic")
        target_language = custom_language.strip() or "English"
    else:
        target_language = language_choice
    st.caption("Pilih bahasa untuk judul, cerita, dialog, hashtag, dan suara.")
    style = st.selectbox("Gaya visual", ["Horor-komedi realistis", "Komedi absurd realistis", "Hantu + manusia", "Karakter bebas"])
    duration = st.selectbox("Durasi", ["8 detik", "10 detik", "12 detik", "15 detik"], index=1)
    humor = st.selectbox("Jenis humor", ["Absurd dan mengejutkan", "Roasting lucu", "Salah paham kocak", "Plot twist", "Slapstick visual", "Deadpan", "Kesialan beruntun", "Role reversal", "Satir sosial"])
    structure = st.selectbox(
        "Struktur cerita (formula tetap)",
        ["Cadas viral: KAGET → KONFLIK → REAKSI LUCU → BALIK MENYERANG → CTA",
         "Horor misteri → salah paham → twist → CTA",
         "Kejadian absurd → eskalasi → punchline → CTA"],
        index=0,
        help="Struktur dikunci; cerita, karakter, dialog, dan punchline tetap dibuat baru setiap generate."
    )
    avoid = st.text_input("Hindari ide/karakter (opsional)")

if "idea" not in st.session_state:
    st.session_state.idea = None

if "recent_ctas" not in st.session_state:
    st.session_state.recent_ctas = []

if st.button("🔥 GENERATE IDE BARU", type="primary", use_container_width=True):
    recent_cta_text = "\\n".join(f"- {line}" for line in st.session_state.recent_ctas[-12:]) or "- None yet"
    prompt = f"""Create ONE original YouTube Shorts idea designed to gain subscribers.
OUTPUT LANGUAGE: {target_language}. Write title, hook, story, dialogue, punchline, ending, hashtags, and cta_note in {target_language}. Do not use Indonesian unless Indonesian is selected. Write naturally for native speakers; do not literally translate jokes.
MANDATORY STORY STRUCTURE — KEEP THIS ORDER, DO NOT SKIP OR MERGE BEATS:
{structure}
1) SHOCK HOOK (0–1s): start already inside a startling event. Extreme close-up/reveal, sudden accusation, scream, or impossible action. No intro.
2) CONFLICT (1s onward): a human and a scary character directly confront each other. The visual action and spoken line must match.
3) FUNNY REACTION: show a clear reaction shot from the other character; fear, disbelief, or a sharp comeback. Use the reaction to create comedy.
4) REVERSAL / COUNTERATTACK: the person who seemed powerful gets embarrassed, exposed, or surprised. The twist must come from the actual conflict, not a random unrelated joke.
5) DIRECT-TO-CAMERA CTA (final spoken line): the character snaps their gaze to the lens, points/leans toward camera, and delivers a loud, intense, scary-but-funny subscribe line that grows from the twist. CTA is spoken, not just a button overlay.
6) ENDING: finish on a strong readable expression/action. If possible, return to opening composition for a loop, but do not sacrifice the punchline.
The structure must remain stable across generations, while every story's setting, conflict, character roles, comeback, punchline and CTA wording must be meaningfully new. Do not reuse the exact plot of “GAK PUNYA CHANNEL!”.
HOOK QUALITY RULES:
- Begin in the middle of an incident: a sudden reveal, impossible action, intense reaction, or unexpected accusation.
- The first spoken line should be short and forceful (roughly 2–7 words where natural), not exposition.
- Make the opening visual and dialogue tell the same story beat; no mismatch between what is seen and heard.
- No slow intro, greetings, scene-setting, or generic “Wait until the end.”
CTA QUALITY RULES:
- The CTA must make the viewer react emotionally: surprised, amused, challenged, mock-guilty, or caught off guard.
- Add a sharp emotional turn immediately before or during the CTA: the character goes from smug to desperate, scary to offended, confident to betrayed, or another story-fitting reversal.
- The CTA should sound like a memorable final line in a comedy sketch, not a marketing slogan.
- Make it a final mini-joke or unexpected twist that grows directly out of the punchline.
- Use a bold, cheeky, dramatic, absurd, or mock-serious delivery; playful, not genuinely threatening.
- Address the camera/viewer directly in a natural way, but do NOT start every CTA with “you,” “lu,” “hey you,” or the same repeated phrase.
- Do NOT use bland/generic CTAs such as “Please subscribe,” “If you enjoyed this,” “Want more? Subscribe,” or “Don't forget to subscribe.”
- Every new story must invent a different wording AND a different comedic mechanism. Avoid merely swapping one noun in a repeated template.
- CTA must be the FINAL spoken dialogue line, must fit the story's exact punchline, and must be short enough to deliver clearly in the selected duration.
- The speaker must turn and look directly into the camera lens during the CTA.
RECENT CTAs TO AVOID repeating or imitating:
{recent_cta_text}
Selected structure: {structure}. Visual style: {style}. Humor type: {humor}. Duration: {duration}. Avoid these ideas/characters: {avoid or 'none'}.
Dialogue must fit the duration, use at most 3 characters, and have no long intro. Make each new idea meaningfully different from previous ideas. CTA must be spoken, not only written in notes. Design the ending and opening as a potential seamless loop: specify a repeatable action/pose and make the final action naturally lead into the opening. Do not force a loop if the story ending would become awkward.
Return valid JSON only with fields: title, hook, story, dialogue (array of objects with time, speaker, line), punchline, ending, hashtags, cta_note, structure_beats. structure_beats must be an object with keys shock_hook, conflict, funny_reaction, reversal, direct_to_camera_cta, ending_loop; each key briefly explains the corresponding beat in the generated story. The dialogue array MUST include the story-specific subscribe CTA as its final spoken line. Keep timing labels easy to understand. Jokes must be understandable to viewers familiar with {target_language}."""
    try:
        if not key:
            raise RuntimeError("Masukkan API Key ClarioHub di sidebar atau simpan CLARIOHUB_API_KEY di Streamlit Secrets.")
        if not model.strip():
            raise RuntimeError("Isi nama model yang tersedia dari penyedia.")
        result = call_gemini(key, model.strip(), prompt)
        st.session_state.idea = prompts(result, style, duration, target_language)
        dialogue_items = st.session_state.idea.get("dialogue", [])
        final_cta = ""
        if dialogue_items and isinstance(dialogue_items[-1], dict):
            final_cta = str(dialogue_items[-1].get("line", "")).strip()
        if final_cta:
            st.session_state.recent_ctas.append(final_cta)
            st.session_state.recent_ctas = st.session_state.recent_ctas[-12:]
    except Exception as e:
        st.error(f"ClarioHub gagal: {e}")
        st.info("Tidak memakai ide cadangan otomatis agar kegagalan API tidak disamarkan sebagai cerita baru. Periksa API key, nama model, saldo/kuota, lalu coba lagi.")

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title", "Ide Shorts"))
    st.code(x.get("hashtags", "#Shorts #Comedy #Funny"))
    t1, t2, t3, t4 = st.tabs(["Cerita & Dialog", "Prompt Google Flow", "Prompt Thumbnail", "Evaluasi Subscriber"])
    with t1:
        st.markdown("**HOOK (0–2 detik)**"); st.write(x.get("hook", ""))
        st.markdown("**CERITA**"); st.write(x.get("story", ""))
        st.markdown("**DIALOG**")
        for d in x.get("dialogue", []):
            if isinstance(d, dict):
                st.write(f"**{d.get('time', '')} | {d.get('speaker', '')}** — {d.get('line', '')}")
        st.markdown("**PUNCHLINE**"); st.write(x.get("punchline", ""))
        st.markdown("**ENDING**"); st.write(x.get("ending", ""))
        beats = x.get("structure_beats", {})
        if isinstance(beats, dict) and beats:
            st.markdown("**Pemeriksaan struktur wajib**")
            for beat_key, beat_label in [("shock_hook", "1. Hook mengejutkan"), ("conflict", "2. Konflik"), ("funny_reaction", "3. Reaksi lucu"), ("reversal", "4. Balik menyerang / twist"), ("direct_to_camera_cta", "5. CTA langsung ke kamera"), ("ending_loop", "6. Ending / loop")]:
                if beats.get(beat_key):
                    st.write(f"**{beat_label}:** {beats[beat_key]}")
        st.info(x.get("cta_note", "CTA subscribe menyatu dengan lelucon; karakter menatap kamera saat mengucapkannya."))
    with t2:
        st.text_area("Salin prompt video", x.get("flow_prompt", ""), height=420)
    with t3:
        st.text_area("Salin prompt thumbnail", x.get("thumbnail_prompt", ""), height=250)
    with t4:
        a, b, c = st.columns(3)
        views = a.number_input("Views", 0, step=1)
        subs = b.number_input("Subscriber baru", 0, step=1)
        viewed = c.number_input("Viewed (%)", 0.0, 100.0, step=0.5)
        if views:
            st.metric("Subscriber per 100 views", f"{subs / views * 100:.2f}")
        st.caption("Catat hasil dari YouTube Studio; bandingkan beberapa video, jangan menilai dari satu video saja.")
    data = {k: x.get(k) for k in ["title", "hashtags", "hook", "story", "dialogue", "punchline", "ending", "structure_beats", "flow_prompt", "thumbnail_prompt"]}
    st.download_button("⬇️ Simpan paket ide JSON", json.dumps(data, ensure_ascii=False, indent=2), "shorts_idea.json", "application/json")
else:
    st.write("Klik **GENERATE IDE BARU** untuk mendapatkan judul, dialog, prompt Flow, dan prompt thumbnail.")
    st.write("Pilih bahasa di sidebar untuk membuat konten bagi penonton Indonesia atau audiens internasional.")
    st.write("Target: hook kuat → cerita menarik → punchline ngena → alasan untuk subscribe.")
