 import streamlit as st
import PyPDF2
import re
import random

st.set_page_config(
    page_title="SSC GK Search AI",
    page_icon="📚",
    layout="wide"
)

st.title("📚 SSC GK Search Master")
st.caption("No API Key • Local Knowledge • PDF Search • MCQ")


# =========================================================
# BUILT-IN SSC KNOWLEDGE
# =========================================================

KNOWLEDGE = {
    "rbi": """
RBI की स्थापना 1 अप्रैल 1935 को हुई थी।
RBI का मुख्यालय मुंबई में है।
RBI भारत का केंद्रीय बैंक है।
RBI की स्थापना RBI Act, 1934 के तहत हुई।
RBI मौद्रिक नीति से संबंधित महत्वपूर्ण कार्य करता है।
""",

    "संविधान": """
भारत का संविधान 26 नवंबर 1949 को अंगीकृत किया गया।
भारत का संविधान 26 जनवरी 1950 को लागू हुआ।
भारतीय संविधान की प्रस्तावना में भारत को Sovereign Socialist Secular Democratic Republic कहा गया है।
मौलिक अधिकार संविधान के भाग III में हैं।
राज्य के नीति-निदेशक तत्व भाग IV में हैं।
मौलिक कर्तव्य भाग IVA में हैं।
""",

    "अर्थशास्त्र": """
GDP का अर्थ Gross Domestic Product है।
मुद्रास्फीति का सामान्य अर्थ वस्तुओं और सेवाओं के सामान्य मूल्य स्तर में वृद्धि है।
RBI भारत का केंद्रीय बैंक है।
राजकोषीय नीति सरकार के कर और व्यय से संबंधित नीति है।
मौद्रिक नीति केंद्रीय बैंक द्वारा मुद्रा और ऋण की स्थिति को प्रभावित करने की नीति है।
""",

    "इतिहास": """
1857 का विद्रोह भारत के इतिहास की महत्वपूर्ण घटना थी।
भारतीय राष्ट्रीय कांग्रेस की स्थापना 1885 में हुई।
असहयोग आंदोलन 1920 में शुरू हुआ।
सविनय अवज्ञा आंदोलन 1930 में शुरू हुआ।
भारत छोड़ो आंदोलन 1942 में शुरू हुआ।
""",

    "भूगोल": """
भारत का क्षेत्रफल लगभग 32.87 लाख वर्ग किलोमीटर है।
भारत की सबसे लंबी नदी प्रणाली गंगा नदी प्रणाली है।
हिमालय भारत के उत्तर में स्थित प्रमुख पर्वत प्रणाली है।
भारतीय मानसून भारत की जलवायु का महत्वपूर्ण भाग है।
""",

    "विज्ञान": """
प्रकाश संश्लेषण पौधों में होने वाली महत्वपूर्ण जैविक प्रक्रिया है।
मानव शरीर में हृदय रक्त का परिसंचरण करता है।
जल का रासायनिक सूत्र H2O है।
बल की SI इकाई न्यूटन है।
ऊर्जा की SI इकाई जूल है।
""",

    "computer": """
CPU का पूरा नाम Central Processing Unit है।
RAM का पूरा नाम Random Access Memory है।
ROM का पूरा नाम Read Only Memory है।
HTML का पूरा नाम HyperText Markup Language है।
WWW का पूरा नाम World Wide Web है।
""",

    "पर्यावरण": """
पारिस्थितिकी जीवों और उनके पर्यावरण के बीच संबंधों का अध्ययन है।
जैव विविधता का अर्थ जीवों की विविधता से है।
ग्रीनहाउस गैसें पृथ्वी के ताप संतुलन को प्रभावित करती हैं।
""",

    "कला संस्कृति": """
भरतनाट्यम तमिलनाडु से संबंधित प्रमुख शास्त्रीय नृत्य है।
कथक का विकास उत्तर भारत में प्रमुख रूप से हुआ।
कथकली केरल की प्रमुख नृत्य-नाट्य परंपरा है।
ओडिसी ओडिशा का प्रमुख शास्त्रीय नृत्य है।
"""
}


# =========================================================
# SEARCH ENGINE
# =========================================================

def search_knowledge(query):

    query = query.lower().strip()

    results = []

    for topic, text in KNOWLEDGE.items():

        if (
            query in topic.lower()
            or query in text.lower()
        ):
            results.append(
                (topic, text)
            )

    # individual sentences
    for topic, text in KNOWLEDGE.items():

        sentences = re.split(
            r"[।\n]",
            text
        )

        for sentence in sentences:

            if query and query in sentence.lower():

                results.append(
                    (topic, sentence.strip())
                )

    # remove duplicates
    final = []

    seen = set()

    for topic, text in results:

        key = text.strip()

        if key and key not in seen:

            seen.add(key)

            final.append(
                (topic, key)
            )

    return final


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf(file):

    reader = PyPDF2.PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text


