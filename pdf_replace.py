import fitz
import os
import argparse
import sys

def replace_text_in_pdf(file_path, search_str, replace_str):
    """Replaces text in a single PDF file using redaction."""
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"Error opening {file_path}: {e}")
        return False

    changed = False
    for page in doc:
        # Search for the string
        text_instances = page.search_for(search_str)
        if not text_instances:
            continue
            
        changed = True
        replacements = []
        
        for inst in text_instances:
            # Try to capture original font size
            text_dict = page.get_text("dict", clip=inst)
            font_size = 10 # Default
            try:
                if text_dict["blocks"]:
                    for block in text_dict["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    if search_str.lower() in span["text"].lower():
                                        font_size = span["size"]
                                        break
            except:
                pass

            # Apply redaction (white out the old text)
            page.add_redact_annot(inst, fill=(1, 1, 1))
            replacements.append((inst.x0, inst.y0, font_size))
            
        page.apply_redactions()
        
        # Insert new text
        for x0, y0, f_size in replacements:
            # Using standard Helvetica (helv) as it's built into PDFs
            page.insert_text((x0, y0 + f_size * 0.85), replace_str, 
                             fontsize=f_size, fontname="helv", color=(0, 0, 0))
            
    if changed:
        temp_path = file_path + ".tmp_repl"
        try:
            doc.save(temp_path)
            doc.close()
            os.replace(temp_path, file_path)
            print(f"Successfully updated: {file_path}")
            return True
        except PermissionError:
            doc.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"PERMISSION ERROR: Could not save {file_path}. Is it open in another program?")
            return False
        except Exception as e:
            doc.close()
            print(f"ERROR saving {file_path}: {e}")
            return False
    else:
        doc.close()
        print(f"No matches found in: {file_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generic PDF text replacement tool.")
    parser.add_argument("search", help="The text string to search for")
    parser.add_argument("replace", help="The text string to replace it with")
    parser.add_argument("paths", nargs="+", help="One or more PDF files or directories to process")
    
    args = parser.parse_args()

    files_to_process = []
    for path in args.paths:
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith(".pdf"):
                    files_to_process.append(os.path.join(path, f))
        elif os.path.isfile(path):
            if path.lower().endswith(".pdf"):
                files_to_process.append(path)
            else:
                print(f"Skipping non-PDF file: {path}")
        else:
            print(f"Path not found: {path}")

    if not files_to_process:
        print("No valid PDF files identified to process.")
        sys.exit(1)

    print(f"Searching for '{args.search}' and replacing with '{args.replace}'...")
    success_count = 0
    for file_path in files_to_process:
        if replace_text_in_pdf(file_path, args.search, args.replace):
            success_count += 1
    
    print(f"\nDone. Processed {len(files_to_process)} files. {success_count} files were modified.")

if __name__ == "__main__":
    main()
