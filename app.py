import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import re

# Mock functions for testing without AWS credentials
def mock_detect_language(text):
    """Mock language detection based on simple heuristics."""
    if not text or len(text.encode('utf-8')) > 5000:
        return {"error": "Text is empty or exceeds 5,000 bytes."}
    text_lower = text.lower()
    if any(word in text_lower for word in ['hello', 'world', 'love', 'is']):
        return {"language": "en", "confidence": 0.95}
    elif any(word in text_lower for word in ['hola', 'mundo', 'gusta']):
        return {"language": "es", "confidence": 0.90}
    else:
        return {"language": "unknown", "confidence": 0.80}

def mock_extract_key_phrases(text, language_code='en'):
    """Mock key phrase extraction by extracting noun-like phrases."""
    if not text or len(text.encode('utf-8')) > 5000:
        return {"error": "Text is empty or exceeds 5,000 bytes."}
    phrases = re.findall(r'\b[A-Z][a-z]*\b|\b[a-z]+(?:\s+[a-z]+)*\b', text)
    key_phrases = [{"phrase": phrase, "confidence": 0.85} for phrase in phrases[:3] if len(phrase) > 2]
    return {"key_phrases": key_phrases} if key_phrases else {"error": "No key phrases detected."}

# AWS Comprehend functions
def detect_language(text):
    """Detect language using AWS Comprehend."""
    try:
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        if not text or len(text.encode('utf-8')) > 5000:
            return {"error": "Text is empty or exceeds 5,000 bytes."}
        response = comprehend.detect_dominant_language(Text=text)
        languages = response['Languages']
        if languages:
            return {
                "language": languages[0]['LanguageCode'],
                "confidence": round(languages[0]['Score'], 4)
            }
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

# Custom CSS for attractive and clear UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #2b5876, #4e4376);
        padding: 30px;
        border-radius: 15px;
        color: #ffffff;
    }
    .stTextArea textarea {
        background-color: #f8f9fa;
        border: 2px solid #4e4376;
        border-radius: 12px;
        padding: 15px;
        font-size: 16px;
        color: #333333;
    }
    .stButton>button {
        background: linear-gradient(45deg, #7b2cbf, #3f37c9);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 30px;
        font-size: 18px;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin: 5px;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .result-card {
        background: #ffffff;
        border-left: 5px solid #7b2cbf;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        color: #333333;
    }
    .result-card:hover {
        transform: translateY(-5px);
    }
    .title {
        font-size: 3.2em;
        text-align: center;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.6em;
        text-align: center;
        color: #e0e0e0;
        margin-bottom: 30px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f8f9fa, #e3f2fd);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .sidebar-header {
        background: linear-gradient(45deg, #7b2cbf, #3f37c9);
        color: white;
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
                st.warning("AWS credentials not found. Using mock API for testing. Configure credentials with 'aws configure' for Comprehend API.")

            # Language Detection
            lang_result = detect_language(text_input) if use_aws else mock_detect_language(text_input)
            if "error" in lang_result:
                st.error(lang_result["error"])
            else:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 🗣️ Language Detection")
                st.markdown(f"<span class='icon'>🌐</span><b>Detected Language:</b> {lang_result['language'].upper()}<br>"
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