def search_pdf(text, query):

    sentences = re.split(
        r"[।\n]",
        text
    )

    results = []

    query_words = query.lower().split()

    for sentence in sentences:

        sentence_clean = sentence.strip()

        if not sentence_clean:
            continue

        sentence_lower = sentence_clean.lower()

        matches = sum(
            1
            for word in query_words
            if word in sentence_lower
        )

        if matches > 0:

            results.append(
                (matches, sentence_clean)
            )

    results.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        text
        for score, text in results[:10]
    ]


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🔎 Search",
        "📄 PDF Search",
        "📝 MCQ"
    ]
)


# =========================================================
# SEARCH
# =========================================================

with tab1:

    st.header("🔎 SSC Knowledge Search")

    query = st.text_input(
        "अपना सवाल या keyword लिखें",
        placeholder="जैसे RBI क्या है?"
    )

    if st.button(
        "🔍 Search करें",
        type="primary"
    ):

        if not query.strip():

            st.warning(
                "पहले सवाल लिखें।"
            )

        else:

            results = search_knowledge(
                query
            )

            if results:

                st.success(
                    f"{len(results)} result मिले"
                )

                for topic, answer in results:

                    st.markdown(
                        f"### 📌 {topic}"
                    )

                    st.write(
                        answer
                    )

                    st.divider()

            else:

                st.warning(
                    "इस सवाल का answer अभी built-in knowledge में नहीं मिला।"
                )

                st.info(
                    "PDF upload करके PDF Search से भी खोज सकते हो।"
                )


# =========================================================
# PDF SEARCH
# =========================================================

with tab2:

    st.header("📄 PDF से Answer Search")

    pdf = st.file_uploader(
        "अपनी SSC PDF upload करें",
        type=["pdf"]
    )

    if pdf:

        with st.spinner(
            "PDF पढ़ी जा रही है..."
        ):

            try:

                pdf_text = extract_pdf(
                    pdf
                )

                st.success(
                    "✅ PDF तैयार है।"
                )

            except Exception as e:

                st.error(
                    "PDF पढ़ने में समस्या आई।"
                )

                st.stop()


        pdf_query = st.text_input(
            "PDF में क्या search करना है?",
            placeholder="जैसे RBI, 1857, Fundamental Rights"
        )


        if st.button(
            "🔎 PDF Search करें"
        ):

            if not pdf_query.strip():

                st.warning(
                    "पहले search शब्द लिखें।"
                )

            else:

                results = search_pdf(
                    pdf_text,
                    pdf_query
                )

                if results:

                    st.success(
                        f"{len(results)} relevant results मिले"
                    )

                    for result in results:

                        st.write(
                            "📌 " + result
                        )

                        st.divider()

                else:

                    st.warning(
                        "PDF में matching information नहीं मिली।"
                    )


# =========================================================
# MCQ
# =========================================================

with tab3:

    st.header(
        "📝 SSC Practice MCQ"
    )

    mcq_data = [

        (
            "RBI की स्थापना किस वर्ष हुई?",
            [
                "1935",
                "1947",
                "1950",
                "1969"
            ],
            "1935"
        ),

        (
            "भारत का संविधान कब लागू हुआ?",
            [
                "15 अगस्त 1947",
                "26 नवंबर 1949",
                "26 जनवरी 1950",
                "2 अक्टूबर 1950"
            ],
            "26 जनवरी 1950"
        ),

        (
            "CPU का पूरा नाम क्या है?",
            [
                "Central Processing Unit",
                "Central Program Unit",
                "Computer Processing Unit",
                "Control Processing Unit"
            ],
            "Central Processing Unit"
        ),

        (
            "बल की SI इकाई क्या है?",
            [
                "जूल",
                "वाट",
                "न्यूटन",
                "पास्कल"
            ],
            "न्यूटन"
        ),

        (
            "भारत छोड़ो आंदोलन किस वर्ष शुरू हुआ?",
            [
                "1919",
                "1920",
                "1930",
                "1942"
            ],
            "1942"
        )
    ]


    number = st.slider(
        "कितने प्रश्न?",
        1,
        len(mcq_data),
        5
    )


    selected = random.sample(
        mcq_data,
        number
    )


    for i, (question, options, answer) in enumerate(
        selected,
        start=1
    ):

        st.markdown(
            f"### प्रश्न {i}. {question}"
        )

        user_answer = st.radio(
            "उत्तर चुनें:",
            options,
            key=f"mcq_{i}"
        )


        if st.button(
            f"Answer देखें {i}",
            key=f"answer_{i}"
        ):

            if user_answer == answer:

                st.success(
                    f"✅ सही उत्तर: {answer}"
                )

            else:

                st.error(
                    f"❌ गलत। सही उत्तर: {answer}"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📚 SSC GK Search Master | "
    "No API Key Required"
)
