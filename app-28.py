import os, json, random, requests
import streamlit as st

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

def api_key():
    try:
        if st.secrets.get("GEMINI_API_KEY"): return st.secrets["GEMINI_API_KEY"]
    except Exception: pass
    return os.getenv("GEMINI_API_KEY", "")

def call_gemini(key, model, prompt):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json={"contents":[{"parts":[{"text":prompt}]}],
              "generationConfig":{"temperature":0.95,"responseMimeType":"application/json"}},
        timeout=90)
    if not r.ok:
        try: msg = r.json().get("error",{}).get("message",r.text)
        except Exception: msg = r.text
        raise RuntimeError(f"Gemini API {r.status_code}: {msg}")
    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(txt)

def prompts(x, style, duration, language):
    dialogue = "\\n".join(f'{d.get("time","")} {d.get("speaker","")}: "{d.get("line","")}"' for d in x.get("dialogue",[]))
    x["flow_prompt"] = f"""Create a {duration} vertical 9:16 {style} YouTube Short.
GOAL: gain subscribers through funny, memorable entertainment.
HOOK 0–2s: {x.get('hook','')}
STORY: {x.get('story','')}
DIALOGUE:
{dialogue}
PUNCHLINE: {x.get('punchline','')}
ENDING: {x.get('ending','')}
Start immediately with a surprising close-up/action. No long intro. Use expressive faces, clear body language, cinematic sharp visuals, fast but understandable timing. All spoken dialogue and voices must use {language}; use natural pronunciation and accurate lip-sync. No overlapping dialogue. Humor-based indirect subscribe joke should feel natural, not like an ad. No gore, subtitles, text overlays, logos or watermark. Keep all action in vertical 9:16. Do not add extra dialogue."""
    x["thumbnail_prompt"] = f"""Create a bold, cinematic vertical 9:16 YouTube Shorts thumbnail for an international comedy audience. Target language for any optional title text: {language}. Video title: {x.get('title','')}. Main moment: {x.get('hook','')}. Exaggerated funny/shocked faces, one character close to camera, another reacting in the background, dramatic lighting, high contrast, sharp readable composition on a phone. Leave clear space at bottom for a short, readable title in {language}. No logos, no watermark, no gore."""
    x.setdefault("hashtags","#Shorts #HororLucu #KomediHoror")
    return x

def local_idea():
    pool = [
      {"title":"HANTU GAK PUNYA CHANNEL! 👻😂","hook":"Hantu menerjang kamera dan menunjuk penonton: “WOI! KAMU YANG DI SITU!”","story":"Hantu menuduh penonton menonton sampai habis tetapi tidak subscribe. Manusia membalas dengan kejutan.","dialogue":[{"time":"0–2 detik","speaker":"HANTU","line":"WOI! KAMU YANG DI SITU!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"KENAPA GUE?!"},{"time":"4–7 detik","speaker":"HANTU","line":"NONTON TERUS, TAPI GAK SUBSCRIBE!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"LAH, LU AJA GAK PUNYA CHANNEL!"}],"punchline":"Hantu terdiam malu, lalu menjerit dan kabur.","ending":"Manusia tertawa; gunakan loop hanya jika sambungannya alami."},
      {"title":"HANTU KENA ROAST! 🤣👻","hook":"Manusia malah menunjuk hantu yang bersiap menakut-nakuti.","story":"Hantu sok seram, tetapi manusia membalas dengan lelucon tentang subscriber.","dialogue":[{"time":"0–2 detik","speaker":"MANUSIA","line":"MAU NAKUTIN GUE?!"},{"time":"2–4 detik","speaker":"HANTU","line":"IYA! TAKUT GAK?!"},{"time":"4–7 detik","speaker":"MANUSIA","line":"GUE TAKUT LU GAK DAPAT SUBSCRIBER!"},{"time":"7–10 detik","speaker":"HANTU","line":"LAH, KOK GUE YANG SEDIH?!"}],"punchline":"Hantu menangis dramatis; manusia kebingungan.","ending":"Tutup dengan ekspresi hantu yang lebay."},
      {"title":"KETAHUAN GAK PUNYA CHANNEL! 😂","hook":"Hantu muncul mendadak dengan wajah seram tepat di depan kamera.","story":"Hantu mengancam manusia, tetapi malah ditanya soal channel miliknya.","dialogue":[{"time":"0–2 detik","speaker":"HANTU","line":"BERHENTI! GUE MAU NAKUTIN LU!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"EMANG LU TERKENAL?!"},{"time":"4–7 detik","speaker":"HANTU","line":"BELUM, TAPI GUE MENAKUTKAN!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"BIKIN CHANNEL DULU, BOS!"}],"punchline":"Hantu panik karena tidak tahu cara membuat channel.","ending":"Hantu menatap kamera dengan wajah bingung."}
    ]
    return random.choice(pool)

