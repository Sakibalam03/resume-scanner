import os
import io
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from resume_scanner import (
    get_document_text,
    load_sentence_transformer_model,
    get_embedding,
    calculate_similarity,
)

load_dotenv()

DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_THRESHOLD = int(os.getenv("TEXT_LENGTH_THRESHOLD", 100))

st.set_page_config(
    page_title="Resume Scanner",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .score-bar-container { background: #f0f0f0; border-radius: 4px; height: 8px; margin-top: 4px; }
    .score-bar { height: 8px; border-radius: 4px; }
    .result-card {
        background: #fafafa;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .rank-badge {
        font-size: 0.75rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .resume-name { font-size: 1rem; font-weight: 600; margin: 0.15rem 0; }
    .score-label { font-size: 0.85rem; color: #555; }
    .method-tag {
        display: inline-block;
        font-size: 0.7rem;
        background: #efefef;
        border-radius: 4px;
        padding: 1px 6px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_model(model_name):
    return load_sentence_transformer_model(model_name)


def score_color(score):
    if score >= 0.75:
        return "#22c55e"
    elif score >= 0.55:
        return "#f59e0b"
    else:
        return "#ef4444"


def process_uploaded_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    tmp_path = f"_tmp_{uploaded_file.name}"
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    try:
        text, method = get_document_text(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return text, method


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Resume Scanner")
    st.caption("Rank candidates by semantic similarity to a job description.")
    st.divider()

    st.subheader("Model")
    model_name = st.selectbox(
        "Embedding model",
        ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-MiniLM-L6-v2"],
        index=0,
        help="all-MiniLM-L6-v2 is fast and accurate for most use cases. all-mpnet-base-v2 is more accurate but slower.",
    )

    st.subheader("Extraction")
    threshold = st.number_input(
        "Minimum text length (chars)",
        min_value=0,
        max_value=1000,
        value=DEFAULT_THRESHOLD,
        step=10,
        help="If direct extraction returns fewer characters than this, OCR is attempted.",
    )

    st.divider()
    st.caption("Scores are cosine similarity (0–1). Use them as relative rankings within a batch, not absolute pass/fail values.")


# ── Main layout ────────────────────────────────────────────────────────────────

upload_col, results_col = st.columns([1, 1.6], gap="large")

with upload_col:
    st.subheader("Job Description")
    jd_file = st.file_uploader(
        "Upload job description",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    if jd_file:
        st.caption(f"Uploaded: **{jd_file.name}**")

    st.divider()

    st.subheader("Resumes")
    resume_files = st.file_uploader(
        "Upload resumes",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if resume_files:
        st.caption(f"{len(resume_files)} file(s) selected")

    st.divider()

    ready = bool(jd_file and resume_files)
    analyze_btn = st.button(
        "Analyze Resumes",
        type="primary",
        disabled=not ready,
        use_container_width=True,
    )
    if not ready:
        st.caption("Upload a job description and at least one resume to continue.")


with results_col:
    st.subheader("Results")

    if analyze_btn:
        with st.spinner("Loading model..."):
            model = load_model(model_name)

        if model is None:
            st.error("Failed to load embedding model. Check your Python environment.")
            st.stop()

        with st.spinner("Extracting text from job description..."):
            jd_text, jd_method = process_uploaded_file(jd_file)

        if not jd_text:
            st.error("Could not extract text from the job description. Check the file is not empty or password-protected.")
            st.stop()

        jd_embedding = get_embedding(jd_text, model)
        if jd_embedding is None:
            st.error("Failed to generate embedding for job description.")
            st.stop()

        results = []
        progress = st.progress(0, text="Processing resumes...")

        for i, resume_file in enumerate(resume_files):
            progress.progress((i + 1) / len(resume_files), text=f"Processing {resume_file.name}...")
            text, method = process_uploaded_file(resume_file)

            if not text:
                results.append({
                    "resume": resume_file.name,
                    "score": None,
                    "method": "failed",
                    "error": "Text extraction failed",
                })
                continue

            embedding = get_embedding(text, model)
            if embedding is None:
                results.append({
                    "resume": resume_file.name,
                    "score": None,
                    "method": method,
                    "error": "Embedding failed",
                })
                continue

            score = calculate_similarity(jd_embedding, embedding)
            results.append({
                "resume": resume_file.name,
                "score": score,
                "method": method,
                "error": None,
            })

        progress.empty()

        scored = sorted(
            [r for r in results if r["score"] is not None],
            key=lambda x: x["score"],
            reverse=True,
        )
        failed = [r for r in results if r["score"] is None]

        if not scored:
            st.warning("No resumes could be scored. Check file formats and Tesseract installation.")
        else:
            for rank, r in enumerate(scored, start=1):
                score = r["score"]
                color = score_color(score)
                bar_width = int(score * 100)

                st.markdown(f"""
                <div class="result-card">
                    <div class="rank-badge">Rank {rank}</div>
                    <div class="resume-name">{r['resume']}</div>
                    <div class="score-label">
                        Score: <strong>{score:.4f}</strong>
                        &nbsp;<span class="method-tag">{r['method']}</span>
                    </div>
                    <div class="score-bar-container">
                        <div class="score-bar" style="width:{bar_width}%; background:{color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if failed:
                with st.expander(f"{len(failed)} file(s) could not be processed"):
                    for r in failed:
                        st.caption(f"- **{r['resume']}**: {r['error']}")

            st.divider()
            df = pd.DataFrame([
                {"Rank": i + 1, "Resume": r["resume"], "Score": round(r["score"], 4), "Method": r["method"]}
                for i, r in enumerate(scored)
            ])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download results as CSV",
                data=csv,
                file_name="resume_scores.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.caption("Results will appear here after analysis.")
