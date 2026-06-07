import streamlit as st
import pandas as pd

from scenarios import SCENARIOS, LEVELS, TONES
from prompts import build_roleplay_prompt, build_conversation_prompt
from gemini_client import generate_text, GeminiClientError
from feedback import generate_feedback
from storage import load_profile, load_sessions

st.set_page_config(
    page_title="NativeFlow English",
    page_icon="🗣️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
.main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0.2rem;}
.subtitle {font-size: 1rem; color: #666; margin-bottom: 1.2rem;}
.metric-card {border: 1px solid #ddd; border-radius: 14px; padding: 1rem; background: #fafafa;}
.small-note {font-size: 0.85rem; color: #666;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "history": [],
        "system_prompt": "",
        "session_started": False,
        "feedback": "",
        "selected_scenario": "Restaurante",
        "selected_character": None,
        "selected_level": "Intermedio",
        "selected_tone": "Profesional",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session():
    st.session_state.history = []
    st.session_state.system_prompt = ""
    st.session_state.session_started = False
    st.session_state.feedback = ""


def start_session(scenario, character, level, tone):
    st.session_state.system_prompt = build_roleplay_prompt(scenario, character, level, tone)
    opening = generate_text(st.session_state.system_prompt, temperature=0.8)
    st.session_state.history = [{"role": "assistant", "content": opening}]
    st.session_state.session_started = True
    st.session_state.feedback = ""


def send_user_message(user_text):
    st.session_state.history.append({"role": "user", "content": user_text})
    prompt = build_conversation_prompt(st.session_state.system_prompt, st.session_state.history)
    answer = generate_text(prompt, temperature=0.8)
    st.session_state.history.append({"role": "assistant", "content": answer})


init_state()

st.markdown('<div class="main-title">NativeFlow English</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Un simulador conversacional para pensar en inglés, sonar natural y recibir corrección al final.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuración")

    scenario = st.selectbox("Escenario", list(SCENARIOS.keys()), index=list(SCENARIOS.keys()).index(st.session_state.selected_scenario))
    st.session_state.selected_scenario = scenario

    character_options = list(SCENARIOS[scenario]["characters"].keys())
    if st.session_state.selected_character not in character_options:
        st.session_state.selected_character = character_options[0]
    character = st.selectbox("Personaje", character_options, index=character_options.index(st.session_state.selected_character))
    st.session_state.selected_character = character

    level = st.selectbox("Nivel", list(LEVELS.keys()), index=list(LEVELS.keys()).index(st.session_state.selected_level))
    tone = st.selectbox("Tono objetivo", list(TONES.keys()), index=list(TONES.keys()).index(st.session_state.selected_tone))
    st.session_state.selected_level = level
    st.session_state.selected_tone = tone

    st.info(SCENARIOS[scenario]["description"])
    st.caption(f"Meta: {SCENARIOS[scenario]['user_goal']}")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Iniciar", use_container_width=True):
            try:
                start_session(scenario, character, level, tone)
                st.rerun()
            except GeminiClientError as exc:
                st.error(str(exc))
    with col_b:
        if st.button("Reiniciar", use_container_width=True):
            reset_session()
            st.rerun()

    st.divider()
    st.subheader("Tu perfil")
    profile = load_profile()
    st.metric("Sesiones", profile.get("total_sessions", 0))
    if profile.get("last_practice"):
        st.caption(f"Última práctica: {profile['last_practice']}")


tab_chat, tab_profile, tab_native, tab_history, tab_help = st.tabs(["Simulador", "Perfil de errores", "Expresiones nativas", "Historial", "Guía"])

with tab_chat:
    left, right = st.columns([2, 1])

    with left:
        st.subheader(f"{scenario} · {character}")

        if not st.session_state.session_started:
            st.warning("Configura tu escenario y presiona **Iniciar**. La IA abrirá la conversación en inglés.")
        else:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            user_text = st.chat_input("Responde en inglés...")
            if user_text:
                try:
                    send_user_message(user_text)
                    st.rerun()
                except GeminiClientError as exc:
                    st.error(str(exc))

            st.divider()
            if st.button("Finalizar y analizar mi conversación", type="primary"):
                try:
                    with st.spinner("Analizando claridad, naturalidad, errores y frases nativas..."):
                        feedback_text, profile = generate_feedback(
                            st.session_state.history,
                            scenario,
                            character,
                            level,
                            tone,
                        )
                        st.session_state.feedback = feedback_text
                    st.rerun()
                except GeminiClientError as exc:
                    st.error(str(exc))

        if st.session_state.feedback:
            st.markdown("## Debrief de la sesión")
            st.markdown(st.session_state.feedback)

    with right:
        st.markdown("### Cómo practicar")
        st.markdown(
            """
1. No traduzcas mentalmente palabra por palabra.  
2. Contesta aunque te equivoques.  
3. Mantén la conversación viva con preguntas.  
4. Al final revisa solo 2 o 3 errores clave.  
5. Repite el mismo escenario otro día con más naturalidad.
            """
        )
        st.markdown("### Frases comodín")
        st.code("Could you tell me a bit more about that?\nThat sounds interesting.\nLet me clarify what I mean.\nI’m not sure I understood correctly.\nCould we explore that option?", language="text")

with tab_profile:
    st.subheader("Errores recurrentes")
    profile = load_profile()
    errors = profile.get("common_errors", [])
    if errors:
        df = pd.DataFrame(errors)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay errores guardados. Finaliza una conversación para construir tu perfil.")

with tab_native:
    st.subheader("Expresiones nativas que pudiste usar")
    profile = load_profile()
    expressions = profile.get("native_expressions", [])

    if expressions:
        df = pd.DataFrame(expressions)
        preferred_columns = ["expression", "meaning", "scenario", "tone", "example", "count"]
        available_columns = [col for col in preferred_columns if col in df.columns]
        st.dataframe(df[available_columns], use_container_width=True)

        st.markdown("### Top 5 para practicar esta semana")
        for item in expressions[:5]:
            st.markdown(f"""
**{item.get('expression', '')}**  
Significado: {item.get('meaning', '')}  
Ejemplo: `{item.get('example', '')}`
""")
    else:
        st.info("Aún no hay expresiones guardadas. Finaliza una conversación para construir esta lista.")

with tab_history:
    st.subheader("Últimas sesiones")
    sessions = load_sessions(limit=10)
    if not sessions:
        st.info("Todavía no hay sesiones guardadas.")
    for idx, session in enumerate(sessions, start=1):
        with st.expander(f"{idx}. {session['created_at']} · {session['scenario']} · {session['character']}"):
            st.markdown(f"**Nivel:** {session['level']}  ")
            st.markdown(f"**Tono:** {session['tone']}")
            st.markdown("### Feedback")
            st.markdown(session.get("feedback", ""))

with tab_help:
    st.subheader("Instalación rápida")
    st.markdown(
        """
1. Sube estos archivos a un repositorio de GitHub.  
2. Crea tu app en Streamlit Community Cloud.  
3. En **Settings > Secrets**, agrega:

```toml
GEMINI_API_KEY = "TU_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

4. Ejecuta `app.py` como archivo principal.

**Importante:** nunca subas tu archivo real `.streamlit/secrets.toml` a GitHub.
        """
    )
    st.subheader("Próximas mejoras sugeridas")
    st.markdown(
        """
- Login de usuario.  
- Base de datos Supabase.  
- Modo carrera profesional.  
- Sistema de XP y niveles.  
- Audio con Gemini Live o TTS.  
- Exportar progreso a Excel.
        """
    )
