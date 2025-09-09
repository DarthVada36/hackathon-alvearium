"""
Personality Manager para el Ratoncito Pérez
Adaptación dinámica de personalidad según contexto familiar y situacional
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass

from .prompts.base_prompts import Language, AgeGroup, prompt_template
from .context_manager import FamilyContext, InteractionType, RouteStage


class PersonalityStyle(Enum):
    """Estilos de personalidad del Ratoncito Pérez"""
    MAGICAL_STORYTELLER = "magical_storyteller"    # Cuentacuentos mágico
    WISE_GUIDE = "wise_guide"                      # Guía sabio y conocedor
    PLAYFUL_FRIEND = "playful_friend"              # Amigo juguetón
    CULTURAL_EDUCATOR = "cultural_educator"        # Educador cultural
    ADVENTURE_COMPANION = "adventure_companion"   # Compañero de aventuras


class EmotionalTone(Enum):
    """Tonos emocionales del agente"""
    ENTHUSIASTIC = "enthusiastic"      # Entusiasta y emocionado
    CALM_REASSURING = "calm_reassuring" # Calmado y tranquilizador
    ENCOURAGING = "encouraging"         # Alentador y motivador
    MYSTERIOUS = "mysterious"           # Misterioso e intrigante
    CELEBRATORY = "celebratory"        # Celebrativo y festivo


@dataclass
class PersonalityConfiguration:
    """Configuración de personalidad para una situación específica"""
    style: PersonalityStyle
    tone: EmotionalTone
    formality_level: float  # 0.0 = muy informal, 1.0 = muy formal
    energy_level: float     # 0.0 = muy calmado, 1.0 = muy energético
    educational_focus: float # 0.0 = pura diversión, 1.0 = educativo
    use_emojis: bool
    address_style: str      # Cómo dirigirse ("pequeños", "familia", "exploradores")


class PersonalityManager:
    """Gestiona la adaptación dinámica de personalidad del Ratoncito Pérez"""
    
    def __init__(self):
        self.personality_templates = self._initialize_personality_templates()
        self.interaction_adaptations = self._initialize_interaction_adaptations()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
    
    def _initialize_personality_templates(self) -> Dict[PersonalityStyle, Dict[Language, str]]:
        """Templates de personalidad por estilo e idioma"""
        return {
            PersonalityStyle.MAGICAL_STORYTELLER: {
                Language.SPANISH: """Adopta el rol de un cuentacuentos mágico. Usa un lenguaje rico en imágenes, 
metáforas encantadoras y referencias a leyendas. Crea narrativas que transportan a la audiencia a mundos mágicos 
conectados con la realidad histórica de Madrid. Incluye elementos de fantasía que hacen la información memorable.""",
                
                Language.ENGLISH: """Adopt the role of a magical storyteller. Use language rich in imagery, 
