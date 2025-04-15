# agents/template_agent.py
from agents.base import Agent
import re
import json
import os
import random
from datetime import datetime

class TemplateAgent(Agent):
    """Agente especializado en generar templates HTML personalizados."""
    
    def __init__(self, llm):
        super().__init__(
            name="Diseñador",
            role="Especialista en diseño visual y UX",
            goal="Crear templates HTML personalizados y atractivos para cada tipo de contenido",
            backstory="Diseñador visual con experiencia en crear experiencias visuales efectivas y adaptadas al contexto",
            llm=llm
        )
        self.templates_folder = "templates"
        self.ensure_templates_folder()
        self.template_library = self.load_template_library()
        
    def ensure_templates_folder(self):
        """Asegurar que existe el directorio de templates."""
        os.makedirs(self.templates_folder, exist_ok=True)
        
    def load_template_library(self):
        """Cargar biblioteca de templates o crear si no existe."""
        library_file = os.path.join(self.templates_folder, "template_library.json")
        
        if os.path.exists(library_file):
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Crear biblioteca por defecto
        default_library = {
            "templates": [
                {
                    "id": "business",
                    "name": "Profesional Corporativo",
                    "description": "Diseño profesional para comunicaciones corporativas",
                    "primary_color": "#1a5276",
                    "accent_color": "#3498db",
                    "suitable_for": ["negocios", "finanzas", "corporativo", "formal"],
                    "usage_count": 0
                },
                {
                    "id": "academic",
                    "name": "Académico",
                    "description": "Diseño formal para comunicaciones académicas y educativas",
                    "primary_color": "#6b5b95",
                    "accent_color": "#feb236",
                    "suitable_for": ["educación", "investigación", "universidad", "ciencia"],
                    "usage_count": 0
                },
                {
                    "id": "creative",
                    "name": "Creativo",
                    "description": "Diseño dinámico para temas creativos o innovadores",
                    "primary_color": "#26ae60",
                    "accent_color": "#e67e22",
                    "suitable_for": ["arte", "diseño", "innovación", "creativo", "marketing"],
                    "usage_count": 0
                },
                {
                    "id": "technical",
                    "name": "Técnico",
                    "description": "Diseño estructurado para información técnica o detallada",
                    "primary_color": "#34495e",
                    "accent_color": "#f1c40f",
                    "suitable_for": ["tecnología", "ingeniería", "desarrollo", "programación"],
                    "usage_count": 0
                },
                {
                    "id": "newsletter",
                    "name": "Boletín Informativo",
                    "description": "Diseño tipo newsletter para noticias e información",
                    "primary_color": "#e74c3c",
                    "accent_color": "#3498db",
                    "suitable_for": ["noticias", "actualidad", "eventos", "anuncios"],
                    "usage_count": 0
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(library_file, 'w', encoding='utf-8') as f:
            json.dump(default_library, f, ensure_ascii=False, indent=2)
            
        return default_library
        
    def select_template_for_content(self, topic, content, subject=None):
        """Seleccionar el template más adecuado basado en el contenido."""
        template_selection_prompt = f"""
        Analiza este tema y contenido de correo electrónico, y determina qué tipo de template sería más adecuado.
        
        TEMA: {topic}
        ASUNTO: {subject if subject else 'No disponible'}
        CONTENIDO: 
        {content[:1000]}  # Limitar para no exceder tokens
        
        Elige una de estas categorías de template:
        1. business - Para comunicaciones corporativas, formales o de negocios
        2. academic - Para temas educativos, investigación o contenido académico
        3. creative - Para contenido creativo, marketing o innovación
        4. technical - Para información técnica, tutoriales o desarrollo
        5. newsletter - Para noticias, eventos o actualizaciones periódicas
        
        Responde SOLO con la categoría (ej: "technical") sin explicaciones.
        """
        
        template_type = self.llm.generate(template_selection_prompt).strip().lower()
        
        # Validar respuesta
        valid_types = ["business", "academic", "creative", "technical", "newsletter"]
        if template_type not in valid_types:
            # Si la respuesta no es válida, intentar extraer
            for valid_type in valid_types:
                if valid_type in template_type:
                    template_type = valid_type
                    break
            else:
                # Si aún no se encuentra, usar business como default
                template_type = "business"
        
        # Encontrar el template correspondiente
        selected_template = None
        for template in self.template_library["templates"]:
            if template["id"] == template_type:
                selected_template = template
                template["usage_count"] += 1
                break
        
        # Si no se encuentra, usar el primero
        if not selected_template:
            selected_template = self.template_library["templates"][0]
            selected_template["usage_count"] += 1
        
        # Guardar biblioteca actualizada
        library_file = os.path.join(self.templates_folder, "template_library.json")
        self.template_library["last_updated"] = datetime.now().isoformat()
        with open(library_file, 'w', encoding='utf-8') as f:
            json.dump(self.template_library, f, ensure_ascii=False, indent=2)
        
        return selected_template
        
    def analyze_content_structure(self, content):
        """Analizar la estructura del contenido para adaptarla al template."""
        analysis_prompt = f"""
        Analiza este contenido de correo electrónico y extrae su estructura:
        
        {content}
        
        Identifica y devuelve en formato JSON:
        1. "greeting": El saludo inicial
        2. "paragraphs": Un array con los párrafos principales (solo texto)
        3. "bullet_points": Un array con cualquier lista de puntos
        4. "important_phrases": Frases o palabras que deberían destacarse
        5. "closing": La despedida o cierre
        6. "signature": La firma
        
        Responde solo con el JSON, sin explicaciones adicionales.
        """
        
        analysis_result = self.llm.generate(analysis_prompt).strip()
        
        # Intentar extraer el JSON
        try:
            # Buscar el primer { y el último }
            start = analysis_result.find('{')
            end = analysis_result.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = analysis_result[start:end]
                structure = json.loads(json_str)
            else:
                raise ValueError("No se encontró JSON válido")
        except (json.JSONDecodeError, ValueError):
            # Si falla, crear estructura básica
            print("Error analizando estructura, usando formato básico")
            
            # Intentar extraer partes básicas
            lines = content.split('\n')
            greeting = lines[0] if lines else "Estimado/a:"
            
            paragraphs = []
            bullet_points = []
            
            in_bullet_list = False
            current_paragraph = []
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    if current_paragraph:
                        paragraphs.append(" ".join(current_paragraph))
                        current_paragraph = []
                    in_bullet_list = False
                elif line.startswith('-') or line.startswith('•'):
                    in_bullet_list = True
                    bullet_points.append(line[1:].strip())
                elif in_bullet_list and (line.startswith(' ') or line.startswith('\t')):
                    # Continuación de un punto de lista
                    if bullet_points:
                        bullet_points[-1] += " " + line.strip()
                else:
                    current_paragraph.append(line)
            
            # Añadir el último párrafo si existe
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
            
            # Extraer firma
            signature = ""
            closing = "Atentamente,"
            
            for i, para in enumerate(paragraphs):
                if "atentamente" in para.lower():
                    closing = para
                    if i < len(paragraphs) - 1:
                        signature = " ".join(paragraphs[i+1:])
                        paragraphs = paragraphs[:i]
                    break
            
            structure = {
                "greeting": greeting,
                "paragraphs": paragraphs,
                "bullet_points": bullet_points,
                "important_phrases": [],
                "closing": closing,
                "signature": signature
            }
        
        return structure
    
    def generate_html_template(self, template_config, content_structure, subject):
        """Generar HTML basado en el template seleccionado y la estructura del contenido."""
        template_id = template_config["id"]
        primary_color = template_config["primary_color"]
        accent_color = template_config["accent_color"]
        
        # Según el template, ajustar estilos específicos
        styles = {
            "business": {
                "font": "Arial, sans-serif",
                "header_style": f"border-bottom: 3px solid {primary_color}; padding-bottom: 15px;",
                "heading_style": f"color: {primary_color}; font-size: 24px;",
                "paragraph_style": "line-height: 1.6;",
                "bullet_style": f"margin-left: 20px; color: {accent_color};",
                "highlight_style": f"background-color: #f8f9fa; border-left: 4px solid {accent_color}; padding: 10px 15px;",
                "footer_style": f"border-top: 1px solid #dddddd; color: #666666;"
            },
            "academic": {
                "font": "Georgia, serif",
                "header_style": f"border-bottom: 2px solid {primary_color}; padding-bottom: 12px;",
                "heading_style": f"color: {primary_color}; font-size: 26px; font-weight: normal;",
                "paragraph_style": "line-height: 1.8; text-align: justify;",
                "bullet_style": f"margin-left: 25px; color: {primary_color};",
                "highlight_style": f"background-color: #f9f7fd; border-left: 4px solid {accent_color}; padding: 15px;",
                "footer_style": f"border-top: 1px dotted #dddddd; color: {primary_color};"
            },
            "creative": {
                "font": "'Segoe UI', Tahoma, sans-serif",
                "header_style": f"border-bottom: 4px dotted {accent_color}; padding-bottom: 20px;",
                "heading_style": f"color: {primary_color}; font-size: 28px; letter-spacing: 1px;",
                "paragraph_style": "line-height: 1.7;",
                "bullet_style": f"margin-left: 15px; color: {accent_color};",
                "highlight_style": f"background-color: {primary_color}22; border-radius: 8px; padding: 15px;",
                "footer_style": f"border-top: 2px dashed {accent_color}88; color: {primary_color};"
            },
            "technical": {
                "font": "'Courier New', monospace",
                "header_style": f"border-bottom: 3px solid {primary_color}; padding-bottom: 10px;",
                "heading_style": f"color: {primary_color}; font-size: 22px; font-weight: bold;",
                "paragraph_style": "line-height: 1.5; font-size: 15px;",
                "bullet_style": f"margin-left: 30px; color: {accent_color}; font-family: monospace;",
                "highlight_style": f"background-color: #f5f5f5; border: 1px solid {accent_color}; border-radius: 4px; padding: 15px; font-family: monospace;",
                "footer_style": f"border-top: 1px solid {primary_color}; color: #555555; font-size: 13px;"
            },
            "newsletter": {
                "font": "Helvetica, Arial, sans-serif",
                "header_style": f"background-color: {primary_color}; color: white; padding: 20px;",
                "heading_style": "color: white; font-size: 26px; margin: 0;",
                "paragraph_style": "line-height: 1.6; color: #333;",
                "bullet_style": f"margin-left: 20px; color: {accent_color};",
                "highlight_style": f"background-color: {accent_color}22; border: 1px solid {accent_color}; padding: 15px; margin: 15px 0;",
                "footer_style": f"background-color: #f5f5f5; padding: 15px; color: #666; text-align: center;"
            }
        }
        
        # Si el template no está en estilos, usar business por defecto
        style = styles.get(template_id, styles["business"])
        
        # Construir el HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: {style["font"]};
                    line-height: 1.6;
                    color: #333333;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 5px;
                }}
                .header {{
                    {style["header_style"]}
                }}
                .heading {{
                    {style["heading_style"]}
                }}
                .content p {{
                    {style["paragraph_style"]}
                }}
                .content ul li {{
                    {style["bullet_style"]}
                }}
                .highlight {{
                    {style["highlight_style"]}
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 10px;
                    {style["footer_style"]}
                }}
                .signature {{
                    font-weight: bold;
                    color: {primary_color};
                }}
                @media only screen and (max-width: 620px) {{
                    .container {{
                        width: 100% !important;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
        """
        
        # Header específico según el tipo de template
        if template_id == "newsletter":
            html += f"""
                <div class="header">
                    <h1 class="heading">{subject}</h1>
                    <p style="color: white; margin-top: 5px;">Newsletter - {datetime.now().strftime("%d %B, %Y")}</p>
                </div>
            """
        else:
            html += f"""
                <div class="header">
                    <h1 class="heading">{subject}</h1>
                </div>
            """
        
        # Contenido
        html += f"""
                <div class="content">
                    <p><strong>{content_structure.get("greeting", "Estimado/a:")}</strong></p>
        """
        
        # Párrafos
        for i, paragraph in enumerate(content_structure.get("paragraphs", [])):
            # Cada tercer párrafo en creative y newsletter se destaca
            if template_id in ["creative", "newsletter"] and i % 3 == 1:
                html += f"""
                    <div class="highlight">
                        <p>{paragraph}</p>
                    </div>
                """
            else:
                html += f"""
                    <p>{paragraph}</p>
                """
        
        # Puntos de lista
        if content_structure.get("bullet_points"):
            html += "<ul>"
            for point in content_structure.get("bullet_points"):
                html += f"<li>{point}</li>"
            html += "</ul>"
        
        # Si hay frases importantes, resaltarlas
        if content_structure.get("important_phrases"):
            html += "<div class=\"highlight\">"
            for phrase in content_structure.get("important_phrases"):
                html += f"<p><strong>{phrase}</strong></p>"
            html += "</div>"
        
        # Cierre y firma
        html += f"""
                    <p>{content_structure.get("closing", "Atentamente,")}</p>
                    <p class="signature">{content_structure.get("signature", "Equipo de Investigación")}</p>
                </div>
                
                <div class="footer">
                    <p>Este correo ha sido generado automáticamente por el Sistema Multiagente.</p>
                    <p>© {datetime.now().year} - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def execute_template_task(self, topic, content, subject):
        """Ejecutar tarea completa de generación de template."""
        print(f"🎨 {self.name} está analizando el contenido y seleccionando un template...")
        
        # 1. Seleccionar template adecuado
        selected_template = self.select_template_for_content(topic, content, subject)
        print(f"✅ Template seleccionado: {selected_template['name']}")
        
        # 2. Analizar estructura del contenido
        content_structure = self.analyze_content_structure(content)
        
        # 3. Generar HTML
        html_content = self.generate_html_template(selected_template, content_structure, subject)
        
        # Guardar el template usado
        template_file = os.path.join(self.templates_folder, f"{topic.replace(' ', '_').lower()}_template.html")
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_content