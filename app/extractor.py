import re
def extract_email(text):
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match=re.search(pattern,text)
    return match.group() if match else None

def extract_phone(text):
    pattern=r"(\+?\d{1,3}[- ]?)?\d{10}"
    match = re.search(pattern,text)
    return match.group() if match else None

def extract_name(text):
    """
    Simple approach:
    Assume the first non-empty line is the candidate's name.
    """
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if line:
            return line

    return None