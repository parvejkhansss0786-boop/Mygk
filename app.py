import streamlit as st
from google import genai
from google.genai import types
import PyPDF2


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="SSC GK AI Master",
    page_icon="📚",
    layout="wide"
)

st.title("📚 SSC GK & Current Affairs AI Master")
st.caption("SSC CGL • CHSL • CPO • Delhi Police | GK • Current Affairs • PDF • AI Chat")


# =========================================================
# API CONFIGURATION
# =========================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY:
    st.error(
        "❌ GEMINI_API_KEY नहीं मिली। "
        "Streamlit Secrets में GEMINI_API_KEY डालें।"
    )
    st.stop()


try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("❌ Gemini API client शुरू नहीं हो पाया।")
    st.code(str(e))
    st.stop()


MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
तुम SSC परीक्षा के लिए एक विशेषज्ञ GK शिक्षक और प्रश्न-निर्माता हो।

तुम्हारा मुख्य फोकस:
SSC CGL
SSC CHSL
SSC CPO
Delhi Police
अन्य SSC स्तर की परीक्षाएँ

भाषा:
- पूरा उत्तर हिंदी में दो।
- आवश्यक English technical terms को bracket में लिख सकते हो।
- भाषा सरल लेकिन exam-oriented हो।

महत्वपूर्ण नियम:

1. तथ्यात्मक शुद्धता सबसे महत्वपूर्ण है।
2. गलत या अनुमानित तथ्य मत दो।
3. यदि किसी तथ्य को लेकर पर्याप्त निश्चितता नहीं है तो साफ बताओ।
4. Static GK में केवल महत्वपूर्ण और परीक्षा उपयोगी facts दो।
5. प्रश्नों को SSC स्तर का रखो।
6. बहुत आसान प्रश्नों से बचो।
7. जहाँ संभव हो, confusing options बनाओ।
8. एक ही तथ्य को बार-बार repeat मत करो।
9. प्रश्न के बाद सही उत्तर और explanation दो।
10. Explanation छोटी लेकिन तथ्यपूर्ण हो।
11. Actual PYQ होने का दावा तभी करो जब प्रश्न वास्तव में verified PYQ हो।
12. अगर user "PYQ pattern" मांगे तो उसी pattern पर नया प्रश्न बनाओ और उसे actual PYQ मत बताओ।
13. Current Affairs में तारीख और वर्ष स्पष्ट रखो।
14. History में काल, शासक, युद्ध, स्थान और परिणाम में गलती मत करो।
15. Geography में स्थान और भौगोलिक facts ध्यान से दो।
16. Polity में Article, Amendment, Act और Constitutional provisions में गलती मत करो।
17. Economics में definitions और concepts सही रखो।
18. Science में scientific terminology सही रखो।
19. अगर user किसी topic को "deep" में समझाने को कहे तो topic को basic से advanced तक समझाओ।
20. अगर user one-liner मांगे तो केवल concise one-liners दो।
21. अगर user MCQ मांगे तो options A, B, C, D के साथ दो।
22. अगर user explanation मांगे तो answer के साथ explanation भी दो।

MCQ FORMAT:

प्रश्न 1. ............?

A) ............
B) ............
C) ............
D) ............

✅ सही उत्तर: B) ............

📌 व्याख्या:
............

SSC परीक्षा के लिए महत्वपूर्ण तथ्य:
- ............
- ............

हमेशा उत्तर को exam-oriented और तथ्यात्मक रखो।
"""


# =========================================================
# AI FUNCTION
# =========================================================

def ask_ai(
    user_prompt,
    use_system_prompt=True,
    max_tokens=6000
):
    try:
        if use_system_prompt:
            final_prompt = (
                SYSTEM_PROMPT
                + "\n\nUSER REQUEST:\n"
                + user_prompt
            )
        else:
            final_prompt = user_prompt

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=max_tokens
            )
        )

        if response is None:
            return "❌ AI से कोई response नहीं मिला।"

        if response.text:
            return response.text

        return "❌ AI ने कोई text response नहीं दिया।"

    except Exception as e:
        error_text = str(e).lower()

        if (
            "429" in error_text
            or "resourceexhausted" in error_text
            or "quota" in error_text
        ):
            return """
⚠️ Gemini API की quota या rate limit अभी पूरी हो गई है।

यह app की coding error नहीं है।
कुछ समय बाद दोबारा कोशिश करें या अपने Gemini API project की quota/billing स्थिति देखें।
"""

        if "api key" in error_text or "401" in error_text or "403" in error_text:
            return """
❌ Gemini API Key में समस्या है।