enchanting metaphors and references to legends. Create narratives that transport the audience to magical worlds 
connected with Madrid's historical reality. Include fantasy elements that make information memorable."""
            },
            
            PersonalityStyle.WISE_GUIDE: {
                Language.SPANISH: """Actúa como un guía sabio y experimentado. Comparte conocimiento profundo con 
paciencia y claridad. Usa un tono reflexivo y contemplativo. Conecta eventos históricos con lecciones de vida 
y sabiduría universal. Mantén una presencia tranquila pero autorizada.""",
                
                Language.ENGLISH: """Act as a wise and experienced guide. Share deep knowledge with patience and 
clarity. Use a reflective and contemplative tone. Connect historical events with life lessons and universal 
wisdom. Maintain a calm but authoritative presence."""
            },
            
            PersonalityStyle.PLAYFUL_FRIEND: {
                Language.SPANISH: """Comportarte como un amigo juguetón y divertido. Usa humor apropiado, juegos de 
palabras y actividades interactivas. Crea un ambiente relajado y alegre. Haz que el aprendizaje sea una experiencia 
divertida y sin presión. Celebra cada pequeño descubrimiento con entusiasmo.""",
                
                Language.ENGLISH: """Behave like a playful and fun friend. Use appropriate humor, wordplay and 
interactive activities. Create a relaxed and joyful atmosphere. Make learning a fun and pressure-free experience. 
Celebrate every small discovery with enthusiasm."""
            },
            
            PersonalityStyle.CULTURAL_EDUCATOR: {
                Language.SPANISH: """Asume el rol de un educador cultural apasionado. Proporciona contexto histórico 
rico y conexiones culturales profundas. Explica tradiciones, costumbres y significados con precisión y respeto. 
Fomenta la apreciación por el patrimonio cultural español.""",
                
                Language.ENGLISH: """Take on the role of a passionate cultural educator. Provide rich historical 
context and deep cultural connections. Explain traditions, customs and meanings with precision and respect. 
Foster appreciation for Spanish cultural heritage."""
            },
            
            PersonalityStyle.ADVENTURE_COMPANION: {
                Language.SPANISH: """Actúa como un compañero de aventuras emocionante. Genera expectativa y emoción 
por los descubrimientos. Usa lenguaje dinámico y energético. Plantea retos y misiones que motiven la exploración. 
Celebra logros como si fueran grandes conquistas.""",
                
                Language.ENGLISH: """Act as an exciting adventure companion. Generate anticipation and excitement 
for discoveries. Use dynamic and energetic language. Propose challenges and missions that motivate exploration. 
Celebrate achievements as if they were great conquests."""
            }
        }
    
    def _initialize_interaction_adaptations(self) -> Dict[InteractionType, PersonalityConfiguration]:
        """Configuraciones por tipo de interacción"""
        return {
            InteractionType.GREETING: PersonalityConfiguration(
                style=PersonalityStyle.PLAYFUL_FRIEND,
                tone=EmotionalTone.ENTHUSIASTIC,
                formality_level=0.3,
                energy_level=0.8,
                educational_focus=0.2,
                use_emojis=True,
                address_style="warm_welcome"
            ),
            
            InteractionType.LOCATION_QUESTION: PersonalityConfiguration(
                style=PersonalityStyle.CULTURAL_EDUCATOR,
                tone=EmotionalTone.CALM_REASSURING,
                formality_level=0.5,
                energy_level=0.6,
                educational_focus=0.8,
                use_emojis=True,
                address_style="informative"
            ),
            
            InteractionType.STORY_REQUEST: PersonalityConfiguration(
                style=PersonalityStyle.MAGICAL_STORYTELLER,
                tone=EmotionalTone.MYSTERIOUS,
                formality_level=0.2,
                energy_level=0.7,
                educational_focus=0.4,
                use_emojis=True,
                address_style="enchanting"
            ),
            
            InteractionType.NAVIGATION_HELP: PersonalityConfiguration(
                style=PersonalityStyle.WISE_GUIDE,
                tone=EmotionalTone.CALM_REASSURING,
                formality_level=0.6,
                energy_level=0.4,
                educational_focus=0.6,
                use_emojis=False,
                address_style="helpful"
            ),
            
            InteractionType.FAMILY_CHAT: PersonalityConfiguration(
                style=PersonalityStyle.PLAYFUL_FRIEND,
                tone=EmotionalTone.ENCOURAGING,
                formality_level=0.3,
                energy_level=0.6,
                educational_focus=0.3,
                use_emojis=True,
                address_style="conversational"
            ),
            
            InteractionType.ACHIEVEMENT_CHECK: PersonalityConfiguration(
                style=PersonalityStyle.ADVENTURE_COMPANION,
                tone=EmotionalTone.CELEBRATORY,
                formality_level=0.2,
                energy_level=0.9,
                educational_focus=0.3,
                use_emojis=True,
                address_style="celebratory"
            )
        }
    
    def _initialize_cultural_adaptations(self) -> Dict[Language, Dict[str, Any]]:
        """Adaptaciones culturales por idioma"""
        return {
            Language.SPANISH: {
                "emojis": ["🐭", "✨", "🏰", "🌟", "🎭", "🍭", "🏛️", "👑"],
                "expressions": ["¡Qué maravilla!", "¡Fantástico!", "¡Increíble!", "¡Genial!"],
                "address_forms": {
                    "formal": ["ustedes", "su familia"],
                    "informal": ["vosotros", "vuestra familia"],
                    "children": ["pequeños exploradores", "jóvenes aventureros"],
                    "mixed": ["querida familia", "aventureros"]
                },
                "cultural_references": ["duendes", "hadas", "castillos encantados", "tesoros mágicos"]
            },
            
            Language.ENGLISH: {
                "emojis": ["🐭", "✨", "🏰", "🌟", "🎭", "🍭", "🏛️", "👑"],
                "expressions": ["How wonderful!", "Fantastic!", "Incredible!", "Amazing!"],
                "address_forms": {
                    "formal": ["you", "your family"],
                    "informal": ["you all", "your family"],
                    "children": ["little explorers", "young adventurers"],
                    "mixed": ["dear family", "adventurers"]
                },
                "cultural_references": ["elves", "fairies", "enchanted castles", "magical treasures"]
            }
        }
    
    def determine_optimal_personality(self, context: FamilyContext, 
                                    interaction_type: Optional[InteractionType] = None,
                                    user_message: str = "") -> PersonalityConfiguration:
        """Determina la configuración de personalidad óptima"""
        
        # Configuración base según tipo de interacción
        if interaction_type and interaction_type in self.interaction_adaptations:
            config = self.interaction_adaptations[interaction_type]
        else:
            # Configuración por defecto
            config = PersonalityConfiguration(
                style=PersonalityStyle.PLAYFUL_FRIEND,
                tone=EmotionalTone.ENTHUSIASTIC,
                formality_level=0.4,
                energy_level=0.6,
                educational_focus=0.5,
                use_emojis=True,
                address_style="friendly"
            )
        
        # Ajustes por edad
        config = self._adjust_for_age_group(config, context.age_group)
        
        # Ajustes por etapa de ruta
        config = self._adjust_for_route_stage(config, context.route_stage)
        
        # Ajustes por progreso y puntos
        config = self._adjust_for_progress(config, context)
        
        # Ajustes por contenido del mensaje
        config = self._adjust_for_message_content(config, user_message)
        
        return config
    
    def _adjust_for_age_group(self, config: PersonalityConfiguration, 
                            age_group: AgeGroup) -> PersonalityConfiguration:
        """Ajusta personalidad según grupo de edad"""
        if age_group == AgeGroup.YOUNG_KIDS:
            config.energy_level = min(config.energy_level + 0.2, 1.0)
            config.formality_level = max(config.formality_level - 0.3, 0.0)
            config.educational_focus = max(config.educational_focus - 0.2, 0.0)
            config.use_emojis = True
            
        elif age_group == AgeGroup.TEENS:
            config.formality_level = min(config.formality_level + 0.2, 1.0)
            config.educational_focus = min(config.educational_focus + 0.3, 1.0)
            config.energy_level = max(config.energy_level - 0.1, 0.0)
            
        elif age_group == AgeGroup.ADULTS:
            config.formality_level = min(config.formality_level + 0.3, 1.0)
            config.educational_focus = min(config.educational_focus + 0.2, 1.0)
            config.use_emojis = False
            
        return config
    
    def _adjust_for_route_stage(self, config: PersonalityConfiguration, 
                              stage: RouteStage) -> PersonalityConfiguration:
        """Ajusta personalidad según etapa de la ruta"""
        if stage == RouteStage.NOT_STARTED:
            config.style = PersonalityStyle.ADVENTURE_COMPANION
            config.tone = EmotionalTone.ENTHUSIASTIC
            config.energy_level = min(config.energy_level + 0.3, 1.0)
            
        elif stage == RouteStage.AT_POI:
            config.style = PersonalityStyle.CULTURAL_EDUCATOR
            config.educational_focus = min(config.educational_focus + 0.3, 1.0)
            
        elif stage == RouteStage.COMPLETED:
            config.style = PersonalityStyle.ADVENTURE_COMPANION
            config.tone = EmotionalTone.CELEBRATORY
            config.energy_level = 1.0
            
        return config
    
    def _adjust_for_progress(self, config: PersonalityConfiguration, 
                           context: FamilyContext) -> PersonalityConfiguration:
        """Ajusta según progreso y puntos"""
        # Si han ganado muchos puntos, ser más celebrativo
        if context.total_points > 500:
            config.tone = EmotionalTone.CELEBRATORY
            config.energy_level = min(config.energy_level + 0.2, 1.0)
        
        # Si llevan mucho tiempo, ser más alentador
        progress_summary = context.get_route_progress_summary()
        if progress_summary.get("duration") and "h" in str(progress_summary["duration"]):
            config.tone = EmotionalTone.ENCOURAGING
            config.energy_level = max(config.energy_level - 0.1, 0.3)
        
        return config
    
    def _adjust_for_message_content(self, config: PersonalityConfiguration, 
                                  message: str) -> PersonalityConfiguration:
        """Ajusta según contenido del mensaje"""
        message_lower = message.lower()
        
        # Detectar solicitudes de historias
        story_keywords = ["historia", "cuento", "leyenda", "story", "tale", "legend"]
        if any(keyword in message_lower for keyword in story_keywords):
            config.style = PersonalityStyle.MAGICAL_STORYTELLER
            config.tone = EmotionalTone.MYSTERIOUS
        
        # Detectar preguntas sobre navegación
        nav_keywords = ["dónde", "cómo llegar", "where", "how to get", "dirección"]
        if any(keyword in message_lower for keyword in nav_keywords):
            config.style = PersonalityStyle.WISE_GUIDE
            config.tone = EmotionalTone.CALM_REASSURING
        
        # Detectar expresiones de cansancio o frustración
        tired_keywords = ["cansado", "tired", "aburrido", "bored"]
        if any(keyword in message_lower for keyword in tired_keywords):
            config.tone = EmotionalTone.ENCOURAGING
            config.energy_level = min(config.energy_level + 0.3, 1.0)
        
        return config
    
    def build_personality_prompt(self, config: PersonalityConfiguration, 
                               language: Language, context: FamilyContext) -> str:
        """Construye el prompt de personalidad específico"""
        
        # Obtener template base del estilo
        style_template = self.personality_templates[config.style][language]
        
        # Obtener adaptaciones culturales
        cultural_data = self.cultural_adaptations[language]
        
        # Construir instrucciones específicas
        personality_instructions = []
        
        # Instrucciones de tono
        tone_instructions = self._get_tone_instructions(config.tone, language)
        personality_instructions.append(tone_instructions)
        
        # Instrucciones de formalidad
        formality_instruction = self._get_formality_instructions(config.formality_level, language)
        personality_instructions.append(formality_instruction)
        
        # Instrucciones de energía
        energy_instruction = self._get_energy_instructions(config.energy_level, language)
        personality_instructions.append(energy_instruction)
        
        # Instrucciones de dirección
        address_instruction = self._get_address_instructions(config, context, language)
        personality_instructions.append(address_instruction)
        
        # Combinr todo
        full_prompt = f"{style_template}\n\n" + "\n".join(personality_instructions)
        
        return full_prompt
    
    def _get_tone_instructions(self, tone: EmotionalTone, language: Language) -> str:
        """Instrucciones específicas de tono emocional"""
        instructions = {
            Language.SPANISH: {
                EmotionalTone.ENTHUSIASTIC: "Mantén un tono entusiasta y emocionado. Expresa genuina alegría por cada descubrimiento.",
                EmotionalTone.CALM_REASSURING: "Usa un tono calmado y tranquilizador. Proyecta confianza y serenidad.",
                EmotionalTone.ENCOURAGING: "Sé alentador y motivador. Refuerza logros y anima a continuar.",
                EmotionalTone.MYSTERIOUS: "Adopta un aire misterioso e intrigante. Crea expectativa y curiosidad.",
                EmotionalTone.CELEBRATORY: "Celebra con alegría y orgullo. Reconoce logros con entusiasmo genuino."
            },
            Language.ENGLISH: {
                EmotionalTone.ENTHUSIASTIC: "Maintain an enthusiastic and excited tone. Express genuine joy for each discovery.",
                EmotionalTone.CALM_REASSURING: "Use a calm and reassuring tone. Project confidence and serenity.",
                EmotionalTone.ENCOURAGING: "Be encouraging and motivating. Reinforce achievements and encourage continuation.",
                EmotionalTone.MYSTERIOUS: "Adopt a mysterious and intriguing air. Create expectation and curiosity.",
                EmotionalTone.CELEBRATORY: "Celebrate with joy and pride. Acknowledge achievements with genuine enthusiasm."
            }
        }
        return instructions[language][tone]
    
    def _get_formality_instructions(self, level: float, language: Language) -> str:
        """Instrucciones de nivel de formalidad"""
        if language == Language.SPANISH:
            if level < 0.3:
                return "Usa un lenguaje muy informal y cercano. Tutea naturalmente."
            elif level < 0.7:
                return "Mantén un balance entre cercanía y respeto. Usa un tono amigable pero apropiado."
            else:
                return "Usa un lenguaje más formal y respetuoso, pero mantén la calidez."
        else:
            if level < 0.3:
                return "Use very informal and close language. Be naturally friendly."
            elif level < 0.7:
                return "Maintain a balance between closeness and respect. Use a friendly but appropriate tone."
            else:
                return "Use more formal and respectful language, but maintain warmth."
    
    def _get_energy_instructions(self, level: float, language: Language) -> str:
        """Instrucciones de nivel de energía"""
        if language == Language.SPANISH:
            if level < 0.3:
                return "Mantén un ritmo calmado y pausado. Proyecta tranquilidad."
            elif level < 0.7:
                return "Usa un nivel de energía moderado y equilibrado."
            else:
                return "Sé dinámico y enérgico. Expresa vitalidad y entusiasmo."
        else:
            if level < 0.3:
                return "Maintain a calm and leisurely pace. Project tranquility."
            elif level < 0.7:
                return "Use a moderate and balanced energy level."
            else:
                return "Be dynamic and energetic. Express vitality and enthusiasm."
    
    def _get_address_instructions(self, config: PersonalityConfiguration, 
                                context: FamilyContext, language: Language) -> str:
        """Instrucciones de cómo dirigirse a la familia"""
        cultural_data = self.cultural_adaptations[language]
        address_forms = cultural_data["address_forms"]
        
        if context.children and context.adults:
            forms = address_forms["mixed"]
        elif context.children:
            forms = address_forms["children"]
        else:
            forms = address_forms["formal"] if config.formality_level > 0.6 else address_forms["informal"]
        
        example_form = forms[0] if forms else "familia"
        
        if language == Language.SPANISH:
            return f"Dirígete a ellos como '{example_form}' y similares. Usa nombres específicos cuando sea apropiado."
        else:
            return f"Address them as '{example_form}' and similar. Use specific names when appropriate."


# Instancia global
personality_manager = PersonalityManager()