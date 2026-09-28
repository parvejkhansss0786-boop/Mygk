import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
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
st.caption(
    "SSC CGL • CHSL • CPO • Delhi Police | "
    "GK • Current Affairs • PDF • AI Chat"
)


# =========================================================
# API KEYS
# =========================================================

def get_secret(name):
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")
GROQ_API_KEY = get_secret("GROQ_API_KEY")


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
तुम SSC परीक्षा के लिए एक विशेषज्ञ GK शिक्षक और प्रश्न-निर्माता हो।

मुख्य फोकस:
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
3. किसी तथ्य पर पर्याप्त certainty न हो तो साफ बताओ।
4. Static GK में महत्वपूर्ण exam-oriented facts दो।
5. प्रश्न SSC स्तर के रखो।
6. बहुत आसान प्रश्नों से बचो।
7. जहाँ संभव हो confusing options बनाओ।
8. एक ही तथ्य को बार-बार repeat मत करो।
9. प्रश्न के बाद सही उत्तर और explanation दो।
10. Explanation छोटी लेकिन तथ्यपूर्ण हो।
11. Actual PYQ होने का दावा तभी करो जब verified हो।
12. "PYQ pattern" में नया प्रश्न बनाओ और उसे actual PYQ मत बताओ।
13. Current Affairs में तारीख और वर्ष स्पष्ट रखो।
14. History में काल, शासक, युद्ध, स्थान और परिणाम में गलती मत करो।
15. Geography के facts ध्यान से दो।
16. Polity में Article, Amendment, Act और Constitutional provisions सही रखो।
17. Economics में definitions और concepts सही रखो।
18. Science में scientific terminology सही रखो।
19. "Deep" में basic से advanced तक समझाओ।
20. "One liner" में concise one-liners दो।
21. MCQ में A, B, C, D options दो।
22. Explanation मांगने पर answer और explanation दोनों दो।

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

हमेशा उत्तर exam-oriented और तथ्यात्मक रखो।
"""


# =========================================================
# AI PROVIDERS
# =========================================================

providers = []


# ---------------- GEMINI ----------------

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        providers.append({
            "name": "Google Gemini",
            "type": "gemini",
            "client": gemini_client,
            "models": [
                "gemini-2.5-flash",
                "gemini-2.5-pro"
            ]
        })

    except Exception:
        pass


# ---------------- OPENAI ----------------

if OPENAI_API_KEY:

    try:

        openai_client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        providers.append({
            "name": "OpenAI",
            "type": "openai",
            "client": openai_client,
            "models": [
                "gpt-5",
                "gpt-5-mini"
            ]
        })

    except Exception:
        pass


# ---------------- OPENROUTER ----------------

if OPENROUTER_API_KEY:

    try:

        openrouter_client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        providers.append({
            "name": "OpenRouter",
            "type": "openrouter",
            "client": openrouter_client,
            "models": [
                "openai/gpt-5",
                "anthropic/claude-sonnet-4",
                "google/gemini-2.5-pro",
                "google/gemini-2.5-flash"
            ]
        })

    except Exception:
        pass


# ---------------- GROQ ----------------

if GROQ_API_KEY:

    try:

        groq_client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        providers.append({
            "name": "Groq",
            "type": "groq",
            "client": groq_client,
            "models": [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant"
            ]
        })

    except Exception:
        pass


# =========================================================
# AI FUNCTION WITH AUTOMATIC FALLBACK
# =========================================================

def ask_ai(
    user_prompt,
    use_system_prompt=True,
    max_tokens=6000
):

    if use_system_prompt:

        final_prompt = (
            SYSTEM_PROMPT
            + "\n\nUSER REQUEST:\n"
            + user_prompt
        )

    else:

        final_prompt = user_prompt


    if not providers:

        return """
❌ कोई AI API configured नहीं है।

Streamlit Secrets में कम से कम एक API key डालें:

GEMINI_API_KEY
OPENAI_API_KEY
OPENROUTER_API_KEY
GROQ_API_KEY
"""


    errors = []


    # =====================================================
    # PROVIDER → MODEL FALLBACK
    # =====================================================

    for provider in providers:

        provider_name = provider["name"]
        provider_type = provider["type"]
        client = provider["client"]


        for model in provider["models"]:

            try:

                # =========================================
                # GEMINI
                # =========================================

                if provider_type == "gemini":

                    response = client.models.generate_content(

                        model=model,

                        contents=final_prompt,

                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=max_tokens
                        )
                    )

                    if response and response.text:

                        return response.text


                # =========================================
                # OPENAI / OPENROUTER / GROQ
                # =========================================

                else:

                    response = client.chat.completions.create(

                        model=model,

                        messages=[
                            {
                                "role": "system",
                                "content": SYSTEM_PROMPT
                            },
                            {
                                "role": "user",
                                "content": user_prompt
                            }
                        ],

                        temperature=0.2,

                        max_tokens=max_tokens
                    )


                    if response.choices:

                        answer = (
                            response
                            .choices[0]
                            .message
                            .content
                        )

                        if answer:

                            return answer


            except Exception as e:

                errors.append(
                    f"{provider_name} / {model}: "
                    f"{str(e)[:300]}"
                )

                continue


    # =====================================================
    # ALL PROVIDERS FAILED
    # =====================================================

    return """
⚠️ सभी configured AI providers से response नहीं मिला।

