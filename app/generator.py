import os
from app.utils import get_top_k_chunks
from app.llm_runner import run_llm_with_prompt

# Template prompt format for document generation
def build_prompt(doc_type, user_prompt):
    context_chunks = get_top_k_chunks(doc_type, k=10)
    context_text = "\n".join(context_chunks)

    prompt = f"""
You are an expert in documentation and compliance systems.
Use the following extracted {doc_type} content to generate the next stage document as per the user's instruction.

---
REFERENCE {doc_type} CONTENT:
{context_text}

---
USER INSTRUCTION:
{user_prompt}

Now generate a complete {doc_type} document based on the above.
Ensure the output is professional, detailed, and structured over 4 pages.
"""
    return prompt

def generate_document(doc_type, user_prompt):
    prompt = build_prompt(doc_type, user_prompt)
    result = run_llm_with_prompt(prompt)
    return result
