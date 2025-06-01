from transformers import pipeline
import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# Using Hugging Face hosted model
model_name = "bigcode/starcoderbase"  # You can change this to any HF hosted code model
pipe = pipeline("text-generation", model=model_name)

def generate_code_from_description(api_desc, archetype=""):
    prompt = f"""
You are a senior software engineer. Write full Java classes to implement the following API:

{api_desc}

Archetype code (optional):
{archetype}

Return only valid Java code.
"""
    result = pipe(prompt, max_new_tokens=1024, do_sample=False)[0]["generated_text"]
    return result