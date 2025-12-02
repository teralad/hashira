from transformers import pipeline
import os

# Lazy load the model - only initialize when first called
_pipe = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        # Using StarCoder - best model for code generation
        # Priority: StarCoder > CodeGen > DistilGPT2
        try:
            model_name = "bigcode/starcoderbase"
            _pipe = pipeline("text-generation", model=model_name)
            print(f"✓ Loaded model: {model_name}")
        except Exception as e:
            # Fallback to CodeGen if StarCoder fails
            try:
                model_name = "Salesforce/codegen-350M-mono"
                _pipe = pipeline("text-generation", model=model_name)
                print(f"✓ Loaded fallback model: {model_name}")
            except Exception as e2:
                # Final fallback to DistilGPT2
                model_name = "distilgpt2"
                _pipe = pipeline("text-generation", model=model_name)
                print(f"✓ Loaded backup model: {model_name}")
    return _pipe

def generate_code_from_description(api_desc, archetype=""):
    prompt = f"""
You are a senior software engineer. Write full Java classes to implement the following API:

{api_desc}

Archetype code (optional):
{archetype}

Return only valid Java code.
"""
    try:
        pipe = get_pipeline()
        result = pipe(prompt, max_new_tokens=1024, do_sample=False)[0]["generated_text"]
        return result
    except Exception as e:
        # Fallback to a simple template if model fails
        return f"""
public class GeneratedAPI {{
    // API Description:
    // {api_desc}
    
    // Note: Model loading failed. Please check your internet connection.
    // Error: {str(e)}
    
    // Implement your API endpoints here based on the description above
}}
"""