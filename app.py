import streamlit as st
from google import genai
from google.genai import types
import PyPDF2
import time

# =========================================================
# APP SETTINGS
# =========================================================

st.set_page_config(
    page_title="SSC GK AI Master",
    page_icon="📚",
    layout="wide"
)

st.title("📚 SSC GK & Current Affairs AI Master")
st.caption(
    "SSC CGL • CHSL • CPO • Delhi Police | "
    "Static GK • Current Affairs • PDF Analysis"
)

# =========================================================
# API SETUP
# =========================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error(
        "❌ GEMINI_API_KEY नहीं मिली। "
        "Streamlit Secrets में अपनी API key डालें।"
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# वर्तमान मॉडल
MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# SSC MASTER PROMPT
# =========================================================

SYSTEM_PROMPT = """
तुम SSC CGL, CHSL, CPO और Delhi Police परीक्षा के लिए
एक अत्यंत अनुभवी GK शिक्षक और प्रश्न-निर्माता हो।

तुम्हारा मुख्य लक्ष्य है:
विद्यार्थी को सही, परीक्षा-उपयोगी और गहराई वाले प्रश्न तथा
उनके बिल्कुल स्पष्ट उत्तर देना।

भाषा:
- पूरा उत्तर हिंदी में हो।
- जरूरी English term को हिंदी के साथ bracket में लिख सकते हो।
- भाषा ऐसी हो जैसे एक अनुभवी शिक्षक विद्यार्थी को समझा रहा हो।

FACT CHECKING:
1. तथ्य गलत मत बनाओ।
2. अगर प्रश्न Current Affairs या बदलने वाला तथ्य है,
   तो उपलब्ध Google Search से सत्यापन करो।
3. दो स्रोतों में विरोध हो तो उसे छिपाओ मत।
4. तारीख, वर्ष, स्थान, व्यक्ति और पदनाम विशेष रूप से जाँचो।
5. अनुमान को तथ्य की तरह मत लिखो।
6. अगर तथ्य निश्चित नहीं है तो साफ लिखो कि इसकी पुष्टि आवश्यक है।

SSC LEVEL:
- केवल बहुत आसान सामान्य ज्ञान मत दो।
- SSC CGL/CHSL/CPO स्तर के प्रश्न बनाओ।
- विकल्पों में ऐसे तथ्य रखो जिनमें वास्तविक confusion हो।
- Static GK को प्राथमिकता दो।
- जरूरत पड़ने पर संबंधित इतिहास, भूगोल, अर्थशास्त्र,
  संविधान, विज्ञान और संस्कृति से connection बताओ।

हर MCQ का FORMAT:

प्रश्न 1. ...
(A) ...
(B) ...
(C) ...
(D) ...

✅ सही उत्तर: (B) ...

📌 व्याख्या:
...

🎯 SSC Exam Point:
...

अगर प्रश्न में कोई महत्वपूर्ण तथ्य है तो:
📚 याद रखने योग्य तथ्य:
...

अगर user सिर्फ किसी topic को समझने के लिए पूछता है,
तो पहले concept समझाओ और फिर examples/MCQs दो।

अगर user कहता है "one liner",
तो केवल छोटे और factual one-liners दो।

अगर user कहता है "deep",
तो topic को basic → advanced → exam facts → traps
के क्रम में समझाओ।

अगर user सिर्फ सामान्य सवाल पूछता है,
तो सामान्य ChatGPT की तरह सीधे और स्पष्ट उत्तर दो।
"""


# =========================================================
# AI FUNCTION
# =========================================================

def ask_ai(prompt, use_search=True):

    full_prompt = SYSTEM_PROMPT + "\n\nUSER REQUEST:\n" + prompt

    try:

        tools = []

        # Current / changing information के लिए Google Search
        if use_search:
            tools = [
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.25,
                tools=tools
            )
        )

        if response and response.text:
            return response.text

        return "AI ने कोई उत्तर नहीं दिया। कृपया दोबारा प्रयास करें।"

    except Exception as e:

        error_text = str(e).lower()

        if "429" in error_text or "resourceexhausted" in error_text:
            return (
                "⚠️ अभी AI API की quota/rate limit पूरी हो गई है।\n\n"
                "यह ऐप की programming error नहीं है। "
                "थोड़ी देर बाद दोबारा प्रयास करें या अपने Gemini "
                "project की quota/billing स्थिति देखें।"
            )

        if "api key" in error_text or "authentication" in error_text:
            return (
                "🔐 API Key में समस्या है। "
                "Streamlit Secrets में GEMINI_API_KEY जाँचें।"
            )

        return (
            "❌ AI से उत्तर लेते समय समस्या आई।\n\n"
            f"तकनीकी जानकारी: {str(e)}"
        )


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Topic से प्रश्न",
    "📚 Subject-wise",
    "📄 PDF से प्रश्न",
    "💬 कुछ भी पूछें"
])