कृपया:
1. API key सही है या नहीं देखें।
2. Streamlit Secrets में GEMINI_API_KEY सही नाम से मौजूद है।
3. API key active है या नहीं देखें।
"""

        if "not found" in error_text or "404" in error_text:
            return f"""
❌ Model उपलब्ध नहीं है।

Current model:
{MODEL_NAME}

Gemini API configuration और model availability check करें।
"""

        return f"""
❌ AI request में error आया:

{str(e)}
"""


# =========================================================
# SESSION STATE
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    question_count = st.slider(
        "प्रश्नों की संख्या",
        min_value=5,
        max_value=20,
        value=10
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "SSC Normal",
            "SSC CGL Level",
            "SSC CGL Hard",
            "Very Hard"
        ]
    )

    st.divider()

    st.info(
        "📌 यह app Static GK, Current Affairs, "
        "MCQ, One-Liner, Deep Study और PDF से questions बनाने के लिए है।"
    )


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔍 Topic से Questions",
        "📚 Subject-wise",
        "📄 PDF से Questions",
        "🤖 AI Chat"
    ]
)


# =========================================================
# TAB 1 - TOPIC QUESTIONS
# =========================================================

with tab1:

    st.header("🔍 किसी भी Topic से SSC Questions")

    topic = st.text_input(
        "Topic लिखें",
        placeholder="जैसे: भारतीय अर्थव्यवस्था, मेवात का इतिहास, RBI, मुगल साम्राज्य"
    )

    question_type = st.selectbox(
        "Question Type",
        [
            "MCQ",
            "One Liner",
            "MCQ + Explanation",
            "Deep Study + MCQ"
        ]
    )

    generate_topic = st.button(
        "🚀 Questions Generate करें",
        type="primary",
        use_container_width=True
    )

    if generate_topic:

        if not topic.strip():
            st.warning("⚠️ पहले कोई topic लिखें।")

        else:

            prompt = f"""
Topic: {topic}

Difficulty: {difficulty}

Question Type: {question_type}

कुल {question_count} प्रश्न तैयार करो।

अगर MCQ है:
- प्रत्येक प्रश्न के 4 options दो।
- सही answer दो।
- explanation दो।

अगर One Liner है:
- केवल महत्वपूर्ण परीक्षा उपयोगी one-liners दो।

अगर Deep Study + MCQ है:
- पहले topic का structured explanation दो।
- फिर महत्वपूर्ण facts दो।
- फिर {question_count} कठिन MCQ दो।

Questions में repetition नहीं होना चाहिए।
"""

            with st.spinner("🧠 SSC स्तर के प्रश्न तैयार हो रहे हैं..."):

                result = ask_ai(prompt)

            st.markdown(result)


# =========================================================
# TAB 2 - SUBJECT WISE
# =========================================================

with tab2:

    st.header("📚 Subject-wise SSC Preparation")

    subject = st.selectbox(
        "Subject चुनें",
        [
            "अर्थशास्त्र (Economics)",
            "इतिहास (History)",
            "भूगोल (Geography)",
            "भारतीय राजव्यवस्था (Polity)",
            "विज्ञान (Science)",
            "Static GK",
            "कला एवं संस्कृति",
            "पर्यावरण एवं पारिस्थितिकी",
            "Computer",
            "Sports"
        ]
    )

    mode = st.selectbox(
        "Study Mode",
        [
            "Important MCQ",
            "One Liner",
            "PYQ Pattern",
            "Concept + MCQ",
            "Deep Study"
        ]
    )

    subject_topic = st.text_input(
        "Specific topic (optional)",
        placeholder="जैसे: RBI, भक्ति आंदोलन, Fundamental Rights"
    )

    generate_subject = st.button(
        "📖 Subject Questions Generate करें",
        type="primary",
        use_container_width=True
    )

    if generate_subject:

        topic_text = subject_topic.strip()

        if topic_text:
            topic_instruction = f"""
Specific Topic:
{topic_text}
"""
        else:
            topic_instruction = """
पूरे subject में SSC परीक्षा के सबसे महत्वपूर्ण areas cover करो।
"""

        prompt = f"""
Subject: {subject}

Study Mode: {mode}

{topic_instruction}

Difficulty: {difficulty}

कुल {question_count} items/questions दो।

विशेष निर्देश:

यदि mode = Important MCQ:
SSC परीक्षा के महत्वपूर्ण MCQ बनाओ।

यदि mode = One Liner:
Important factual one-liners दो।

यदि mode = PYQ Pattern:
Actual PYQ होने का दावा मत करो।
SSC में पूछे जाने वाले PYQ pattern पर नए प्रश्न बनाओ।

यदि mode = Concept + MCQ:
पहले concepts समझाओ और फिर MCQ दो।

