"""Prompts for text simplification using evidence-based dyslexia guidelines"""
from api.schemas.common import SimplificationMode, SimplificationIntensity


def get_simplification_prompt(
    text: str,
    mode: SimplificationMode,
    intensity: SimplificationIntensity,
    max_sentence_length: int,
    options: dict
) -> str:
    """Generate the appropriate simplification prompt based on mode and settings"""
    
    # Base rules (British Dyslexia Association guidelines)
    base_rules = f"""
You are an expert text simplifier for people with dyslexia. Follow these evidence-based rules:

**Sentence Structure:**
- Maximum {max_sentence_length} words per sentence
- Use active voice exclusively (avoid passive constructions)
- One idea per sentence
- Avoid double negatives
- Use simple conjunctions (and, but, so)

**Vocabulary:**
- Replace complex words (>6 letters) with simpler alternatives
- Avoid words with silent letters when possible
- Use everyday language over technical jargon
- Provide simple definitions in parentheses when technical terms are essential

**Paragraph Structure:**
- Short paragraphs: {options.get('paragraph_max_sentences', 3)} sentences maximum
- Use bullet points for lists
- One main idea per paragraph
- Generous spacing between paragraphs

**Formatting:**
- Left-aligned text
- Use bold for emphasis (never italics or underline)
- Never use ALL CAPS for continuous text

**Content Clarity:**
- Use concrete examples over abstract concepts
- Break complex explanations into step-by-step instructions
- Provide context before introducing new concepts
"""
    
    # Mode-specific instructions
    mode_instructions = {
        SimplificationMode.GENERAL: """
**Mode: General (Everyday Content)**
- Target: News, emails, web content
- Convert complex lists to bullet points
- Use simple, everyday language
- Break down any complex sentences
""",
        SimplificationMode.ACADEMIC: """
**Mode: Academic (Educational Materials)**
- Target: Textbooks, research, educational content
- Define technical terms, don't remove them
- Use numbered steps for processes
- Preserve all facts, data, and citations
- Slightly longer sentences allowed (up to {max_sentence_length} words) for complex concepts
""",
        SimplificationMode.TECHNICAL: """
**Mode: Technical (Documentation & Manuals)**
- Target: How-to guides, documentation, manuals
- Define jargon in parentheses
- Use step-by-step numbered instructions
- Include concrete examples for abstract concepts
- Preserve technical accuracy
""",
        SimplificationMode.NARRATIVE: """
**Mode: Narrative (Stories & Fiction)**
- Target: Stories, fiction, creative writing
- Shorter sentences for faster pacing (max {max_sentence_length} words)
- Simple descriptive words
- Frequent paragraph breaks
- Maintain emotional tone and character voice
- Keep dialogue natural
""",
        SimplificationMode.INTERACTIVE: """
**Mode: Interactive (Analysis with Options)**
- Provide the original text with inline suggestions
- Format: complex_word [simpler1/simpler2/simpler3]
- Offer 3 versions: light/medium/heavy simplification
- Let the user choose their preferred level
"""
    }
    
    # Intensity-specific instructions
    intensity_instructions = {
        SimplificationIntensity.LIGHT: "- Minimal changes, only simplify the most complex parts",
        SimplificationIntensity.MEDIUM: "- Balanced simplification, replace most complex words",
        SimplificationIntensity.HEAVY: "- Maximum simplification, use only common vocabulary",
        SimplificationIntensity.CUSTOM: f"- Custom simplification with {max_sentence_length} words per sentence"
    }
    
    # Construct final prompt
    prompt = f"""{base_rules}

{mode_instructions.get(mode, mode_instructions[SimplificationMode.GENERAL])}

**Intensity Level:**
{intensity_instructions.get(intensity, intensity_instructions[SimplificationIntensity.MEDIUM])}

**Text to Simplify:**
{text}

**Instructions:**
Return ONLY the simplified text. Do not include explanations, notes, or metadata.
Maintain the original meaning while making it accessible for people with dyslexia.
"""
    
    return prompt


def get_mode_descriptions() -> dict:
    """Get descriptions of all available modes"""
    return {
        "general": {
            "name": "General",
            "description": "Everyday content like news, emails, and web pages",
            "max_sentence_length": 15,
            "use_case": "General reading and communication"
        },
        "academic": {
            "name": "Academic",
            "description": "Educational materials, textbooks, and research papers",
            "max_sentence_length": 18,
            "use_case": "Learning and studying"
        },
        "technical": {
            "name": "Technical",
            "description": "Documentation, manuals, and how-to guides",
            "max_sentence_length": 15,
            "use_case": "Following instructions and procedures"
        },
        "narrative": {
            "name": "Narrative",
            "description": "Stories, fiction, and creative writing",
            "max_sentence_length": 12,
            "use_case": "Reading for enjoyment"
        },
        "interactive": {
            "name": "Interactive",
            "description": "Analysis with multiple simplification options",
            "max_sentence_length": 15,
            "use_case": "Choosing your own simplification level"
        }
    }
