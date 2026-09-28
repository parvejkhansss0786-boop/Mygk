import streamlit as st
import google.generativeai as genai
import PyPDF2

# ऐप की सेटिंग और डिज़ाइन
st.set_page_config(page_title="SSC GK AI Master", page_icon="📚", layout="wide")
st.title("📚 SSC GK & Current Affairs AI")
st.write("SSC एग्जामिनर के नजरिए से स्टैटिक GK, करंट अफेयर्स और PDF से महत्वपूर्ण प्रश्न हिंदी में निकालें।")

# API Key इनपुट
API_KEY = st.text_input("अपनी Google Gemini API Key डालें:", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    

    # AI का अपडेटेड SSC Examiner माइंडसेट (Static GK और Current Affairs पर फोकस)
    system_prompt = """
    तुम एक बेहद अनुभवी SSC (CGL, CHSL, CPO) एग्जामिनर हो। तुम्हारा काम दिए गए टॉपिक, विषय या टेक्स्ट से ऐसे प्रश्न बनाना है जिनके एग्जाम में आने की सबसे ज्यादा संभावना है।
    तुम्हें इन बातों का सख्ती से पालन करना है:
    1. **स्टैटिक जीके (Static GK) पर सबसे ज्यादा फोकस करें।** प्रश्न सीधे, तथ्यात्मक (factual) और SSC के पैटर्न पर होने चाहिए।
    2. **करंट अफेयर्स को स्टैटिक से जोड़ें:** यदि कोई हालिया घटना है, तो उसके पीछे की स्टैटिक जानकारी भी पूछें (जैसे SSC पूछता है)।
    3. सवाल बहुत ज्यादा आसान न हों, थोड़ा घुमावदार हों। विकल्पों (Options) के साथ उत्तर दें।
    4. विकिपीडिया और प्रामाणिक एजुकेशन साइट्स के एकदम सटीक फैक्ट्स का ही उपयोग करें।
    5. सारे सवाल, उनके सही जवाब और विस्तार से व्याख्या (Explanation) केवल 'हिंदी' भाषा में दें।
    """

    # ऐप को 3 हिस्सों (Tabs) में बांटा गया है
    tab1, tab2, tab3 = st.tabs(["🔍 टॉपिक से प्रश्न", "🌐 विषय-अनुसार करेंट & स्टैटिक", "📄 PDF से प्रश्न"])

    # फीचर 1: किसी विशेष टॉपिक से सवाल
    with tab1:
        st.subheader("किसी भी टॉपिक के महत्वपूर्ण प्रश्न")
        topic = st.text_input("टॉपिक का नाम लिखें (जैसे: भारत की राष्ट्रीय आय, मेवात का इतिहास, बैंकिंग प्रणाली):")
        
        if st.button("टॉपिक के प्रश्न जनरेट करें") and topic:
            with st.spinner('SSC के पैटर्न पर स्टैटिक GK प्रश्न तैयार किए जा रहे हैं...'):
                prompt = f"{system_prompt}\n\nटॉपिक: {topic}\nइस टॉपिक पर 5 से 10 सबसे महत्वपूर्ण प्रश्न (ऑप्शन और उत्तर सहित) हिंदी में बनाओ।"
                response = model.generate_content(prompt)
                st.write(response.text)

    # फीचर 2: विषय-अनुसार (Subject-wise) करंट और स्टैटिक GK
    with tab2:
        st.subheader("विषय चुनें और ताज़ा प्रश्न पाएं")
        # अर्थशास्त्र, इतिहास आदि विषयों का विकल्प
        subject = st.selectbox("किस विषय के प्रश्न चाहिए?", ["अर्थशास्त्र (Economics)", "इतिहास (History)", "भूगोल (Geography)", "राजव्यवस्था (Polity)", "सामान्य विज्ञान (General Science)"])
        
        if st.button(f"{subject} के प्रश्न निकालें"):
            with st.spinner(f'{subject} के करंट और स्टैटिक प्रश्न निकाले जा रहे हैं...'):
                prompt = f"{system_prompt}\n\nविषय: {subject}\nइस विषय के वे 10 प्रश्न बनाओ जिनके इस साल SSC में आने की सबसे ज्यादा संभावना है। इसमें स्टैटिक GK और हालिया करंट अफेयर्स दोनों का मिश्रण होना चाहिए।"
                response = model.generate_content(prompt)
                st.write(response.text)

    # फीचर 3: PDF से सवाल छांटना
    with tab3:
        st.subheader("किताब या नोट्स की PDF से परीक्षा वाले प्रश्न निकालें")
        uploaded_file = st.file_uploader("अपनी PDF फ़ाइल यहाँ अपलोड करें", type="pdf")
        
        if st.button("PDF से प्रश्न निकालें") and uploaded_file is not None:
            with st.spinner('PDF को पढ़ा जा रहा है और महत्वपूर्ण फैक्ट्स निकाले जा रहे हैं...'):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                pdf_prompt = f"{system_prompt}\n\nनीचे दिए गए टेक्स्ट को ध्यान से पढ़ो और इसमें से परीक्षा में आने लायक सबसे महत्वपूर्ण स्टैटिक प्रश्न और उत्तर हिंदी में निकालो:\n\n{text[:10000]}"
                
                response = model.generate_content(pdf_prompt)
                st.write(response.text)
else:
    st.warning("ऐप का इस्तेमाल करने के लिए कृपया ऊपर अपनी API Key डालें।")
