from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import os

# Set cache directory explicitly
cache_dir = "/app/.cache/huggingface"
os.environ["HF_HOME"] = cache_dir
os.environ["TRANSFORMERS_CACHE"] = cache_dir

# Lazy load the model - only initialize when first called
_pipe = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        # Try to load model from cache
        model_name = "Salesforce/codegen-350M-mono"
        
        try:
            print(f"Loading model from cache: {model_name}...")
            
            # Load tokenizer and model separately with explicit cache dir
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                local_files_only=True,
                trust_remote_code=True
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                local_files_only=True,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1  # CPU
            )
            
            print(f"✓ Successfully loaded: {model_name}")
            
        except Exception as e:
            print(f"✗ CodeGen failed: {str(e)[:200]}")
            print("Trying distilgpt2...")
            
            # Fallback to distilgpt2
            try:
                model_name = "distilgpt2"
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=cache_dir,
                    local_files_only=True
                )
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    cache_dir=cache_dir,
                    local_files_only=True
                )
                
                _pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1
                )
                
                print(f"✓ Successfully loaded: {model_name}")
                
            except Exception as e2:
                print(f"✗ All models failed. Error: {str(e2)[:200]}")
                _pipe = None
    
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

@RestController
@RequestMapping("/api")
public class GeneratedAPIController {{
    
    /**
     * API Specification:
     * {api_desc.replace(newline, newline + '     * ')}
     */
    
{newline.join(endpoints)}
    
    @GetMapping("/hello")
    public ResponseEntity<String> sayHello() {{
        return ResponseEntity.ok("Hello, World!");
    }}
    
    // Add your implementation here
}}
"""