# =========================================================
# TAB 1 — TOPIC QUESTIONS
# =========================================================

with tab1:

    st.subheader("🔍 किसी भी Topic से SSC Questions")

    topic = st.text_input(
        "Topic लिखें",
        placeholder=(
            "जैसे: भारत की राष्ट्रीय आय, मेवात का इतिहास, "
            "RBI, मौलिक अधिकार, सिंधु घाटी सभ्यता..."
        )
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "SSC CGL स्तर",
            "SSC CGL कठिन",
            "SSC CPO / Delhi Police कठिन",
            "बहुत कठिन"
        ]
    )

    number = st.slider(
        "कितने प्रश्न?",
        min_value=5,
        max_value=20,
        value=10
    )

    if st.button(
        "🚀 प्रश्न Generate करें",
        key="topic_btn",
        use_container_width=True
    ):

        if not topic.strip():
            st.warning("पहले Topic लिखें।")
        else:

            with st.spinner(
                "📚 Topic का analysis करके प्रश्न तैयार किए जा रहे हैं..."
            ):

                prompt = f"""
Topic: {topic}

Difficulty: {difficulty}

कुल प्रश्न: {number}

निर्देश:
- इस topic के सबसे महत्वपूर्ण SSC facts चुनो।
- प्रश्नों को दोहराना नहीं है।
- सही उत्तर की व्याख्या अवश्य दो।
- जहाँ आवश्यक हो current information को verify करो।
- पुराने/गलत facts का उपयोग मत करो।
"""

                result = ask_ai(prompt, use_search=True)

                st.markdown(result)


# =========================================================
# TAB 2 — SUBJECT WISE
# =========================================================

with tab2:

    st.subheader("📚 Subject-wise SSC Practice")

    subject = st.selectbox(
        "विषय चुनें",
        [
            "अर्थशास्त्र (Economics)",
            "इतिहास (History)",
            "भूगोल (Geography)",
            "भारतीय राजव्यवस्था (Polity)",
            "विज्ञान (Science)",
            "Static GK",
            "कला एवं संस्कृति",
            "पर्यावरण",
            "कंप्यूटर"
        ]
    )

    mode = st.selectbox(
        "Practice Type",
        [
            "Important Questions",
            "PYQ Pattern",
            "One Liner",
            "Concept + MCQ",
            "Deep Study"
        ]
    )

    if st.button(
        f"📖 {subject} शुरू करें",
        key="subject_btn",
        use_container_width=True
    ):

        with st.spinner(
            f"{subject} का SSC-level material तैयार हो रहा है..."
        ):

            prompt = f"""
विषय: {subject}

Practice Type: {mode}

इस विषय पर परीक्षा में उपयोगी सामग्री तैयार करो।

अगर PYQ Pattern चुना गया है:
- वास्तविक PYQ होने का दावा तभी करो जब verified हो।
- अन्यथा "PYQ Pattern" लिखो।

अगर One Liner चुना गया है:
- छोटे, factual और याद रखने योग्य points दो।

अगर Deep Study चुना गया है:
- Concept
- Important Facts
- SSC Traps
- One Liners
- MCQs
के क्रम में समझाओ।
"""

            result = ask_ai(prompt, use_search=True)

            st.markdown(result)


# =========================================================
# TAB 3 — PDF QUESTIONS
# =========================================================