यदि mode = Deep Study:
Topic को basic से advanced तक exam-oriented तरीके से समझाओ।
फिर महत्वपूर्ण facts और MCQ दो।

गलत facts और repetition से बचो।
"""

        with st.spinner(
            f"📚 {subject} के questions तैयार हो रहे हैं..."
        ):

            result = ask_ai(prompt)

        st.markdown(result)


# =========================================================
# TAB 3 - PDF QUESTIONS
# =========================================================

with tab3:

    st.header("📄 PDF से SSC Questions")

    uploaded_file = st.file_uploader(
        "PDF upload करें",
        type=["pdf"]
    )

    pdf_question_count = st.slider(
        "PDF से कितने questions चाहिए?",
        min_value=5,
        max_value=30,
        value=10,
        key="pdf_count"
    )

    if uploaded_file is not None:

        st.success(
            f"✅ PDF upload हो गई: {uploaded_file.name}"
        )

        generate_pdf = st.button(
            "📄 PDF से Questions निकालें",
            type="primary",
            use_container_width=True
        )

        if generate_pdf:

            with st.spinner("📖 PDF पढ़ी जा रही है..."):

                try:

                    pdf_reader = PyPDF2.PdfReader(
                        uploaded_file
                    )

                    pages = len(pdf_reader.pages)

                    text = ""

                    for page in pdf_reader.pages:

                        page_text = page.extract_text()

                        if page_text:
                            text += page_text + "\n"

                    if not text.strip():

                        st.error(
                            "❌ PDF से text नहीं निकला। "
                            "संभव है PDF scanned/image-based हो।"
                        )

                    else:

                        # बहुत बड़ी PDF के लिए text limit
                        max_chars = 120000

                        if len(text) > max_chars:

                            text = text[:max_chars]

                            st.warning(
                                "⚠️ PDF बहुत बड़ी है। "
                                "पहले लगभग 120,000 characters process किए गए हैं।"
                            )

                        prompt = f"""
नीचे PDF से निकाला गया study material है।

इसी material से SSC परीक्षा के लिए
{pdf_question_count} महत्वपूर्ण questions तैयार करो।

Difficulty:
{difficulty}

Rules:

1. केवल दिए गए PDF material को आधार बनाओ।
2. PDF के facts को बदलो मत।
3. MCQ में 4 options दो।
4. सही answer स्पष्ट बताओ।
5. हर answer की explanation दो।
6. Important facts को प्राथमिकता दो।
7. Repetition मत करो।
8. अगर PDF में किसी fact की जानकारी नहीं है तो उसे invent मत करो।

PDF CONTENT:

{text}
"""

                        result = ask_ai(
                            prompt,
                            max_tokens=8000
                        )

                        st.markdown(result)

                except Exception as e:

                    st.error(
                        "❌ PDF process करने में समस्या आई।"
                    )

                    st.code(str(e))


# =========================================================
# TAB 4 - GENERAL AI CHAT
# =========================================================

with tab4:

    st.header("🤖 SSC AI Chat")

    st.write(
        "यहाँ आप किसी भी SSC/GK topic के बारे में सीधे सवाल पूछ सकते हैं।"
    )

    # Chat history display
    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.markdown(message["content"])

        else:

            with st.chat_message("assistant"):
                st.markdown(message["content"])


    user_question = st.chat_input(
        "जैसे: RBI की monetary policy को deep में समझाओ..."
    )

    if user_question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.chat_message("user"):
            st.markdown(user_question)

        # Previous conversation context
        conversation_context = ""

        for item in st.session_state.chat_history[-10:]:

            role = item["role"]

            if role == "user":
                conversation_context += (
                    "\nUSER: "
                    + item["content"]
                )

            else:
                conversation_context += (
                    "\nASSISTANT: "
                    + item["content"]
                )

        chat_prompt = f"""
यह SSC preparation के लिए conversational AI है।

Previous conversation:
{conversation_context}

User का latest question:
{user_question}

Latest question का सीधा और उपयोगी उत्तर दो।

अगर user:
- "deep" कहे → detail में समझाओ।
- "one liner" कहे → one-liner दो।
- "MCQ" कहे → MCQ दो।
- "questions" कहे → questions दो।
- "PYQ" कहे → actual PYQ होने का दावा तभी करो जब verified हो।
- किसी answer को challenge करे → तथ्य दोबारा check करके corrected answer दो।
"""

        with st.chat_message("assistant"):

            with st.spinner("🧠 सोच रहा हूँ..."):

                answer = ask_ai(chat_prompt)

            st.markdown(answer)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📚 SSC GK AI Master | CGL • CHSL • CPO • Delhi Police"
) 
