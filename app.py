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

def local_idea(recent_titles=None):
    recent = set((t or "").strip().casefold() for t in (recent_titles or []))
    pool = [
      {"title":"HANTU DITAGIH SUBSCRIBE! 👻😂","hook":"Hantu muncul dari lemari sambil membawa buku catatan.","story":"Hantu menagih manusia yang sudah menonton semua videonya tetapi belum subscribe.","dialogue":[{"time":"0–2 detik","speaker":"HANTU","line":"TAGIHAN SUBSCRIBE KAMU SUDAH JATUH TEMPO!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Lah, emang kamu jualan apa?"},{"time":"4–7 detik","speaker":"HANTU","line":"AKU JUALAN KETAKUTAN, BAYARNYA SUBSCRIBE!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Pantesan daganganmu gak laku, promonya serem!"}],"punchline":"Hantu melihat buku catatannya kosong lalu ikut panik.","ending":"Hantu buru-buru membuat akun channel sendiri.","cta_note":"CTA masuk ke dialog sebagai lelucon tentang subscribe."},
      {"title":"MALAIKAT IKUT ROASTING! 😇🤣","hook":"Malaikat turun dengan wajah kecewa sambil menunjuk HP manusia.","story":"Manusia mengira malaikat datang membawa kabar baik, ternyata malaikat mengomentari kebiasaan menonton tanpa subscribe.","dialogue":[{"time":"0–2 detik","speaker":"MALAIKAT","line":"AKU DATANG MEMBAWA PESAN PENTING!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Aku masuk surga?!"},{"time":"4–7 detik","speaker":"MALAIKAT","line":"BELUM. SUBSCRIBE DULU, BARU KITA BICARA!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Lah, surga sekarang pakai syarat channel?"}],"punchline":"Malaikat mengangguk serius lalu memeriksa statistik subscriber.","ending":"Manusia dan malaikat sama-sama menatap kamera.","cta_note":"CTA subscribe menyatu dengan kejutan dialog."},
      {"title":"KUNTILANAK SALAH SASARAN! 😂👻","hook":"Kuntilanak menerjang kamera, tetapi malah kaget melihat manusia.","story":"Kuntilanak hendak menakuti manusia, tetapi manusia mengira ia datang untuk promosi channel.","dialogue":[{"time":"0–2 detik","speaker":"KUNTILANAK","line":"HIIII! TAKUT KAN?!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Oh, sales datang?"},{"time":"4–7 detik","speaker":"KUNTILANAK","line":"SALES APA? AKU HANTU!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Kalau begitu, bantu subscribe dulu, Mbak!"}],"punchline":"Kuntilanak bingung lalu menunjuk dirinya sendiri.","ending":"Kuntilanak malah meminta manusia mengajari cara membuat channel.","cta_note":"CTA hadir sebagai punchline, bukan teks tempelan."},
      {"title":"SATPAM AKHIRAT KENA PRANK! 💀🤣","hook":"Satpam akhirat menghadang seorang manusia yang sedang scroll HP.","story":"Satpam mengira manusia sedang mencari jalan ke akhirat, ternyata manusia sedang menonton Shorts tanpa subscribe.","dialogue":[{"time":"0–2 detik","speaker":"SATPAM","line":"MAU KE MANA, BOS?!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Cuma scroll video."},{"time":"4–7 detik","speaker":"SATPAM","line":"SUDAH NONTON, SUBSCRIBE BELUM?!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Pak, ini pemeriksaan atau promosi?"}],"punchline":"Satpam mengeluarkan papan bertuliskan 'pos jaga subscriber'.","ending":"Satpam kembali berjaga sambil ikut scroll.","cta_note":"CTA dimasukkan ke percakapan komedi."},
      {"title":"HANTU TAKUT LIHAT ANALYTICS! 📉👻","hook":"Hantu menjerit melihat layar HP yang menunjukkan angka nol.","story":"Manusia mengira hantu takut matahari, ternyata ia takut melihat subscriber channel-nya.","dialogue":[{"time":"0–2 detik","speaker":"MANUSIA","line":"Kok kamu pucat banget?"},{"time":"2–4 detik","speaker":"HANTU","line":"SUBSCRIBER-KU MASIH NOL!"},{"time":"4–7 detik","speaker":"MANUSIA","line":"Kamu kan hantu, bukan kreator!"},{"time":"7–10 detik","speaker":"HANTU","line":"MAKANYA SUBSCRIBE, BIAR AKU PUNYA MASA DEPAN!"}],"punchline":"Manusia menepuk bahu hantu, lalu kabur karena hantu mulai menangis.","ending":"Hantu menatap kamera dengan mata berkaca-kaca.","cta_note":"CTA langsung menjadi alasan komedi dalam cerita."},
      {"title":"POCONG GAGAL MENAKUTI! 🧟‍♂️😂","hook":"Pocong melompat ke depan manusia, tetapi manusia malah menguap.","story":"Pocong kesal karena manusia tidak takut. Ia mencoba mengancam, tetapi manusia menyuruhnya membangun channel dulu.","dialogue":[{"time":"0–2 detik","speaker":"POCONG","line":"BOO! TAKUT GAK?!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Kurang niat, Bang."},{"time":"4–7 detik","speaker":"POCONG","line":"TERUS AKU HARUS APA?!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Bikin channel, terus suruh orang subscribe!"}],"punchline":"Pocong mencoba mengangguk tetapi malah terguling.","ending":"Manusia membantu pocong berdiri sambil tertawa.","cta_note":"CTA berada di dialog terakhir dan menyatu dengan lelucon."},
      {"title":"DOKTER HANTU SALAH RESEP! 🩺👻","hook":"Dokter hantu memeriksa manusia lalu langsung menggeleng dramatis.","story":"Manusia takut divonis sakit parah, tetapi dokter hantu mengatakan penyakitnya adalah menonton tanpa subscribe.","dialogue":[{"time":"0–2 detik","speaker":"DOKTER HANTU","line":"HASIL PEMERIKSAAN SUDAH KELUAR!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Saya sakit apa, Dok?!"},{"time":"4–7 detik","speaker":"DOKTER HANTU","line":"KEKURANGAN SUBSCRIBE!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Dok, itu penyakit atau target kerja?"}],"punchline":"Dokter hantu menyerahkan resep berupa tombol subscribe imajiner.","ending":"Dokter hantu ikut meminta pasien subscribe channel-nya.","cta_note":"CTA dijadikan bagian dari punchline medis absurd."},
      {"title":"IBLIS PUNYA TARGET SUBSCRIBER! 😈😂","hook":"Iblis datang dengan map tebal dan wajah seperti sales kelelahan.","story":"Manusia mengira iblis datang menjemputnya, ternyata iblis sedang mengejar target subscriber bulanan.","dialogue":[{"time":"0–2 detik","speaker":"IBLIS","line":"AKHIRNYA KETEMU JUGA!"},{"time":"2–4 detik","speaker":"MANUSIA","line":"Mau bawa aku ke neraka?!"},{"time":"4–7 detik","speaker":"IBLIS","line":"NANTI DULU, TARGET SUBSCRIBER-KU BELUM TERCAPAI!"},{"time":"7–10 detik","speaker":"MANUSIA","line":"Salah alamat, Bang. Aku juga masih berjuang!"}],"punchline":"Iblis duduk lemas karena manusia pun belum punya banyak subscriber.","ending":"Mereka saling menyemangati sambil menunjuk kamera.","cta_note":"CTA dan tema subscriber menyatu dengan cerita."}
    ]
    available = [item for item in pool if item["title"].casefold() not in recent]
    return random.choice(available or pool)


