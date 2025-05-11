import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import re

# Language code to full name mapping
LANGUAGE_MAP = {
    'en': 'ENGLISH',
    'es': 'SPANISH',
    'sw': 'SWAHILI',
    'fr': 'FRENCH',
    'de': 'GERMAN',
    'it': 'ITALIAN',
    'pt': 'PORTUGUESE',
    'ja': 'JAPANESE',
    'ko': 'KOREAN',
    'hi': 'HINDI',
    'ar': 'ARABIC',
    'zh': 'CHINESE',
    'zh-TW': 'CHINESE_TAIWAN',
    'tl': 'TAGALOG',
    'unknown': 'UNKNOWN'
}

# Mock functions for testing without AWS credentials
def mock_detect_language(text):
    """Mock language detection based on simple heuristics, including Swahili."""
    if not text or len(text.encode('utf-8')) > 5000:
        return {"error": "Text is empty or exceeds 5,000 bytes."}
    text_lower = text.lower()
    if any(word in text_lower for word in ['hello', 'world', 'love', 'is']):
        return {"language": LANGUAGE_MAP['en'], "confidence": 0.95}
    elif any(word in text_lower for word in ['hola', 'mundo', 'gusta']):
        return {"language": LANGUAGE_MAP['es'], "confidence": 0.90}
    elif any(word in text_lower for word in ['habari', 'mambo', 'napenda', 'safari', 'jambo']):
        return {"language": LANGUAGE_MAP['sw'], "confidence": 0.90}
    else:
        return {"language": LANGUAGE_MAP['unknown'], "confidence": 0.80}

def mock_extract_key_phrases(text, language_code='en'):
    """Mock key phrase extraction by extracting noun-like phrases."""
    if not text or len(text.encode('utf-8')) > 5000:
        return {"error": "Text is empty or exceeds 5,000 bytes."}
    phrases = re.findall(r'\b[A-Z][a-z]*\b|\b[a-z]+(?:\s+[a-z]+)*\b', text)
    key_phrases = [{"phrase": phrase, "confidence": 0.85} for phrase in phrases[:3] if len(phrase) > 2]
    return {"key_phrases": key_phrases} if key_phrases else {"error": "No key phrases detected."}

# AWS Comprehend functions
def detect_language(text):
    """Detect language using AWS Comprehend, with Swahili correction."""
    try:
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        if not text or len(text.encode('utf-8')) > 5000:
            return {"error": "Text is empty or exceeds 5,000 bytes."}
        response = comprehend.detect_dominant_language(Text=text)
        languages = response['Languages']
        if languages:
            lang_code = languages[0]['LanguageCode']
            confidence = round(languages[0]['Score'], 4)
            # Correct TL to SW if Swahili keywords are present
            text_lower = text.lower()
            swahili_keywords = ['habari', 'mambo', 'napenda', 'safari', 'jambo']
            if lang_code == 'tl' and any(word in text_lower for word in swahili_keywords):
                lang_code = 'sw'
                confidence = min(confidence, 0.90)  # Adjust confidence for correction
            return {"language": LANGUAGE_MAP.get(lang_code, LANGUAGE_MAP['unknown']), "confidence": confidence}
        return {"error": "No language detected."}
    except NoCredentialsError:
        return {"error": "AWS credentials not configured. Please run 'aws configure'."}
    except ClientError as e:
        return {"error": f"AWS error: {e}"}
    except Exception as e:
        return {"error": f"Error: {e}"}

def extract_key_phrases(text, language_code='en'):
    """Extract key phrases using AWS Comprehend."""
    try:
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        if not text or len(text.encode('utf-8')) > 5000:
            return {"error": "Text is empty or exceeds 5,000 bytes."}
        supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'hi', 'ar', 'zh', 'zh-TW']
        if language_code not in supported_languages:
            language_code = 'en'
        response = comprehend.detect_key_phrases(Text=text, LanguageCode=language_code)
        key_phrases = [
            {"phrase": kp['Text'], "confidence": round(kp['Score'], 4)}
            for kp in response['KeyPhrases']
        ]
        return {"key_phrases": key_phrases} if key_phrases else {"error": "No key phrases detected."}
    except NoCredentialsError:
        return {"error": "AWS credentials not configured. Please run 'aws configure'."}
    except ClientError as e:
        return {"error": f"AWS error: {e}"}
    except Exception as e:
        return {"error": f"Error: {e}"}

# Streamlit configuration
st.set_page_config(page_title="Comprehend NLP Analyzer", page_icon="🧠", layout="wide")

