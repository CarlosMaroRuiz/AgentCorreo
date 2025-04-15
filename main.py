import os
import re
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from llm.deepseek import DeepSeekAPI
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.communicator import CommunicatorAgent
from agents.template_agent import TemplateAgent
from workflow.task import Task
from workflow.workflow import MultiAgentWorkflow
from utils.email_utils import send_email
from utils.text_processing import clean_email_content
from config.settings import DEFAULT_EMAIL_RECIPIENTS
from memory.agente_memory import AgenteMemoria

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definir estados de la conversación
CHOOSING_TOPIC = 0
CONFIRMING_SEND = 1

# Almacenar datos de conversaciones activas
conversation_data = {}

# Inicializar recursos compartidos
deepseek = DeepSeekAPI(model="deepseek-chat", temperature=0.7)

# Inicializar agentes
investigador = ResearcherAgent(deepseek)
investigador.memoria = AgenteMemoria("Investigador")

analista = AnalystAgent(deepseek)
analista.memoria = AgenteMemoria("Analista")

comunicador = CommunicatorAgent(deepseek)
comunicador.memoria = AgenteMemoria("Comunicador")

disenador = TemplateAgent(deepseek)
disenador.memoria = AgenteMemoria("Disenador")

# Token de Telegram (agregar a settings.py y .env)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación y solicita el tema."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hola {user.mention_html()}! Soy un bot que genera correos profesionales sobre cualquier tema.\n\n"
        f"¿Sobre qué tema deseas crear un correo?",
        reply_markup=ForceReply(selective=True),
    )
    return CHOOSING_TOPIC


