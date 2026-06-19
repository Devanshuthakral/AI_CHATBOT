import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

# ---------- Page setup ----------
st.set_page_config(
    page_title="Gemini Chat",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #fafbff 0%, #eef1fb 100%);
        color: #1f2333;
    }
    h1, h2, h3 { color: #1f2333 !important; }

    .hero {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6a5cff, #2f8bff, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero p {
        color: #6b7088;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }

    .response-card {
        background: #ffffff;
        border: 1px solid #e2e5f1;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-top: 1rem;
        color: #1f2333;
        box-shadow: 0 8px 24px rgba(108, 99, 255, 0.08);
    }
    .response-card h4 {
        color: #6a5cff;
        margin-top: 0;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1f2333 !important;
        border-radius: 10px !important;
        border: 1px solid #d8dcec !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #6a5cff, #00b4d8);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.55rem 1.6rem;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(79, 139, 255, 0.35);
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e5f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings")


    model = st.selectbox(
        "Model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        index=0,
    )

    st.markdown("---")

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
        <h1>✨ Gemini Chat</h1>
        <p>Ask anything. Powered by Google's Gemini API.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Prompt input ----------
prompt = st.text_area(
    "Your prompt",
    placeholder="e.g. Who is the PM of India and the United Kingdom?",
    height=140,
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 5])
with col1:
    generate = st.button("Generate ✨", use_container_width=True)

# ---------- Generation ----------
if generate:
    if not api_key_input:
        st.error("Please add your Google API key in the sidebar (or in a .env file as GOOGLE_API_KEY).")
    elif not prompt.strip():
        st.warning("Type a prompt first.")
    else:
        client = genai.Client(api_key=api_key_input)

        max_retries = 3
        response = None
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                with st.spinner(
                    "Thinking..." if attempt == 1 else f"Model is busy, retrying ({attempt}/{max_retries})..."
                ):
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                last_error = None
                break
            except Exception as e:
                last_error = e
                # Only retry on overload/unavailable errors; fail fast on anything else
                if "503" in str(e) or "UNAVAILABLE" in str(e) or "overloaded" in str(e).lower():
                    if attempt < max_retries:
                        time.sleep(2 * attempt)  # 2s, 4s backoff
                        continue
                break

        if response is not None:
            st.markdown(
                f"""
                <div class="response-card">
                    <h4>Response</h4>
                    {response.text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif last_error is not None:
            if "503" in str(last_error) or "UNAVAILABLE" in str(last_error):
                st.error(
                    "Gemini's servers are overloaded right now (503). "
                    "This is on Google's end, not your app — try again in a minute, "
                    "or switch to a different model in the sidebar."
                )
            else:
                st.error(f"Something went wrong: {last_error}")

# ---------- Footer ----------
st.markdown(
    "<p style='text-align:center; color:#6b6b85; margin-top:2.5rem; font-size:0.8rem;'>"
    "Built with Streamlit + Gemini API</p>",
    unsafe_allow_html=True,
)