import re

def write_generated_code(code_str, output_dir):
    class_defs = re.findall(r'(public\s+class\s+\w+\s*\{[^}]*\})', code_str, re.DOTALL)
    if not class_defs:
        # fallback to simple split if regex fails
        parts = code_str.split("class ")
        for part in parts[1:]:
            lines = part.splitlines()
            class_name = lines[0].split(" ")[0].strip("{")
            file_path = output_dir / f"{class_name}.java"
            with open(file_path, "w") as f:
                f.write("class " + part)
        return

    for class_def in class_defs:
        match = re.search(r'public\s+class\s+(\w+)', class_def)
        if match:
            class_name = match.group(1)
            file_path = output_dir / f"{class_name}.java"
            with open(file_path, "w") as f:
                f.write(class_def)
