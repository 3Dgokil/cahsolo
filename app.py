import os, json, random, requests
import streamlit as st

st.set_page_config(page_title="Shorts Subscriber Studio", page_icon="🔥", layout="wide")
st.title("🔥 Shorts Subscriber Studio")
st.caption("DILIHAT → BERTAHAN → KEMBALI | Fokus: mencari subscriber")

BASE_URL = "https://clariohub.id/v1"

def api_key():
    try:
        if st.secrets.get("CLARIOHUB_API_KEY"): return st.secrets["CLARIOHUB_API_KEY"]
    except Exception: pass
    return os.getenv("CLARIOHUB_API_KEY", "")

def call_gemini(key, model, prompt):
    # ClarioHub menggunakan endpoint OpenAI-compatible Chat Completions.
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert YouTube Shorts comedy writer. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.95,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
    if not r.ok:
        payload.pop("response_format", None)
        r = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
    if not r.ok:
        try: msg = r.json().get("error", {}).get("message", r.text)
        except Exception: msg = r.text
        raise RuntimeError(f"ClarioHub API {r.status_code}: {msg}")
    try:
        txt = r.json()["choices"][0]["message"]["content"].strip()
        if txt.startswith("```"):
            import re
            txt = re.sub(r"^```(?:json)?\s*", "", txt, flags=re.IGNORECASE)
            txt = re.sub(r"\s*```$", "", txt)
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            start, end = txt.find("{"), txt.rfind("}")
            if start >= 0 and end > start:
                return json.loads(txt[start:end + 1])
            raise
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Respons ClarioHub tidak sesuai format Chat Completions.") from exc

def prompts(x, style, duration):
    dialogue = "\\n".join(f'{d.get("time","")} {d.get("speaker","")}: "{d.get("line","")}"' for d in x.get("dialogue",[]))
    x["flow_prompt"] = f"""Create a {duration} vertical 9:16 {style} YouTube Short.
GOAL: a highly memorable 10-second Indonesian horror-comedy Short that earns subscribers.
TIMING IS STRICT: 0.0s starts with the hook/action immediately; 0–2s hook; 2–5s conflict; 5–8s unexpected twist; 8–10s spoken subscribe CTA fused with the punchline.
HOOK 0–2s: {x.get('hook','')}
STORY: {x.get('story','')}
DIALOGUE (speak exactly these lines, in order):
{dialogue}
PUNCHLINE: {x.get('punchline','')}
ENDING: {x.get('ending','')}
Create ONE continuous, coherent vertical 9:16 scene that completes within 10 seconds. Start on the most surprising action in the first frame; no intro, no establishing shot, no slow walking, no pauses. Fast but intelligible timing, natural Indonesian voices, accurate lip-sync, expressive faces, clear body language, sharp cinematic visuals. The final spoken line must contain the story-specific subscribe joke/CTA; make the character address the viewer/camera if appropriate. Do not add, omit, reorder, or paraphrase dialogue. No extra scene after the punchline. No gore, subtitles, text overlays, logos, or watermark."""
    x["thumbnail_prompt"] = f"""Create a bold, cinematic vertical 9:16 YouTube Shorts thumbnail for Indonesian comedy: {x.get('title','')}. Main moment: {x.get('hook','')}. Exaggerated funny/shocked faces, one character close to camera, another reacting in the background, dramatic lighting, high contrast, sharp readable composition on a phone. Leave clear space at bottom for large Indonesian title text. No logos, no watermark, no gore."""
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
    st.write("ClarioHub API:", "✅ Key tersedia" if key else "⚠️ Belum diatur")
    model = st.selectbox("Model ClarioHub", ["clario/gemini-3.7-flash", "clario/deepseek-v4-pro", "clario/deepseek-v4-flash"], index=0)
    style = st.selectbox("Gaya visual", ["Horor-komedi realistis","Komedi absurd realistis","Hantu + manusia","Karakter bebas"])
    duration = st.selectbox("Durasi Google Flow", ["8 detik","10 detik"], index=1)
    humor = st.selectbox("Jenis humor", ["Absurd dan mengejutkan","Roasting lucu","Salah paham kocak","Plot twist"])
    avoid = st.text_input("Hindari ide/karakter (opsional)")

if "idea" not in st.session_state: st.session_state.idea = None
if st.button("🔥 GENERATE IDE BARU", type="primary", use_container_width=True):
    prompt = f"""Kamu penulis utama YouTube Shorts horor-komedi Indonesia yang fokus meningkatkan subscriber.
Buat SATU cerita BARU, padat, kuat, dan langsung bisa diproduksi di Google Flow. Batas video maksimal 10 detik.
ATURAN WAJIB:
1. DETIK 0.0 langsung ada aksi/visual mengejutkan dan dialog pendek yang menghentak. DILARANG intro, berjalan lama, memperkenalkan karakter, atau menjelaskan latar.
2. Konflik langsung terbaca secara visual. Maksimal 2 karakter berbicara; maksimal 4 giliran dialog; setiap kalimat pendek dan mudah diucapkan.
3. Pada detik 5–8 harus ada TWIST yang membalik keadaan atau mengejutkan penonton. Jangan gunakan punchline generik.
4. Pada detik 8–10 masukkan CTA SUBSCRIBE yang diucapkan karakter dan menyatu dengan punchline/roasting, bukan teks tempelan atau permintaan biasa. CTA harus spesifik pada kejadian cerita, lucu, emosional, dan mudah diingat.
5. Hindari pola usang/berulang seperti hantu mengeluh tidak punya channel kecuali diminta secara eksplisit. Jangan meniru judul, hook, punchline, atau CTA dari ide sebelumnya. Pilih premis, karakter, konflik, dan pembalikan yang berbeda.
6. Visual harus bisa dipahami tanpa penjelasan panjang. Akhiri pada reaksi/twist yang jelas; jangan menambahkan adegan baru setelah punchline.
Gaya visual: {style}. Jenis humor: {humor}. Durasi target: {duration}. Hindari ide/karakter: {avoid or 'tidak ada'}.
Buat dialog sesuai garis waktu total maksimal 10 detik. Gunakan bahasa Indonesia lisan yang natural, tajam, dan tidak bertele-tele. Cerita harus punya alasan komedi yang jelas, bukan sekadar hantu muncul lalu orang berteriak.
Keluarkan JSON valid saja, tanpa Markdown, dengan fields: title, hook, story, dialogue (array berisi time, speaker, line), punchline, ending, hashtags, cta_note.
Pastikan CTA benar-benar ada di salah satu line dialogue. cta_note menjelaskan kenapa CTA cocok dengan punchline."""

    try:
        if key: result = call_gemini(key, model, prompt)
        else: result = local_idea()
        st.session_state.idea = prompts(result, style, duration)
    except Exception as e:
        st.error(f"ClarioHub gagal: {e}")
        st.info("Menampilkan ide lokal. Periksa CLARIOHUB_API_KEY, saldo/kuota, atau nama model.")
        st.session_state.idea = prompts(local_idea(), style, duration)

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
    st.write("Target: hook kuat → cerita menarik → punchline ngena → alasan untuk subscribe.")