संभावित कारण:

• API quota समाप्त
• API key invalid
• Model unavailable
• Rate limit
• Provider server समस्या
• Internet/API connection समस्या

App ने उपलब्ध providers और fallback models को try किया।

Technical details:

""" + "\n".join(errors[-10:])


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

    st.subheader("🤖 AI Providers")

    if providers:

        for provider in providers:

            st.success(
                "✓ " + provider["name"]
            )

    else:

        st.error(
            "कोई API configured नहीं है"
        )

    st.divider()

    st.info(
        "📌 Static GK, Current Affairs, MCQ, "
        "One-Liner, Deep Study और PDF Questions"
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
# TAB 1
# =========================================================

with tab1:

    st.header(
        "🔍 किसी भी Topic से SSC Questions"
    )

    topic = st.text_input(
        "Topic लिखें",
        placeholder=(
            "जैसे: भारतीय अर्थव्यवस्था, "
            "मेवात का इतिहास, RBI, मुगल साम्राज्य"
        )
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

            st.warning(
                "⚠️ पहले कोई topic लिखें।"
            )

        else:

            prompt = f"""
Topic: {topic}

Difficulty: {difficulty}

Question Type: {question_type}

कुल {question_count} प्रश्न तैयार करो।

अगर MCQ है:
- 4 options दो।
- सही answer दो।
- explanation दो।

अगर One Liner है:
- केवल महत्वपूर्ण परीक्षा उपयोगी one-liners दो।

अगर Deep Study + MCQ है:
- पहले structured explanation दो।
- फिर important facts दो।
- फिर {question_count} कठिन MCQ दो।

Questions में repetition नहीं होना चाहिए।
"""

            with st.spinner(
                "🧠 SSC स्तर के प्रश्न तैयार हो रहे हैं..."
            ):

                result = ask_ai(prompt)

            st.markdown(result)


# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.header(
        "📚 Subject-wise SSC Preparation"
    )

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
        placeholder=(
            "जैसे: RBI, भक्ति आंदोलन, "
            "Fundamental Rights"
        )
    )

    generate_subject = st.button(
        "📖 Subject Questions Generate करें",
        type="primary",
        use_container_width=True
    )


    if generate_subject:

        if subject_topic.strip():

            topic_instruction = f"""
Specific Topic:
{subject_topic.strip()}
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

यदि mode = Important MCQ:
SSC परीक्षा के महत्वपूर्ण MCQ बनाओ।

यदि mode = One Liner:
Important factual one-liners दो।

यदि mode = PYQ Pattern:
Actual PYQ होने का दावा मत करो।
SSC PYQ pattern पर नए प्रश्न बनाओ।

यदि mode = Concept + MCQ:
पहले concepts समझाओ और फिर MCQ दो।

यदि mode = Deep Study:
Topic को basic से advanced तक समझाओ।
फिर important facts और MCQ दो।

गलत facts और repetition से बचो।
"""


        with st.spinner(
            f"📚 {subject} के questions तैयार हो रहे हैं..."
        ):

            result = ask_ai(prompt)

        st.markdown(result)


# =========================================================
# TAB 3 - PDF
# =========================================================

with tab3:

    st.header(
        "📄 PDF से SSC Questions"
    )

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
            f"✅ PDF upload हो गई: "
            f"{uploaded_file.name}"
        )

        generate_pdf = st.button(
            "📄 PDF से Questions निकालें",
            type="primary",
            use_container_width=True
        )


        if generate_pdf:

            with st.spinner(
                "📖 PDF पढ़ी जा रही है..."
            ):

                try:

                    pdf_reader = PyPDF2.PdfReader(
                        uploaded_file
                    )

                    text = ""

                    for page in pdf_reader.pages:

                        page_text = page.extract_text()

                        if page_text:

                            text += (
                                page_text
                                + "\n"
                            )


                    if not text.strip():

                        st.error(
                            "❌ PDF से text नहीं निकला। "
                            "संभव है PDF scanned/image-based हो।"
                        )

                    else:

                        max_chars = 120000

                        if len(text) > max_chars:

                            text = text[:max_chars]

                            st.warning(
                                "⚠️ PDF बहुत बड़ी है। "
                                "पहले 120,000 characters process किए गए हैं।"
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
8. PDF में जानकारी न हो तो invent मत करो।

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

                    st.code(
                        str(e)
                    )


# =========================================================
# TAB 4 - AI CHAT
# =========================================================

with tab4:

    st.header(
        "🤖 SSC AI Chat"
    )

    st.write(
        "यहाँ किसी भी SSC/GK topic के बारे में सीधे सवाल पूछें।"
    )


    # -----------------------------------------------
    # DISPLAY HISTORY
    # -----------------------------------------------

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message("assistant"):

                st.markdown(
                    message["content"]
                )


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

            st.markdown(
                user_question
            )


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
- किसी answer को challenge करे → उपलब्ध जानकारी के आधार पर दोबारा जांचकर corrected answer दो।
"""


        with st.chat_message("assistant"):

            with st.spinner(
                "🧠 AI सोच रहा है..."
            ):

                answer = ask_ai(
                    chat_prompt
                )

            st.markdown(
                answer
            )


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
    "📚 SSC GK AI Master | "
    "CGL • CHSL • CPO • Delhi Police | "
    "Multi-AI Fallback System"
            )
