import google.generativeai as genai

def ask_gemini(context_chunks: list, query: str, model_name="gemini-2.5-pro"):
    # keep context to reasonable size outside (caller should pass top chunks)
    prompt = f"Given the following context:\n\n{ '\n\n'.join(context_chunks) }\n\nAnswer this:\n{query}"
    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(prompt)
    return resp.text
