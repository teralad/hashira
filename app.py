import streamlit as st
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO
from parsers.openapi import parse_openapi
from parsers.word import parse_word_doc
from llm.generator import generate_code_from_description
from templates.writer import write_generated_code

st.set_page_config(
    page_title="Hashira - AI Code Generator",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Hashira - API Code Generator")
st.markdown("Generate Java code from API specifications using AI")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.info("""
    **Supported Input Formats:**
    - OpenAPI: .yaml, .yml, .json
    - Word Documents: .docx
    """)
    
    use_archetype = st.checkbox("Use Code Archetype", value=False)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Hashira uses the **bigcode/starcoderbase** model to generate 
    Java implementations from API specifications.
    
    First run will download ~6GB model.
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Input")
    
    uploaded_file = st.file_uploader(
        "Upload API Specification",
        type=["yaml", "yml", "json", "docx"],
        help="Upload your OpenAPI spec or Word document"
    )
    
    archetype_files = None
    if use_archetype:
        archetype_files = st.file_uploader(
            "Upload Archetype Java Files",
            type=["java"],
            accept_multiple_files=True,
            help="Upload example Java files to guide code generation"
        )

with col2:
    st.header("⚙️ Status")
    status_placeholder = st.empty()
    
if st.button("🚀 Generate Code", type="primary", use_container_width=True):
    if not uploaded_file:
        st.error("Please upload an API specification file first!")
    else:
        try:
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save uploaded file
                input_file = temp_path / uploaded_file.name
                input_file.write_bytes(uploaded_file.read())
                
                status_placeholder.info("📖 Parsing API specification...")
                
                # Parse input file
                if input_file.suffix in [".yaml", ".yml", ".json"]:
                    api_description = parse_openapi(input_file)
                elif input_file.suffix == ".docx":
                    api_description = parse_word_doc(input_file)
                else:
                    raise ValueError("Unsupported file type")
                
                st.success(f"✅ Parsed {uploaded_file.name}")
                
                # Process archetype files
                archetype_snippets = ""
                if use_archetype and archetype_files:
                    status_placeholder.info("📚 Processing archetype files...")
                    for arch_file in archetype_files:
                        content = arch_file.read().decode('utf-8')
                        archetype_snippets += f"\n// FILE: {arch_file.name}\n{content}"
                    st.success(f"✅ Loaded {len(archetype_files)} archetype files")
                
                # Generate code
                status_placeholder.info("🤖 Generating code with AI model... (this may take a minute)")
                with st.spinner("Running AI model..."):
                    generated_code = generate_code_from_description(api_description, archetype_snippets)
                
                st.success("✅ Code generation complete!")
                
                # Write generated code
                status_placeholder.info("💾 Writing Java files...")
                output_path = temp_path / "generated_code"
                output_path.mkdir(exist_ok=True)
                write_generated_code(generated_code, output_path)
                
                # Display generated code
                st.header("📦 Generated Code")
                
                java_files = list(output_path.glob("*.java"))
                
                if java_files:
                    st.success(f"✅ Generated {len(java_files)} Java files")
                    
                    # Show code in tabs
                    if len(java_files) <= 5:
                        tabs = st.tabs([f.name for f in java_files])
                        for tab, java_file in zip(tabs, java_files):
                            with tab:
                                code_content = java_file.read_text()
                                st.code(code_content, language="java")
                    else:
                        # If many files, use selectbox
                        selected_file = st.selectbox(
                            "Select file to view:",
                            java_files,
                            format_func=lambda x: x.name
                        )
                        if selected_file:
                            code_content = selected_file.read_text()
                            st.code(code_content, language="java")
                    
                    # Create ZIP for download
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for java_file in java_files:
                            zip_file.write(java_file, java_file.name)
                    
                    st.download_button(
                        label="📥 Download All Files (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="generated_code.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                else:
                    st.warning("No Java files were generated. The model output might need adjustment.")
                    st.text_area("Raw Generated Output", generated_code, height=300)
                
                status_placeholder.success("✅ All done!")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Hugging Face Transformers")