async def topic_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa el tema y comienza el sistema multiagente."""
    tema = update.message.text
    chat_id = update.effective_chat.id
    
    # Almacenar tema en datos de conversación
    conversation_data[chat_id] = {"tema": tema}
    
    await update.message.reply_text(f"Procesando correo sobre: '{tema}'\n\nEsto puede tomar un momento...")
    
    # Ejecutar procesamiento asíncrono
    await generate_email(update, context, tema, chat_id)
    
    await update.message.reply_text(
        f"Correo generado sobre '{tema}'.\n\n"
        f"¿Quieres que envíe este correo a los destinatarios configurados? (sí/no)"
    )
    
    return CONFIRMING_SEND


async def generate_email(update: Update, context: ContextTypes.DEFAULT_TYPE, tema: str, chat_id: int) -> None:
    """Genera el correo usando el sistema multiagente."""
    # Generar asunto
    await update.message.reply_text("Generando asunto...")
    
    prompt_asunto = f"""
    Genera un asunto de correo electrónico corto, profesional y atractivo para un correo sobre:
    {tema}
    
    El asunto debe ser muy breve (máximo 8 palabras) y conciso, pero informativo.
    Responde ÚNICAMENTE con el asunto, sin explicaciones ni texto adicional.
    """
    
    asunto_email = deepseek.generate(prompt_asunto).strip()
    
    # Limpiar asunto
    if len(asunto_email.split('\n')) > 1:
        asunto_email = asunto_email.split('\n')[0]
    
    await update.message.reply_text(f"Asunto generado: {asunto_email}")
    
    # Refinar objetivos de agentes
    await update.message.reply_text("Refinando objetivos de los agentes...")
    
    investigador.refinar_objetivo(tema)
    analista.refinar_objetivo(tema)
    comunicador.refinar_objetivo(tema)
    disenador.refinar_objetivo(tema)
    
    # Buscar tareas similares en memoria
    tareas_similares = investigador.memoria.obtener_tareas_exitosas_similares(
        f"Investigación sobre {tema}", tema=tema
    )
    
    # Crear contexto de memoria
    contexto_memoria_texto = ""
    if tareas_similares:
        await update.message.reply_text(f"Se encontraron {len(tareas_similares)} tareas similares previas para aprender.")
        ejemplos_lista = []
        for i, tarea in enumerate(tareas_similares):
            ejemplos_lista.append(f"Ejemplo {i+1}:\n{tarea['resultado'][:300]}...")
        
        ejemplos = "\n\n".join(ejemplos_lista)
        contexto_de_memoria = f"Ejemplos de investigaciones exitosas en temas similares:\n{ejemplos}"
        contexto_memoria_texto = "CONTEXTO DE MEMORIA:\n" + contexto_de_memoria
    
    # Crear tareas
    descripcion_investigacion = f"""
        Investiga el tema "{tema}" y recopila información relevante.
        
        INSTRUCCIONES:
        1. Busca datos importantes sobre el tema
        2. Incluye definiciones, historia y aplicaciones
        3. Menciona 3-5 puntos interesantes
        4. Organiza la información de forma clara
        5. NO incluyas opiniones personales
        6. NO menciones frases como "Como investigador..."
        
        {contexto_memoria_texto}
        """
    
    tarea_investigacion = Task(
        description=descripcion_investigacion,
        agent=investigador
    )
    
    descripcion_analisis = f"""
        Analiza la siguiente información sobre "{tema}".
        
        INSTRUCCIONES:
        1. Identifica los 3-4 aspectos más importantes del tema
        2. Sintetiza la información de forma concisa
        3. Destaca los datos más interesantes
        4. Organiza el análisis de forma lógica
        5. NO añadas información nueva
        6. NO incluyas frases como "Como analista..."
        
        {{task_1}}
        """
    
    tarea_analisis = Task(
        description=descripcion_analisis,
        agent=analista
    )
    
    descripcion_comunicacion = f"""
        Crea un correo electrónico profesional sobre "{tema}" con el asunto "{asunto_email}".
        
        INSTRUCCIONES:
        1. Crea un correo electrónico profesional y bien estructurado
        2. Comienza con "Estimado/a:"
        3. Termina con "Atentamente, Equipo de Investigación"
        4. Usa viñetas para listar puntos importantes (precedidos por - o •)
        5. Separa cada párrafo con una línea en blanco
        6. Asegúrate de organizar la información en secciones claras
        7. Destaca 3-4 puntos clave sobre el tema
        8. NO incluyas metadatos ni explicaciones del proceso
        9. NO uses placeholders como [nombre]
        
        {{task_2}}
        """
    
    tarea_comunicacion = Task(
        description=descripcion_comunicacion,
        agent=comunicador
    )
    
    descripcion_template = f"""
        Genera un template HTML personalizado para el correo sobre "{tema}".
        Analiza el contenido y selecciona el formato visual más adecuado.
        
        INSTRUCCIONES:
        1. Analiza el tipo de contenido (académico, técnico, corporativo, etc.)
        2. Selecciona colores y estilos apropiados para el tema
        3. Estructura el contenido para máxima legibilidad
        4. Asegura que el diseño sea responsive y profesional
        5. Destaca elementos clave del contenido
        
        {{task_3}}
        """
    
    tarea_template = Task(
        description=descripcion_template,
        agent=disenador
    )
    
    # Crear flujo de trabajo
    flujo_trabajo = MultiAgentWorkflow(
        agents=[investigador, analista, comunicador, disenador],
        tasks=[tarea_investigacion, tarea_analisis, tarea_comunicacion, tarea_template]
    )
    
    await update.message.reply_text("Ejecutando flujo de trabajo con retroalimentación entre agentes...")
    
    # Ejecutar flujo
    resultados = flujo_trabajo.ejecutar_con_retroalimentacion()
    
    # Obtener contenido del correo
    cuerpo_email = resultados.get("task_3", "No se pudo generar el contenido del correo.")
    cuerpo_email = clean_email_content(cuerpo_email)
    
    # Obtener HTML
    html_email = resultados.get("task_4", None)
    
    # Si no se generó HTML correctamente, usar método especializado
    if not html_email or "<html" not in html_email.lower():
        await update.message.reply_text("Generando HTML personalizado para el correo...")
        try:
            html_email = flujo_trabajo.ejecutar_tarea_personalizada(
                3,  # Índice del agente diseñador (0-based)
                tema,
                cuerpo_email,
                asunto_email,
                method_name='execute_template_task'
            )
        except Exception as e:
            logger.error(f"Error al generar HTML: {str(e)}")
            # Crear HTML básico como respaldo
            content_formatted = cuerpo_email.replace('\n\n', '</p><p>').replace('\n', '<br>')
            html_email = f"""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8"><title>{asunto_email}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .content {{ padding: 20px 0; }}
                .footer {{ border-top: 1px solid #ddd; padding-top: 10px; font-size: 12px; }}
            </style></head>
            <body><div class="container">
                <div class="header"><h2>{asunto_email}</h2></div>
                <div class="content">{content_formatted}</div>
                <div class="footer"><p>Correo generado por Sistema Multiagente</p></div>
            </div></body></html>
            """
    
    # Guardar en memoria
    investigador.memoria.agregar_tarea(
        tarea_investigacion.description, 
        resultados.get("task_1", ""), 
        9,
        tema=tema
    )
    
    analista.memoria.agregar_tarea(
        tarea_analisis.description, 
        resultados.get("task_2", ""), 
        9,
        tema=tema
    )
    
    comunicador.memoria.agregar_tarea(
        tarea_comunicacion.description, 
        cuerpo_email, 
        9,
        tema=tema
    )
    
    # Guardar muestra de HTML
    html_sample = html_email[:500] + "..." if html_email and len(html_email) > 500 else html_email
    
    disenador.memoria.agregar_tarea(
        tarea_template.description,
        html_sample,
        9,
        tema=tema
    )
    
    # Guardar archivos
    filename_text = f"{tema.replace(' ', '_').lower()}_email.txt"
    filename_html = f"{tema.replace(' ', '_').lower()}_email.html"
    
    with open(filename_text, 'w', encoding='utf-8') as f:
        f.write(cuerpo_email)
    
    with open(filename_html, 'w', encoding='utf-8') as f:
        f.write(html_email)
    
    # Almacenar datos para envío posterior
    conversation_data[chat_id].update({
        "asunto": asunto_email,
        "cuerpo": cuerpo_email,
        "html": html_email,
        "filename_text": filename_text,
        "filename_html": filename_html
    })
    
    # Enviar contenido al usuario (dividir si es muy largo)
    max_length = 4000  # Límite de Telegram
    if len(cuerpo_email) > max_length:
        chunks = [cuerpo_email[i:i+max_length] for i in range(0, len(cuerpo_email), max_length)]
        for i, chunk in enumerate(chunks):
            await update.message.reply_text(f"Parte {i+1}/{len(chunks)} del correo:\n\n{chunk}")
    else:
        await update.message.reply_text(f"Correo generado:\n\n{cuerpo_email}")
    
    # Enviar archivo HTML como documento
    with open(filename_html, 'rb') as file:
        await context.bot.send_document(
            chat_id=chat_id,
            document=file,
            filename=filename_html,
            caption=f"Versión HTML del correo sobre '{tema}'"
        )


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manejar la confirmación para enviar el correo."""
    user_response = update.message.text.lower()
    chat_id = update.effective_chat.id
    
    if chat_id not in conversation_data:
        await update.message.reply_text("Lo siento, no encuentro datos de tu correo. Por favor inicia de nuevo con /start")
        return ConversationHandler.END
    
    data = conversation_data[chat_id]
    
    if "sí" in user_response or "si" in user_response or "yes" in user_response:
        await update.message.reply_text("Enviando correo a los destinatarios configurados...")
        
        # Verificar credenciales
        if os.getenv("EMAIL_SMTP_SERVER") and os.getenv("EMAIL_USERNAME"):
            success_count = 0
            for destinatario in DEFAULT_EMAIL_RECIPIENTS:
                try:
                    resultado_envio = send_email(
                        to=destinatario,
                        subject=data["asunto"],
                        body=data["html"],
                        is_html=True
                    )
                    if "exitosamente" in resultado_envio:
                        success_count += 1
                    await update.message.reply_text(f"Enviando a {destinatario}: {resultado_envio}")
                except Exception as e:
                    await update.message.reply_text(f"Error al enviar a {destinatario}: {str(e)}")
            
            if success_count > 0:
                await update.message.reply_text(f"✅ Correo enviado exitosamente a {success_count} destinatarios.")
            else:
                await update.message.reply_text("❌ No se pudo enviar el correo a ningún destinatario.")
        else:
            await update.message.reply_text(
                "No se encontraron credenciales de correo configuradas.\n"
                "Para enviar correos, configura las variables de entorno EMAIL_SMTP_SERVER y EMAIL_USERNAME."
            )
    else:
        await update.message.reply_text(
            f"El correo no ha sido enviado.\n\n"
            f"Puedes encontrar los archivos generados en:\n"
            f"- Texto: '{data['filename_text']}'\n"
            f"- HTML: '{data['filename_html']}'"
        )
    
    # Limpiar datos de conversación
    if chat_id in conversation_data:
        del conversation_data[chat_id]
    
    await update.message.reply_text(
        "Proceso completado. Puedes crear un nuevo correo cuando quieras usando /start"
    )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancelar y finalizar la conversación."""
    chat_id = update.effective_chat.id
    
    # Limpiar datos
    if chat_id in conversation_data:
        del conversation_data[chat_id]
    
    await update.message.reply_text(
        "Operación cancelada. Puedes iniciar de nuevo cuando quieras con /start"
    )
    
    return ConversationHandler.END


def main() -> None:
    """Iniciar el bot."""
    # Crear la aplicación con el token del bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Añadir manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, topic_received)],
            CONFIRMING_SEND: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Iniciar el bot
    application.run_polling()


if __name__ == '__main__':
    main()