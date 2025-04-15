import re

def clean_email_content(email_body):
    """Clean email content to remove metadata or instructions.
    
    Args:
        email_body (str): Raw email content
        
    Returns:
        str: Cleaned email content
    """
    # Patterns to search and remove
    metadata_patterns = [
        r"This is the context you're working with:.*?(?=\n\n|\Z)",
        r"This is the summary of your work so far:.*?(?=\n\n|\Z)",
        r"Current Task:.*?(?=\n\n|\Z)",
        r"INSTRUCCIONES IMPORTANTES:.*?(?=\n\n|\Z)",
        r"Contexto:.*?(?=\n\n|\Z)",
        r"\*\*.*?\*\*",  # Text between double asterisks
        r"\[.*?\]",      # Text between brackets
        r"Análisis del tema:.*?(?=\n\n|\Z)",
        r"Verificar.*?(?=\n\n|\Z)",
        r"Organización.*?(?=\n\n|\Z)",
        r"Como (comunicador|investigador|analista).*?(?=\n\n|\Z)",
        r"INFORMACIÓN RECOPILADA:.*?(?=\n\n|\Z)",
        r"ANÁLISIS DEL TEMA:.*?(?=\n\n|\Z)",
        r"INFORMACIÓN ANALIZADA:.*?(?=\n\n|\Z)",
        r"DATOS DISPONIBLES:.*?(?=\n\n|\Z)",
    ]
    
    # Apply patterns to remove metadata
    cleaned_text = email_body
    for pattern in metadata_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove multiple empty lines
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    # Find greeting and everything that follows until signature
    email_pattern = r'(Estimad[oa]s?:?|Hola:?|Saludos:?)(.+?)(Atentamente|Cordialmente|Saludos|Hasta pronto)(.*?)$'
    email_match = re.search(email_pattern, cleaned_text, re.DOTALL | re.IGNORECASE)
    
    if email_match:
        # If we find an email pattern, extract only that part
        greeting = email_match.group(1).strip()
        body = email_match.group(2).strip()
        closing = email_match.group(3).strip()
        signature = email_match.group(4).strip()
        
        # Rebuild the email in an organized format
        cleaned_text = f"{greeting}\n\n{body}\n\n{closing},\n{signature}"
    else:
        # If the complete pattern is not found, ensure it has at least a greeting and signature
        if not any(greeting in cleaned_text.lower()[:100] for greeting in ['estimad', 'hola', 'saludos']):
            cleaned_text = "Estimado/a:\n\n" + cleaned_text
        
        if not any(closing in cleaned_text.lower()[-150:] for closing in ['atentamente', 'cordialmente', 'saludos']):
            if not "equipo de investigación" in cleaned_text.lower()[-150:]:
                cleaned_text += "\n\nAtentamente,\nEquipo de Investigación"
    
    return cleaned_text.strip()