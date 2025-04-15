
import json
import os
from datetime import datetime

class AgenteMemoria:
    """Sistema de memoria para agentes que permite almacenar y aprender de interacciones pasadas."""
    
    def __init__(self, nombre_agente, archivo_memoria=None):
        """Inicializar sistema de memoria para un agente.
        
        Args:
            nombre_agente (str): Nombre del agente
            archivo_memoria (str, opcional): Ruta al archivo de memoria
        """
        self.nombre_agente = nombre_agente
        self.archivo_memoria = archivo_memoria or f"memory/{nombre_agente.lower()}_memoria.json"
        self.asegurar_directorio_memoria()
        self.memoria = self.cargar_memoria()
    
    def asegurar_directorio_memoria(self):
        """Asegurar que el directorio de memoria exista."""
        os.makedirs(os.path.dirname(self.archivo_memoria), exist_ok=True)
    
    def cargar_memoria(self):
        """Cargar memoria desde archivo o inicializar memoria vacía."""
        try:
            with open(self.archivo_memoria, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "tareas_previas": [],
                "resultados_exitosos": [],
                "temas": {},
                "metricas_rendimiento": {}
            }
    
    def guardar_memoria(self):
        """Guardar memoria en archivo."""
        with open(self.archivo_memoria, 'w', encoding='utf-8') as f:
            json.dump(self.memoria, f, ensure_ascii=False, indent=2)
    
    def agregar_tarea(self, descripcion_tarea, resultado, calificacion_exito, tema=None):
        """Añadir una tarea completada a la memoria.
        
        Args:
            descripcion_tarea (str): Descripción de la tarea
            resultado (str): Resultado de la tarea
            calificacion_exito (int): Calificación del éxito (1-10)
            tema (str, opcional): Tema de la tarea
        """
        entrada_tarea = {
            "timestamp": datetime.now().isoformat(),
            "descripcion": descripcion_tarea,
            "muestra_resultado": resultado[:500],  # Almacenar una muestra del resultado
            "calificacion_exito": calificacion_exito,
            "tema": tema
        }
        
        self.memoria["tareas_previas"].append(entrada_tarea)
        
        # Si la tarea fue exitosa, almacenarla como ejemplo
        if calificacion_exito >= 8:  # Considerar 8+ como exitoso
            self.memoria["resultados_exitosos"].append({
                "descripcion": descripcion_tarea,
                "resultado": resultado,
                "tema": tema
            })
        
        # Actualizar información del tema
        if tema:
            if tema not in self.memoria["temas"]:
                self.memoria["temas"][tema] = {"contador": 0, "exito_promedio": 0}
            
            datos_tema = self.memoria["temas"][tema]
            datos_tema["contador"] += 1
            datos_tema["exito_promedio"] = ((datos_tema["exito_promedio"] * (datos_tema["contador"] - 1)) 
                                         + calificacion_exito) / datos_tema["contador"]
        
        self.guardar_memoria()
    
    def obtener_tareas_exitosas_similares(self, descripcion_tarea, tema=None, limite=3):
        """Encontrar tareas exitosas similares en la memoria.
        
        Args:
            descripcion_tarea (str): Descripción de la tarea actual
            tema (str, opcional): Tema de la tarea
            limite (int, opcional): Número máximo de resultados
            
        Returns:
            list: Tareas similares encontradas
        """
        # Esta es una versión simplificada. En un sistema real, usarías
        # similitud semántica o correspondencia de palabras clave
        coincidencias = []
        
        for tarea in self.memoria["resultados_exitosos"]:
            # Coincidencia por tema si se proporciona
            if tema and tarea.get("tema") == tema:
                coincidencias.append(tarea)
            # Correspondencia básica de palabras clave
            elif any(palabra in tarea["descripcion"].lower() for palabra in descripcion_tarea.lower().split()):
                coincidencias.append(tarea)
        
        return coincidencias[:limite]