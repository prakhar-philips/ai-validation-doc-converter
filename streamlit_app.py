import streamlit as st
import os
from app.pdf_reader import extract_text_from_pdf
from app.classifier import load_index_and_labels, classify_text
from app.llm_runner import run_llm_with_prompt
from app.utils import export_to_pdf
# Load FAISS index and labels once
index, labels = load_index_and_labels()

st.set_page_config(page_title="AI Validation Doc Generator", layout="wide")
st.title("🧠 AI Validation Document Generator")

# Initialize session state variables
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

if "doc_type" not in st.session_state:
    st.session_state.doc_type = None

if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

# File Upload
uploaded_file = st.file_uploader("📤 Upload a Validation Document (PDF)", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.session_state.extracted_text = extract_text_from_pdf("temp.pdf")
    st.subheader("📄 Extracted Text Preview")
    st.text_area("Document Content", st.session_state.extracted_text, height=300)

    # Classification Button
    if st.button("🔍 Classify Document"):
        st.session_state.doc_type = classify_text(
            st.session_state.extracted_text, index, labels
        )

# Display classification result
if st.session_state.doc_type:
    st.success(f"📌 Predicted Document Type: {st.session_state.doc_type}")

# If it's URS, show prompt input
if st.session_state.doc_type == "URS":
    st.subheader("📝 Describe What You Want in the FRS")
    st.session_state.prompt_text = st.text_area(
        "Prompt for FRS generation",
        value=st.session_state.prompt_text,
        placeholder="e.g., Include login, user dashboard, and access logs."
    )

    # FRS Generation
    if st.button("⚙️ Generate FRS Document"):
        if not st.session_state.prompt_text.strip():
            st.warning("Please enter a prompt for FRS generation.")
        else:
            with st.spinner("💡 Generating using local LLM..."):
                try:
                    llm_output = run_llm_with_prompt(
                        st.session_state.prompt_text,
                        st.session_state.extracted_text
                    )

                    if not llm_output.strip():
                        st.error("❌ LLM returned empty output. Try modifying the prompt.")
                    else:
                        os.makedirs("output", exist_ok=True)
                        pdf_path = "output/generated_frs.pdf"
                        export_to_pdf(llm_output, pdf_path)

                        st.success("🎉 FRS Document Generated!")
                        st.text_area("📄 Preview of Generated FRS", llm_output, height=400)

                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download FRS PDF",
                                data=f,
                                file_name="FRS_Generated.pdf"
                            )
                except Exception as e:
                    st.error(f"💥 Error during generation: {e}")

# If doc_type is not URS, show info
elif st.session_state.doc_type:
    st.info(f"🚫 FRS generation available only for URS documents (Detected: {st.session_state.doc_type}).")