with tab3:

    st.subheader("📄 PDF से SSC Questions")

    uploaded_file = st.file_uploader(
        "अपनी PDF upload करें",
        type=["pdf"]
    )

    if uploaded_file:

        st.info(
            f"📄 File: {uploaded_file.name}"
        )

        pdf_question_count = st.slider(
            "कितने प्रश्न चाहिए?",
            5,
            20,
            10,
            key="pdf_count"
        )

        if st.button(
            "🧠 PDF Analyze करें",
            key="pdf_btn",
            use_container_width=True
        ):

            with st.spinner(
                "📖 PDF पढ़ी जा रही है..."
            ):

                try:

                    reader = PyPDF2.PdfReader(
                        uploaded_file
                    )

                    pages = len(reader.pages)

                    text_parts = []

                    for page in reader.pages:

                        page_text = page.extract_text()

                        if page_text:
                            text_parts.append(page_text)

                    pdf_text = "\n".join(text_parts)

                    if not pdf_text.strip():
                        st.error(
                            "इस PDF से text नहीं निकाला जा सका। "
                            "अगर यह scanned/image PDF है तो OCR की जरूरत होगी।"
                        )
                        st.stop()

                    # बहुत बड़ी PDF से API request अनावश्यक रूप से बड़ी
                    # न हो इसलिए text को सीमित करते हैं।
                    pdf_text = pdf_text[:100000]

                    prompt = f"""
नीचे एक PDF के notes/text दिए गए हैं।

PDF से केवल वही facts लो जो वास्तव में text में मौजूद हैं।

कुल प्रश्न: {pdf_question_count}

काम:
1. सबसे महत्वपूर्ण परीक्षा वाले facts खोजो।
2. उनसे SSC-level MCQs बनाओ।
3. हर प्रश्न में 4 options हों।
4. सही उत्तर बताओ।
5. विस्तृत लेकिन आसान हिंदी explanation दो।
6. हर प्रश्न के बाद SSC Exam Point दो।
7. PDF में मौजूद तथ्य के बाहर मनगढ़ंत information मत जोड़ो।

PDF TEXT:

{pdf_text}
"""

                    result = ask_ai(
                        prompt,
                        use_search=False
                    )

                    st.markdown(result)

                except Exception as e:

                    st.error(
                        f"PDF पढ़ने में समस्या आई: {str(e)}"
                    )


# =========================================================
# TAB 4 — GENERAL AI CHAT
# =========================================================

with tab4:

    st.subheader("💬 कुछ भी पूछें")

    user_question = st.text_area(
        "अपना सवाल लिखें",
        placeholder=(
            "जैसे:\n"
            "भारत में राष्ट्रीय आय की गणना कैसे होती है?\n"
            "मेवात का इतिहास deep में समझाओ\n"
            "RBI के बारे में SSC CGL level पर बताओ\n"
            "मुझे 20 economics one-liners दो"
        ),
        height=180
    )

    if st.button(
        "🤖 AI से पूछें",
        key="chat_btn",
        use_container_width=True
    ):

        if not user_question.strip():

            st.warning("पहले अपना सवाल लिखें।")

        else:

            with st.spinner(
                "🤖 जवाब तैयार किया जा रहा है..."
            ):

                result = ask_ai(
                    user_question,
                    use_search=True
                )

                st.markdown(result)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📚 SSC GK AI Master | CGL • CHSL • CPO • Delhi Police"
)

"requirements.txt"

:::writing{variant="document" id="74106" title="requirements.txt"}

streamlit
google-genai
PyPDF2

Streamlit Secrets

अपने Streamlit project में Secrets में यह रखना है:

GEMINI_API_KEY = "तुम्हारी_Gemini_API_key"

API key को "app.py" में सीधे मत लिखना।

इसमें क्या बेहतर किया है?

- पुराना "google.generativeai" हटाया → नया "google-genai" SDK।
- "gemini-pro" हटाया → वर्तमान model इस्तेमाल किया।
- Google Search grounding जोड़ा, इसलिए current affairs जैसे बदलने वाले facts को web से verify कराया जा सकता है।
- गलत fact बनाने से रोकने के लिए strict prompt।
- हर MCQ में उत्तर + explanation + SSC Exam Point।
- Topic / Subject / PDF / सामान्य सवाल चारों modes।
- "429 / quota" आने पर app crash होने के बजाय साफ message देगा।
- PDF text पढ़कर उसी से questions बनाएगा।
- "PYQ Pattern" में AI को असली PYQ होने का झूठा दावा करने से रोका है।
- Current facts और historical/static facts को अलग तरह से handle किया है।

एक महत्वपूर्ण सीमा: कोई code API quota को असीमित नहीं बना सकता। अगर Gemini project की quota सच में समाप्त हो जाए तो server भी उसी API से उत्तर नहीं निकाल पाएगा। इसलिए मैंने quota को bypass करने के बजाय graceful error handling रखा है। Google की वर्तमान documentation भी model/SDK migration और rate-limit handling को अलग concern मानती है।

और तुम्हारे “जैसे मैं तुमसे बात करता हूँ, वैसे answer दे” वाले हिस्से के लिए "💬 कुछ भी पूछें" वाला tab रखा है—वहाँ तुम सामान्य भाषा में लिख सकते हो, जैसे “Economics zero se deep me samjha”, और उसी तरह structured explanation मिलेगा
 
