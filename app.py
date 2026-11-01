import streamlit as st

from toolkit.core import (
    InputError, build_blog_prompt, build_regex_prompt, build_resume_prompt,
    extract_pdf_text, fetch_transcript, youtube_video_id,
)
from toolkit.llm import GenerationError, check_connection, generate

st.set_page_config(page_title="The Workbench | AI productivity toolkit", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {font-family: 'DM Sans', sans-serif;}
.stApp {background: #f6f8fc; color: #18243b;}
.block-container {max-width: 1250px; padding-top: 2.6rem; padding-bottom: 4rem;}
[data-testid="stSidebar"] {background: #fff; border-right: 1px solid #e8edf5;}
[data-testid="stSidebar"] > div:first-child {padding-top: 1.7rem;}
[data-testid="stSidebar"] .block-container {padding-top: 0;}
h1,h2,h3 {font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; color: #17243b;}
h1 {font-size: 2.45rem !important; line-height: 1.18 !important; font-weight: 800 !important;}
h2 {font-size: 1.18rem !important; font-weight: 700 !important;}
p {color: #58677e;}
.brand {display:flex; align-items:center; gap:10px; margin:0 0 4px; font-family:Manrope,sans-serif; font-weight:800; font-size:17px; letter-spacing:-.035em; color:#17243b;}
.brand-mark {display:grid; place-items:center; width:34px; height:34px; border-radius:10px; background:#315bce; color:white; font-size:20px;}
.brand-sub {color:#8a97aa; font-size:10px; font-weight:700; letter-spacing:.13em; margin:0 0 35px 44px;}
.nav-label {color:#9aa6b7; font-size:10px; font-weight:700; letter-spacing:.14em; margin:0 0 8px;}
[data-testid="stSidebar"] [role="radiogroup"] {gap: 4px;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding: 9px 10px; border-radius: 7px;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background:#edf2ff;}
[data-testid="stSidebar"] hr {margin: 1.6rem 0; border-color:#edf0f5;}
.eyebrow {color:#315bce; font-size:11px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; margin-bottom:10px;}
.intro {font-size:15px; line-height:1.7; color:#718097; max-width:720px; margin-top:-4px; margin-bottom:24px;}
.topline {display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e5eaf2; padding-bottom:18px; margin-bottom:36px; color:#8a97a9; font-size:12px; font-weight:600;}
.status {color:#61738e; background:white; border:1px solid #e5eaf2; border-radius:30px; padding:7px 11px; font-size:11px;}
.dot {display:inline-block; width:7px; height:7px; background:#65b995; border-radius:50%; margin-right:6px;}
.section-label {font-family:Manrope,sans-serif; font-size:16px; font-weight:700; color:#1b2940; margin:3px 0 4px;}
.section-caption {font-size:13px; color:#8a98aa; margin-bottom:18px;}
.tip {background:#f0f4ff; border:1px solid #e1e9ff; border-radius:9px; padding:14px 16px; color:#536b9c; font-size:12px; line-height:1.6; margin-top:18px;}
.tip strong {color:#315b9f;}
.panel-heading {font-size:11px; font-weight:800; letter-spacing:.11em; color:#8b98aa; text-transform:uppercase; margin-bottom:13px;}
.empty-state {border:1px dashed #d8e1ef; background:#fbfcfe; border-radius:10px; text-align:center; padding:55px 20px; color:#8795a9; font-size:13px; line-height:1.7;}
.empty-icon {display:grid; place-items:center; margin:0 auto 16px; height:43px; width:43px; border-radius:12px; background:#edf2ff; color:#5477d3; font-size:20px;}
.empty-state strong {color:#52627a; font-size:14px;}
.footer-note {font-size:11px; color:#9aa7b8; margin-top:24px;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#e6ebf3 !important; border-radius:12px !important; background:#fff; padding:24px !important;}
.stButton > button[kind="primary"] {background:#315bce; border:0; border-radius:8px; font-weight:600; min-height:44px;}
.stButton > button[kind="primary"]:hover {background:#254caf;}
.stDownloadButton button {border-radius:8px;}
[data-testid="stFileUploader"] section {background:#f9fbfe; border:1px dashed #d8e1ef; border-radius:9px;}
[data-testid="stWidgetLabel"] p {color:#34445c; font-size:13px; font-weight:600;}
@media (max-width: 640px) {.block-container {padding-top:1.5rem;} h1 {font-size:2rem !important;}}
</style>
""", unsafe_allow_html=True)

TOOLS = {
    "Resume Roaster": {"eyebrow": "CAREER INTELLIGENCE", "title": "A better resume starts here.", "description": "Get an honest, role-specific review that turns tough feedback into your next opportunity.", "input": "Your resume", "caption": "Give us the context to make your feedback count.", "empty": "Your review will appear here", "hint": "Upload your resume and select a target role to get started.", "file": "resume-review.md"},
    "Video to Blog": {"eyebrow": "CONTENT WORKSPACE", "title": "Turn video into valuable content.", "description": "Transform a YouTube transcript into a structured, ready-to-refine blog post in minutes.", "input": "Video details", "caption": "Tell us what you'd like to turn into a story.", "empty": "Your draft will appear here", "hint": "Add a YouTube link and we'll build your first draft.", "file": "blog-draft.md"},
    "Regex Generator": {"eyebrow": "DEVELOPER TOOLKIT", "title": "Make sense of regex.", "description": "Describe what you need to match and get a pattern, explanation, and practical test cases.", "input": "Pattern requirements", "caption": "Describe the matching rule in plain language.", "empty": "Your pattern will appear here", "hint": "Describe a rule to generate a pattern and test cases.", "file": "regex-pattern.md"},
}

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✦</span> the workbench</div><div class="brand-sub">AI PRODUCTIVITY SUITE</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">WORKSPACE</div>', unsafe_allow_html=True)
    tool = st.radio("Workspace", list(TOOLS), label_visibility="collapsed")
    st.divider()
    st.markdown('<div class="nav-label">YOUR API KEY</div>', unsafe_allow_html=True)
    api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-...", help="Your key is used for requests to OpenAI. It remains in this browser session's server memory and is not saved by this app.")
    st.caption("Bring your own key. OpenAI usage charges apply to your account.")
    with st.expander("Connection help"):
        st.caption("Test connectivity without sending your API key or content. This test uses the network of the computer running the app.")
        if st.button("Test OpenAI connection"):
            with st.spinner("Testing connection..."):
                connected, message = check_connection()
            if connected:
                st.success(message)
            else:
                st.error(message)
    st.divider()
    st.markdown('<div class="nav-label">APPEARANCE</div>', unsafe_allow_html=True)
    dark_mode = st.toggle("Dark mode", key="dark_mode", help="Switch between light and dark appearance for this session.")
    st.divider()
    st.markdown('<div class="nav-label">BUILT FOR BETTER WORK</div>', unsafe_allow_html=True)
    st.caption("Three focused tools. One simple workspace.")
    st.markdown('<div class="footer-note">Your work, elevated. ✦</div>', unsafe_allow_html=True)

# Streamlit's built-in theme settings do not apply to our custom cards and text.
# Override both those elements and the native widgets together for a cohesive dark mode.
if dark_mode:
    st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background: #101827; color: #e3ebf7;}
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {background: #151f30; border-color: #2c3a50;}
    [data-testid="stSidebar"] hr {border-color: #2c3a50;}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: #243758;}
    h1, h2, h3, h4, .brand, .section-label {color: #edf3fc !important;}
    p, [data-testid="stWidgetLabel"] p, [data-testid="stSidebar"] label, [data-testid="stMarkdownContainer"] li {color: #c4d0e1;}
    .eyebrow {color: #90aaff;}
    .intro, .section-caption, .panel-heading, .nav-label, .brand-sub, .footer-note {color: #a4b4ca;}
    .topline {color: #a4b4ca; border-color: #304058;}
    .status {background: #1c293c; border-color: #34445b; color: #c0cce0;}
    [data-testid="stVerticalBlockBorderWrapper"] > div {background: #1b2739; border-color: #334258 !important;}
    .tip {background: #202f4c; border-color: #334c75; color: #c2d2ef;}
    .tip strong {color: #a9c3ff;}
    .empty-state {background: #172335; border-color: #40516a; color: #b1c0d5;}
    .empty-state strong {color: #dae5f5;}
    .empty-icon {background: #293c60; color: #a6bdff;}
    [data-testid="stFileUploader"] section {background: #172335; border-color: #40516a;}
    [data-testid="stFileUploader"] section small, [data-testid="stCaptionContainer"] p {color: #b4c3d8;}
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div {background: #111d2e !important; color: #edf3fc !important; border-color: #42536b !important;}
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {color: #96a7bd; opacity: 1;}
    [data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stTextArea"] [data-baseweb="textarea"] {background: #111d2e; border-color: #42536b;}
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] {background: #1b2739; color: #edf3fc;}
    [data-baseweb="popover"] [role="option"]:hover {background: #304567;}
    [data-testid="stFileUploader"] button, .stDownloadButton button {background: #283950; color: #edf3fc; border-color: #4a5d76;}
    [data-testid="stMarkdownContainer"] code {color: #e1eaf9; background: #24344a;}
    [data-testid="stMarkdownContainer"] pre {background: #111d2e;}
    </style>
    """, unsafe_allow_html=True)

info = TOOLS[tool]
st.markdown('<div class="topline"><span>WORKSPACE &nbsp; / &nbsp; ' + tool.upper() + '</span><span class="status"><span class="dot"></span> Your AI workspace</span></div>', unsafe_allow_html=True)
st.markdown(f'<div class="eyebrow">✦ &nbsp; {info["eyebrow"]}</div>', unsafe_allow_html=True)
st.title(info["title"])
st.markdown(f'<div class="intro">{info["description"]}</div>', unsafe_allow_html=True)

left, right = st.columns([1, 1.08], gap="large")
with left:
    with st.container(border=True):
        st.markdown(f'<div class="section-label">{info["input"]}</div><div class="section-caption">{info["caption"]}</div>', unsafe_allow_html=True)
        with st.form(f"form_{tool}"):
            if tool == "Resume Roaster":
                uploaded = st.file_uploader("Resume PDF", type=["pdf"], help="Text-based PDF, up to 10 MB. Scanned PDFs are not supported.")
                role = st.text_input("Target role", placeholder="e.g. Senior Product Manager", max_chars=150)
                intensity = st.select_slider("Feedback intensity", options=["Gentle", "Balanced", "Brutally honest"], value="Balanced")
            elif tool == "Video to Blog":
                url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
                audience = st.text_input("Target audience", placeholder="e.g. Founders and product teams", max_chars=150)
            else:
                description = st.text_area("What should the pattern match?", placeholder="e.g. Match an email address that doesn't end in .org", height=150, max_chars=3000)
                flavor = st.selectbox("Regex flavor", ["Python", "JavaScript", "PCRE", "Java", ".NET"])
            submit_label = {"Resume Roaster": "Generate review", "Video to Blog": "Generate blog post", "Regex Generator": "Generate pattern"}[tool]
            submitted = st.form_submit_button(submit_label + "  →", type="primary", use_container_width=True, key=f"submit_{tool}")
        if tool == "Resume Roaster":
            st.markdown('<div class="tip"><strong>For the best results</strong><br>Use a text-based PDF and be specific about your target role. Remove personal details you don’t want to share.</div>', unsafe_allow_html=True)
        elif tool == "Video to Blog":
            st.markdown('<div class="tip"><strong>Good to know</strong><br>Requires an accessible English transcript. YouTube may block transcript requests, particularly from hosted servers.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="tip"><strong>Be specific</strong><br>Include examples, boundaries, and any rules about what should not match.</div>', unsafe_allow_html=True)

if submitted:
    # Clear stale output before a new attempt, including failed validation.
    st.session_state.pop(f"result_{tool}", None)
    try:
        if not api_key.strip():
            raise InputError("Add your OpenAI API key in the sidebar to get started.")
        if tool == "Resume Roaster":
            if not uploaded:
                raise InputError("Please upload your resume as a PDF.")
            if not role.strip():
                raise InputError("Please enter a target role.")
            prompts = build_resume_prompt(extract_pdf_text(uploaded.getvalue()), role.strip(), intensity)
        elif tool == "Video to Blog":
            video_id = youtube_video_id(url)
            with st.spinner("Retrieving transcript..."):
                transcript = fetch_transcript(video_id)
            prompts = build_blog_prompt(transcript, audience.strip() or "general readers")
        else:
            if not description.strip():
                raise InputError("Please describe the pattern you need.")
            prompts = build_regex_prompt(description.strip(), flavor)
        with st.spinner("Generating your result..."):
            st.session_state[f"result_{tool}"] = generate(api_key.strip(), *prompts)
    except (InputError, GenerationError) as exc:
        st.session_state[f"error_{tool}"] = str(exc)
    else:
        st.session_state.pop(f"error_{tool}", None)

with right:
    with st.container(border=True):
        st.markdown('<div class="section-label">Your results</div><div class="section-caption">Thoughtful output, ready for your next step.</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-heading">GENERATED OUTPUT</div>', unsafe_allow_html=True)
        error = st.session_state.get(f"error_{tool}")
        result = st.session_state.get(f"result_{tool}")
        if error:
            st.error(error)
        if result:
            st.markdown(result)
            st.download_button("Download as Markdown", result, file_name=info["file"], mime="text/markdown", use_container_width=True)
            st.caption("AI output can be inaccurate. Review and verify before using.")
        elif not error:
            st.markdown(f'<div class="empty-state"><div class="empty-icon">✧</div><strong>{info["empty"]}</strong><br>{info["hint"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="footer-note">✦ &nbsp; Powered by OpenAI · Generated for you</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">PRIVACY NOTE &nbsp; · &nbsp; Inputs are sent to OpenAI for processing. YouTube transcript requests are sent to YouTube. Avoid sharing sensitive information.</div>', unsafe_allow_html=True)
