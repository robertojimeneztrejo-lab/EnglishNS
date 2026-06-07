from scenarios import SCENARIOS, LEVELS, TONES

APP_COACHING_PRINCIPLES = """
The product is not a grammar course. It is a simulation-based English trainer for Spanish speakers.
The user must practice thinking in English through realistic situations.
Prioritize: clarity, naturalness, useful phrases, and confidence.
Avoid long lectures during the conversation. Save corrections for the final debrief unless communication breaks down.
"""


def build_roleplay_prompt(scenario_name: str, character_name: str, level: str, tone: str) -> str:
    scenario = SCENARIOS[scenario_name]
    character_prompt = scenario["characters"][character_name]
    level_prompt = LEVELS[level]
    tone_prompt = TONES[tone]
    return f"""
{APP_COACHING_PRINCIPLES}

You are running an English roleplay simulation.

Scenario: {scenario_name}
Scenario description: {scenario['description']}
User goal: {scenario['user_goal']}
Character: {character_name}
Character behavior: {character_prompt}
Difficulty: {level_prompt}
Target tone for the user: {tone_prompt}

Rules:
1. Speak only in English during the roleplay.
2. Stay in character.
3. Keep each reply between 1 and 5 sentences.
4. Ask follow-up questions to keep the user speaking.
5. Do not translate every message unless the user is stuck.
6. If the user's English has mistakes but is understandable, continue naturally.
7. If the user's message is unclear, ask a realistic clarification question.
8. Do not give a full correction until the final debrief.
9. Use natural English, contractions, and situation-appropriate expressions.
10. End your message with a question or clear conversational cue.

Start the simulation with a realistic opening line.
"""


def build_conversation_prompt(system_prompt: str, history: list[dict]) -> str:
    transcript = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Character"
        transcript.append(f"{role}: {msg['content']}")
    return system_prompt + "\n\nConversation so far:\n" + "\n".join(transcript) + "\n\nContinue the roleplay as the character."


def build_feedback_prompt(history: list[dict], scenario_name: str, tone: str, level: str) -> str:
    transcript = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "AI Character"
        transcript.append(f"{role}: {msg['content']}")
    return f"""
Act as an expert English coach for Spanish speakers.

Analyze this roleplay conversation.
Scenario: {scenario_name}
Target tone: {tone}
Difficulty: {level}

Transcript:
{chr(10).join(transcript)}

Return the feedback in Spanish using this exact structure:

## Evaluación rápida
- Claridad: X/10
- Naturalidad: X/10
- Gramática: X/10
- Vocabulario: X/10
- Confianza comunicativa: X/10

## Lo que hiciste bien
- Bullet points concretos.

## Correcciones principales
For each correction include:
- Lo que escribiste
- Mejor versión natural
- Por qué suena mejor

## Expresiones nativas que pudiste usar
Give 5 useful phrases related to the scenario.

## Patrón de aprendizaje detectado
Explain the likely recurring pattern from a Spanish speaker perspective.

## Mini práctica para mañana
Give 3 short exercises based on the errors.

## Frase modelo final
Rewrite the user's best possible version for this scenario in natural English.
"""


def build_error_extraction_prompt(feedback_text: str) -> str:
    return f"""
Extract recurring English learning issues from this feedback.
Return only valid JSON, no markdown.
Schema:
{{
  "errors": [
    {{"mistake": "...", "correction": "...", "category": "grammar|vocabulary|naturalness|preposition|tone|structure", "note": "..."}}
  ]
}}

Feedback:
{feedback_text}
"""


def build_native_expression_extraction_prompt(feedback_text: str) -> str:
    return f"""
Extract native/natural English expressions from this feedback.
Return only valid JSON, no markdown.
Schema:
{{
  "expressions": [
    {{
      "expression": "...",
      "meaning": "brief meaning in Spanish",
      "scenario": "business|restaurant|friends|travel|general",
      "tone": "casual|professional|neutral",
      "example": "short example sentence in English"
    }}
  ]
}}

Rules:
- Extract expressions the user could realistically reuse.
- Prefer phrases that sound natural, not textbook-like.
- Avoid duplicates.
- Maximum 8 expressions.

Feedback:
{feedback_text}
"""
