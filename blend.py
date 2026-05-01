import streamlit as st
from groq import Groq
import os

# =========================================================
# 1. CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="BlendAI", layout="wide", page_icon="🎮")

ICONO_IA = "https://upload.wikimedia.org/wikipedia/commons/0/0c/Blender_logo_no_text.svg"
ICONO_USUARIO = "👨‍🎨"

st.markdown("""
<style>
.stApp { background-color: #121212; color: #FFFFFF; }

.stButton>button {
    border-radius: 15px;
    border: 1px solid #444;
    background-color: #1E1E1E;
    color: white;
    transition: 0.3s;
}

.stButton>button:hover {
    border: 1px solid #00FFCC;
    color: #00FFCC;
}

.block {
    background-color: #1E1E1E;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. IA (STREAMLIT CLOUD + GROQ)
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Comprobación de seguridad
if not GROQ_API_KEY:
    st.error("❌ No se encontró la API KEY de Groq.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================================================
# 3. ESTADO DEL JUEGO
# =========================================================
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "level" not in st.session_state:
    st.session_state.level = 1

if "mission" not in st.session_state:
    st.session_state.mission = None

if "mission_step" not in st.session_state:
    st.session_state.mission_step = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "unlocked" not in st.session_state:
    st.session_state.unlocked = ["Cubo"]

# =========================================================
# 4. MISIONES
# =========================================================
MISSIONS = {
    "Cubo": [
        "Abrir Blender y limpiar escena",
        "Crear cubo base",
        "Mover, escalar y rotar",
        "Aplicar material simple"
    ],

    "Donut": [
        "Crear torus base",
        "Subdividir modelo",
        "Crear material de glaseado",
        "Render básico"
    ],

    "Coche": [
        "Bloqueo del cuerpo",
        "Añadir ruedas",
        "Modelado low-poly",
        "Material final"
    ]
}

# =========================================================
# 5. SISTEMA XP
# =========================================================
def add_xp(amount):
    st.session_state.xp += amount
    st.session_state.level = 1 + st.session_state.xp // 50

# =========================================================
# 6. IA TUTOR
# =========================================================
def ask_ai(prompt):

    system = f"""
Eres BlendAI, un tutor experto de Blender.

REGLAS:
- Explica paso a paso
- Fácil para principiantes
- Usa emojis moderadamente
- Solo un paso por respuesta
- Explica herramientas y atajos
- Enseña Blender de forma divertida

DATOS DEL USUARIO:
Nivel: {st.session_state.level}
Misión: {st.session_state.mission}
Paso actual: {st.session_state.mission_step}
"""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    try:

        # MODELO NUEVO Y ESTABLE
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=700
        )

        return res.choices[0].message.content

    except Exception as e:
        return f"❌ Error con Groq:\n\n{str(e)}"

# =========================================================
# 7. INICIAR MISIÓN
# =========================================================
def start_mission(name):

    st.session_state.mission = name
    st.session_state.mission_step = 0

    return ask_ai(
        f"Iniciamos la misión {name}. "
        f"Dame el PASO 1 detallado."
    )

# =========================================================
# 8. COMPLETAR PASO
# =========================================================
def complete_step():

    mission = st.session_state.mission

    st.session_state.mission_step += 1

    add_xp(10)

    if st.session_state.mission_step >= len(MISSIONS[mission]):

        add_xp(50)

        if mission == "Cubo" and "Donut" not in st.session_state.unlocked:
            st.session_state.unlocked.append("Donut")

        if mission == "Donut" and "Coche" not in st.session_state.unlocked:
            st.session_state.unlocked.append("Coche")

        st.session_state.mission = None

        return "🎉 ¡Misión completada! Has desbloqueado nuevas misiones."

    return ask_ai(
        "He completado el paso anterior. "
        "Dame el siguiente paso."
    )

# =========================================================
# 9. INTERFAZ
# =========================================================
st.title("🚀 BlendAI")
st.markdown("### Aprende Blender como un videojuego 🎮")

# =========================================================
# 10. SIDEBAR
# =========================================================
st.sidebar.title("📊 Perfil")

st.sidebar.write(f"⭐ XP: {st.session_state.xp}")
st.sidebar.write(f"🏅 Nivel: {st.session_state.level}")

st.sidebar.divider()

st.sidebar.title("🗺️ Misiones")

for m in st.session_state.unlocked:
    st.sidebar.write(f"✔ {m}")

# =========================================================
# 11. MAPA DE MISIONES
# =========================================================
st.subheader("🌍 Mapa de aprendizaje")

cols = st.columns(len(st.session_state.unlocked))

for i, mission in enumerate(st.session_state.unlocked):

    with cols[i]:

        st.markdown(
            f"""
            <div class="block">
                <h3>{mission}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(f"Entrar a {mission}"):

            msg = start_mission(mission)

            st.session_state.messages = [
                {"role": "assistant", "content": msg}
            ]

            st.rerun()

# =========================================================
# 12. CHAT
# =========================================================
for msg in st.session_state.messages:

    avatar = ICONO_IA if msg["role"] == "assistant" else ICONO_USUARIO

    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# =========================================================
# 13. BOTÓN SIGUIENTE PASO
# =========================================================
if st.session_state.mission:

    if st.button("✅ Completar paso"):

        msg = complete_step()

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": msg
            }
        )

        st.rerun()

# =========================================================
# 14. CHAT LIBRE
# =========================================================
if prompt := st.chat_input("Pregúntale algo a BlendAI..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = ask_ai(prompt)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    st.rerun()