def enforce_cta(idea, language):
    """Keep a spoken subscribe CTA in the dialogue, even when the model forgets it."""
    dialogue = idea.get("dialogue") or []
    text = " ".join(str(d.get("line", "")) for d in dialogue).casefold()
    cta_terms = ("subscribe", "subscrib", "langgan", "ikuti channel", "ikuti saluran")
    if not any(term in text for term in cta_terms):
        lang = (language or "").casefold()
        if lang.startswith("english"):
            line = "You watched all that and still haven't subscribed?!"
        elif lang.startswith("bahasa indonesia"):
            line = "UDAH NONTON SAMPAI HABIS, TAPI BELUM SUBSCRIBE?!" 
        else:
            line = f"Remember to subscribe! ({language})"
        dialogue.append({"time":"akhir","speaker":"KARAKTER","line":line})
        idea["dialogue"] = dialogue
        idea["cta_note"] = "CTA subscribe otomatis ditambahkan ke dialog karena versi cerita sebelumnya belum memuat ajakan."
    else:
        idea.setdefault("cta_note", "CTA subscribe menyatu dengan lelucon.")
    return idea

with st.sidebar:
    st.header("Pengaturan")
    key = api_key()
    st.write("Gemini API:", "✅ Terhubung" if key else "⚠️ Belum diatur")
    model = st.text_input("Model Gemini", "gemini-3.5-flash-lite")
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
if "recent_titles" not in st.session_state: st.session_state.recent_titles = []
if st.button("🔥 GENERATE IDE BARU", type="primary", use_container_width=True):
    prior_titles = st.session_state.recent_titles[-12:]
    variation_seed = random.randint(100000, 999999)
    prompt = f"""Create ONE original YouTube Shorts idea designed to gain subscribers. Variation ID: {variation_seed}. It must be a genuinely new plot, not a rewrite.
OUTPUT LANGUAGE: {target_language}. Write the title, hook, story, dialogue, punchline, ending, hashtags, and cta_note in {target_language}. Do not use Indonesian unless Indonesian is the selected language. Keep wording natural for native speakers, culturally understandable, and not a literal translation.
Formula: an immediate surprising hook in 0–2 seconds; a curiosity-building story; a strong punchline; and a subscribe CTA naturally embedded in the joke. Characters may vary; do not rely only on ghosts. Visual style: {style}. Humor type: {humor}. Duration: {duration}. Avoid these ideas/characters: {avoid or 'none'}. Do not reuse these recent titles or their story premises: {prior_titles or 'none yet'}. Dialogue must fit the duration, use at most 3 characters, and have no long intro. Make each new idea meaningfully different.
Return valid JSON only with fields: title, hook, story, dialogue (array of objects with time, speaker, line), punchline, ending, hashtags, cta_note. Keep timing labels easy to understand. Make jokes understandable to viewers familiar with {target_language}."""
    try:
        if key: result = call_gemini(key, model, prompt)
        else: result = local_idea(st.session_state.recent_titles)
        result = enforce_cta(result, target_language)
        st.session_state.idea = prompts(result, style, duration, target_language)
        st.session_state.recent_titles = ([result.get("title", "")] + st.session_state.recent_titles)[:20]
    except Exception as e:
        st.error(f"Gemini gagal: {e}")
        st.info("Gemini sedang gagal. Ide cadangan lokal dipakai; judul dihindari agar tidak mengulang, dan CTA diperiksa otomatis.")
        fallback = local_idea(st.session_state.recent_titles)
        fallback = enforce_cta(fallback, target_language)
        st.session_state.idea = prompts(fallback, style, duration, target_language)
        st.session_state.recent_titles = ([fallback.get("title", "")] + st.session_state.recent_titles)[:20]

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