with st.sidebar:
    st.header("Pengaturan")
    key = api_key()
    st.write("Gemini API:", "✅ Terhubung" if key else "⚠️ Belum diatur")
    model = st.text_input("Model Gemini", "gemini-3.8-flash")
    language_choice = st.selectbox("🌎 Bahasa cerita & dialog", LANGUAGES, index=0)
    if language_choice == "Bahasa lain (isi sendiri)":
        custom_language = st.text_input("Nama bahasa", placeholder="Contoh: Yoruba, Icelandic, Amharic")
        target_language = custom_language.strip() or "English"
    else:
        target_language = language_choice
    st.caption("Pilih bahasa untuk judul, cerita, dialog, hashtag, dan suara. Untuk bahasa yang tidak ada, pilih 'Bahasa lain'.")
    style = st.selectbox("Gaya visual", ["Horor-komedi realistis","Komedi absurd realistis","Hantu + manusia","Karakter bebas"])
    duration = st.selectbox("Durasi", ["8 detik","10 detik","12 detik","15 detik"], index=1)
    humor = st.selectbox("Jenis humor", ["Absurd dan mengejutkan","Roasting lucu","Salah paham kocak","Plot twist"])
    avoid = st.text_input("Hindari ide/karakter (opsional)")

if "idea" not in st.session_state: st.session_state.idea = None
if st.button("🔥 GENERATE IDE BARU", type="primary", use_container_width=True):
    prompt = f"""Create ONE original YouTube Shorts idea designed to gain subscribers.
OUTPUT LANGUAGE: {target_language}. Write the title, hook, story, dialogue, punchline, ending, hashtags, and cta_note in {target_language}. Do not use Indonesian unless Indonesian is the selected language. Keep wording natural for native speakers, culturally understandable, and not a literal translation.
Formula: an immediate surprising hook in 0–2 seconds; a curiosity-building story; a strong punchline; and a subscribe CTA naturally embedded in the joke. Characters may vary; do not rely only on ghosts. Visual style: {style}. Humor type: {humor}. Duration: {duration}. Avoid these ideas/characters: {avoid or 'none'}. Dialogue must fit the duration, use at most 3 characters, and have no long intro. Make each new idea meaningfully different.
Return valid JSON only with fields: title, hook, story, dialogue (array of objects with time, speaker, line), punchline, ending, hashtags, cta_note. Keep timing labels easy to understand. Make jokes understandable to viewers familiar with {target_language}."""
    try:
        if key: result = call_gemini(key, model, prompt)
        else: result = local_idea()
        st.session_state.idea = prompts(result, style, duration, target_language)
    except Exception as e:
        st.error(f"Gemini gagal: {e}")
        st.info("Ide cadangan saat ini berbahasa Indonesia. Untuk bahasa lain, periksa API/kuota lalu tekan Generate lagi.")
        st.session_state.idea = prompts(local_idea(), style, duration, target_language)

x = st.session_state.idea
if x:
    st.divider()
    st.subheader(x.get("title","Ide Shorts"))
    st.code(x.get("hashtags","#Shorts #HororLucu #KomediHoror"))
    t1,t2,t3,t4 = st.tabs(["Cerita & Dialog","Prompt Google Flow","Prompt Thumbnail","Evaluasi Subscriber"])
    with t1:
        st.markdown("**HOOK (0–2 detik)**"); st.write(x.get("hook",""))
        st.markdown("**CERITA**"); st.write(x.get("story",""))
        st.markdown("**DIALOG**")
        for d in x.get("dialogue",[]): st.write(f"**{d.get('time','')} | {d.get('speaker','')}** — {d.get('line','')}")
        st.markdown("**PUNCHLINE**"); st.write(x.get("punchline",""))
        st.markdown("**ENDING**"); st.write(x.get("ending",""))
        st.info(x.get("cta_note","CTA subscribe menyatu dengan lelucon, jangan terasa memaksa."))
    with t2: st.text_area("Salin prompt video",x.get("flow_prompt",""),height=420)
    with t3: st.text_area("Salin prompt thumbnail",x.get("thumbnail_prompt",""),height=250)
    with t4:
        a,b,c = st.columns(3)
        views = a.number_input("Views",0,step=1)
        subs = b.number_input("Subscriber baru",0,step=1)
        viewed = c.number_input("Viewed (%)",0.0,100.0,step=0.5)
        if views: st.metric("Subscriber per 100 views",f"{subs/views*100:.2f}")
        st.caption("Catat hasil dari YouTube Studio; bandingkan beberapa video, jangan menilai dari satu video saja.")
    data = {k:x.get(k) for k in ["title","hashtags","hook","story","dialogue","punchline","ending","flow_prompt","thumbnail_prompt"]}
    st.download_button("⬇️ Simpan paket ide JSON",json.dumps(data,ensure_ascii=False,indent=2),"shorts_idea.json","application/json")
else:
    st.write("Klik **GENERATE IDE BARU** untuk mendapatkan judul, dialog, prompt Flow, dan prompt thumbnail.")
    st.write("Pilih bahasa di sidebar untuk membuat konten bagi penonton Indonesia atau audiens internasional.")
    st.write("Target: hook kuat → cerita menarik → punchline ngena → alasan untuk subscribe.")
