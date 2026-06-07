# NativeFlow English

Web app en Streamlit para aprender inglés mediante simulaciones conversacionales inmersivas.

No es una app de gramática. Es un simulador para practicar situaciones reales como restaurante, hacer amigos, networking profesional y compra de software académico.

## Funciones del MVP

- Selección de escenario.
- Selección de personaje.
- Conversación en inglés con Gemini.
- Corrección al finalizar la sesión.
- Evaluación de claridad, naturalidad, gramática, vocabulario y confianza.
- Detección de errores recurrentes.
- Perfil básico de aprendizaje.
- Historial local de sesiones.

## Estructura

```text
nativeflow_english_app/
├── app.py
├── feedback.py
├── gemini_client.py
├── prompts.py
├── scenarios.py
├── storage.py
├── user_profile.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
└── data/
    └── .gitkeep
```

## Instalación local

```bash
pip install -r requirements.txt
```

Copia el archivo de ejemplo:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "TU_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

Ejecuta:

```bash
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube el proyecto a GitHub.
2. Entra a Streamlit Community Cloud.
3. Crea una nueva app desde tu repositorio.
4. Selecciona `app.py` como archivo principal.
5. En Settings > Secrets agrega:

```toml
GEMINI_API_KEY = "TU_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

6. Despliega.

## Nota sobre modelos Gemini

El MVP usa `gemini-2.5-flash` por ser un modelo con buen balance entre costo, velocidad y calidad para texto conversacional. Puedes cambiarlo desde los Secrets sin modificar código.

## Importante

No subas `.streamlit/secrets.toml` real a GitHub. Solo sube `secrets.toml.example`.
