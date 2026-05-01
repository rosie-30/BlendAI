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
}
.stButton>button:hover {
    border: 1px solid #00FFCC;
    color: #00FFCC;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. IA (SEGURA PARA STREAMLIT CLOUD)
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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
# 5. SISTEMA XP / NIVEL
# =========================================================
def add_xp(amount):
    st.session_state.xp += amount
    st.session_state.level = 1 + st.session_state.xp // 50

# =========================================================
# 6. IA TUTOR ULTRA
# =========================================================
def ask_ai(prompt):

    system = f"""
Eres BlendAI, un tutor experto de Blender gamificado.

REGLAS:
- Solo un paso por respuesta
- Formato obligatorio:
  PASO X
  EXPLICACIÓN
  ACCIÓN EN BLENDER
- Nivel usuario: {st.session_state.level}
- Misión: {st.session_state.mission}
- Paso actual: {st.session_state.mission_step}
"""

    messages = [{"role": "system", "content": system},
                {"role": "user", "content": prompt}]

    res = client.chat.completions.create(
        model="llama3-70b-8192"
        messages=messages,
        temperature=0.6
    )

    return res.choices[0].message.content

# =========================================================
# 7. INICIAR MISIÓN
# =========================================================
def start_mission(name):
    st.session_state.mission = name
    st.session_state.mission_step = 0

    return ask_ai(f"Iniciamos misión {name}. Dame el paso 1.")

# =========================================================
# 8. COMPLETAR PASO
# =========================================================
def complete_step():

    mission = st.session_state.mission

    st.session_state.mission_step += 1
    add_xp(10)

    if st.session_state.mission_step >= len(MISSIONS[mission]):
        add_xp(50)

        if mission == "Cubo":
            st.session_state.unlocked.append("Donut")
        if mission == "Donut":
            st.session_state.unlocked.append("Coche")

        st.session_state.mission = None
        st.success("🎉 Misión completada")
        return "Misión completada 🎉"

    return ask_ai("Dame el siguiente paso")

# =========================================================
# 9. UI PRINCIPAL
# =========================================================
st.title("🚀 BlendAI")
st.markdown("### Aprende Blender como un videojuego 🎮")

st.sidebar.title("📊 Progreso")
st.sidebar.write(f"⭐ XP: {st.session_state.xp}")
st.sidebar.write(f"🏅 Nivel: {st.session_state.level}")

st.sidebar.title("🗺️ Misiones desbloqueadas")
for m in st.session_state.unlocked:
    st.sidebar.write("✔ " + m)

# =========================================================
# 10. MAPA DE MISIONES
# =========================================================
st.subheader("🌍 Mapa de misiones")

for mission in st.session_state.unlocked:
    if st.button(f"Entrar a {mission}"):

        msg = start_mission(mission)

        st.session_state.messages = [
            {"role": "assistant", "content": msg}
        ]

# =========================================================
# 11. CHAT
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# 12. BOTÓN ULTRA PROGRESO
# =========================================================
if st.session_state.mission:

    if st.button("✅ Completar paso"):
        msg = complete_step()

        st.session_state.messages.append(
            {"role": "assistant", "content": msg}
        )

        st.rerun()

# =========================================================
# 13. CHAT LIBRE
# =========================================================
if prompt := st.chat_input("Habla con BlendAI..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    response = ask_ai(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    st.rerun()