# Custom CSS for bright and dark mode support
st.markdown("""
    <style>
    :root {
        --primary-bg: #2b5876;
        --secondary-bg: #4e4376;
        --card-bg: #ffffff;
        --text-color: #333333;
        --title-color: #ffffff;
        --subtitle-color: #e0e0e0;
        --button-bg-start: #7b2cbf;
        --button-bg-end: #3f37c9;
        --sidebar-bg-start: #f8f9fa;
        --sidebar-bg-end: #e3f2fd;
        --border-color: #4e4376;
        --shadow-color: rgba(0, 0, 0, 0.3);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --primary-bg: #1a2a44;
            --secondary-bg: #2e1a47;
            --card-bg: #2c2c2c;
            --text-color: #e0e0e0;
            --title-color: #e0e0e0;
            --subtitle-color: #b0b0b0;
            --button-bg-start: #9b59b6;
            --button-bg-end: #5b5bd6;
            --sidebar-bg-start: #2c3e50;
            --sidebar-bg-end: #34495e;
            --border-color: #6b4e9b;
            --shadow-color: rgba(0, 0, 0, 0.5);
        }
    }

    .main {
        background: linear-gradient(135deg, var(--primary-bg), var(--secondary-bg));
        padding: 30px;
        border-radius: 15px;
        color: var(--title-color);
    }
    .stTextArea textarea {
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 15px;
        font-size: 16px;
        color: var(--text-color);
    }
    .stButton>button {
        background: linear-gradient(45deg, var(--button-bg-start), var(--button-bg-end));
        color: var(--title-color);
        border: none;
        border-radius: 30px;
        padding: 12px 35px;
        font-size: 18px;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px var(--shadow-color);
        margin: 8px;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px var(--shadow-color);
    }
    .result-card {
        background: var(--card-bg);
        border-left: 5px solid var(--button-bg-start);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px var(--shadow-color);
        transition: transform 0.2s;
        color: var(--text-color);
    }
    .result-card:hover {
        transform: translateY(-5px);
    }
    .title {
        font-size: 3.2em;
        text-align: center;
        color: var(--title-color);
        text-shadow: 2px 2px 4px var(--shadow-color);
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.6em;
        text-align: center;
        color: var(--subtitle-color);
        margin-bottom: 30px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, var(--sidebar-bg-start), var(--sidebar-bg-end));
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 10px var(--shadow-color);
        color: var(--text-color);
    }
    .sidebar-header {
        background: linear-gradient(45deg, var(--button-bg-start), var(--button-bg-end));
        color: var(--title-color);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 20px;
    }
    .icon {
        font-size: 1.2em;
        margin-right: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Page Title
st.markdown('<div class="title">🌟 Comprehend NLP Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Language Detection & Key Phrase Extraction for Machine Learning</div>', unsafe_allow_html=True)

# Text input
with st.container():
    text_input = st.text_area("✍️ Enter your text here (max 5,000 bytes):", height=200, placeholder="Type or paste your text...")

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    analyze = st.button("🚀 Analyze Text")
with col2:
    reset = st.button("🔄 Reset")

if reset:
    st.rerun()

# Analysis process
if analyze:
    if not text_input.strip():
        st.warning("Please enter some text to analyze.")
    else:
        with st.spinner("🔍 Analyzing your text..."):
            # Check if AWS credentials are available
            try:
                boto3.client('comprehend', region_name='us-east-1').list_endpoints()
                use_aws = True
            except NoCredentialsError:
                use_aws = False
                st.warning("AWS credentials not configured. Using mock API for assignment testing. Run 'aws configure' to enable Comprehend API.")

            # Language Detection
            lang_result = detect_language(text_input) if use_aws else mock_detect_language(text_input)
            if "error" in lang_result:
                st.error(lang_result["error"])
            else:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 🗣️ Language Detection")
                st.markdown(f"<span class='icon'>🌐</span><b>Detected Language:</b> {lang_result['language']}<br>"
                            f"<span class='icon'>📊</span><b>Confidence Score:</b> {lang_result['confidence']}", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Key Phrase Extraction
            key_result = extract_key_phrases(text_input, lang_result.get('language', 'en')) if use_aws else mock_extract_key_phrases(text_input)
            if "error" in key_result:
                st.error(key_result["error"])
            else:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 🧠 Key Phrases Extracted")
                for kp in key_result["key_phrases"]:
                    st.markdown(f"<span class='icon'>🔑</span><b>Phrase:</b> {kp['phrase']}<br>"
                                f"<span class='icon'>📈</span><b>Confidence:</b> {kp['confidence']}", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<div class="sidebar-header">📚 Machine Learning Assignment</div>', unsafe_allow_html=True)
st.sidebar.info("""
 **Purpose**: This app fulfills a machine learning assignment to implement:
- **Language Detection**: Identifies the dominant language of input text.
- **Key Phrase Extraction**: Extracts significant phrases with confidence scores.

- Uses **Amazon Comprehend API** for production-grade NLP analysis.

""")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Author**: -GROUP ASSIGNMENT""")