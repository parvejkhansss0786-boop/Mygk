import streamlit as st
import google.generativeai as genai
import PyPDF2

# ऐप की सेटिंग और डिज़ाइन
st.set_page_config(page_title="SSC GK AI Master", page_icon="📚", layout="wide")
st.title("📚 SSC GK & Current Affairs AI")
st.write("SSC एग्जामिनर के नजरिए से स्टेटिक GK, करंट अफेयर्स और PDF से महत्वपूर्ण प्रश्न")

# API Key इनपुट
API_KEY = st.text_input("अपनी Google Gemini API Key डालें:", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # AI का अपडेटेड SSC Examiner माइंडसेट
    system_prompt = """
    तुम एक बेहद अनुभवी SSC (CGL, CHSL, CPO) एग्जामिनर हो। तुम्हारा काम दिए गए टॉपिक, विषय या PDF नोट्स से परीक्षा स्तर के प्रश्न बनाना है।
    तुम्हें इन बातों का सख्ती से पालन करना है:
    1. **स्टैटिक जीके (Static GK) पर सबसे ज्यादा फोकस करें:** प्रश्न सीधे, तथ्यात्मक (Factual) और गहराई वाले होने चाहिए।
    2. **करंट अफेयर्स को स्टैटिक से जोड़ें:** यदि कोई हालिया घटना है, तो उसके पीछे की ऐतिहासिक या भौगोलिक पृष्ठभूमि से सवाल पूछें।
    3. सवाल बहुत ज्यादा आसान न हों, थोड़ा घुमावदार हों। विकल्पों (Options) के बीच भ्रम हो।
    4. विकिपीडिया और प्रामाणिक एजुकेशन साइट्स के एकदम सटीक फैक्ट्स का ही उपयोग करें।
    5. सारे सवाल, उनके सही जवाब और विस्तार से व्याख्या (Explanation) सिर्फ 'हिंदी' भाषा में दें।
    """

    # ऐप को 3 हिस्सों (Tabs) में बांटा गया है
    tab1, tab2, tab3 = st.tabs(["🔍 टॉपिक से प्रश्न", "📘 विषय-अनुसार", "📄 PDF से सवाल"])

    # फीचर 1: किसी विशेष टॉपिक से सवाल
    with tab1:
        st.subheader("किसी भी टॉपिक के महत्वपूर्ण प्रश्न")
        topic = st.text_input("टॉपिक का नाम लिखें (जैसे: भारत की राष्ट्रीय आय, मेवात का इतिहास, बैंकिंग प्रणाली):")
        
        if st.button("टॉपिक के प्रश्न जनरेट करें") and topic:
            with st.spinner('SSC के पैटर्न पर सटीक प्रश्न तैयार किए जा रहे हैं...'):
                prompt = f"{system_prompt}\n\nटॉपिक: {topic}\nइस टॉपिक पर SSC स्तर के 5-10 कठिन प्रश्न, उनके विकल्प और सही उत्तर व्याख्या के साथ बनाएं।"
                response = model.generate_content(prompt)
                st.write(response.text)

    # फीचर 2: विषय अनुसार (Subject-wise) प्रश्न और प्रैक्टिस सेट
    with tab2:
        st.subheader("विषय चुनें और प्रश्न प्राप्त करें")
        subject = st.selectbox("किस विषय से प्रश्न चाहिए?", ("अर्थशास्त्र (Economics)", "इतिहास (History)", "भूगोल (Geography)", "राजनीति (Polity)", "विज्ञान (Science)"))
        
        if st.button(f"{subject} के प्रश्न निकालें"):
            with st.spinner(f'{subject} के सबसे बेहतरीन प्रश्न निकाले जा रहे हैं...'):
                prompt = f"{system_prompt}\n\nविषय: {subject}\nइस विषय के सबसे महत्वपूर्ण और बार-बार पूछे जाने वाले 5-10 प्रश्न तैयार करें।"
                response = model.generate_content(prompt)
                st.write(response.text)

    # फीचर 3: PDF से सवाल बनाना
    with tab3:
        st.subheader("किताब या नोट्स की PDF से परीक्षा वाले प्रश्न निकालें")
        uploaded_file = st.file_uploader("अपनी PDF फाइल यहाँ अपलोड करें", type="pdf")
        
        if st.button("PDF से प्रश्न निकालें") and uploaded_file is not None:
            with st.spinner('PDF को पढ़ा जा रहा है और महत्वपूर्ण फैक्ट्स निकाले जा रहे हैं...'):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                pdf_prompt = f"{system_prompt}\n\nनीचे दिए गए टेक्स्ट को ध्यान से पढ़ें और इसमें से SSC परीक्षा के लिए सबसे महत्वपूर्ण 5-10 प्रश्न, उनके विकल्प और सही उत्तर व्याख्या के साथ बनाएं:\n\n{text}"
                response = model.generate_content(pdf_prompt)
                st.write(response.text)

else:
    st.warning("ऐप का इस्तेमाल करने के लिए कृपया ऊपर अपनी API Key डालें।")
