from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
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
    archetype_text = f'Use this code style as reference:\n{archetype}\n' if archetype else ''
    
    prompt = f"""You are a senior Java developer. Generate complete, working Java code for the following API specification.

API Specification:
{api_desc}

{archetype_text}

Generate complete Java classes with:
- Proper package declarations
- All necessary imports
- RESTful endpoint annotations (@RestController, @GetMapping, etc.)
- Request/response handling
- Error handling
- Complete method implementations

Return ONLY valid, compilable Java code without any explanations."""

    try:
        pipe = get_pipeline()
        
        if pipe is None:
            raise RuntimeError("Model not loaded")
        
        # Generate code with optimized parameters
        result = pipe(
            prompt,
            max_new_tokens=800,
            do_sample=True,
            temperature=0.2,
            top_p=0.95,
            repetition_penalty=1.1
        )[0]["generated_text"]
        
        # Extract only the generated part (remove the prompt)
        if prompt in result:
            result = result.replace(prompt, "").strip()
        
        return result
        
    except Exception as e:
        print(f"Generation error: {str(e)}")
        # Return a basic but complete Java template
        endpoints = []
        for line in api_desc.split('\n'):
            if 'GET' in line or 'POST' in line or 'PUT' in line or 'DELETE' in line:
                endpoints.append(f"    // TODO: Implement {line.strip()}")
        
        newline = '\n'
        return f"""package com.example.api;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

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