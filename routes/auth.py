import streamlit as st
from database import verificar_usuario, crear_usuario


CSS_LOGIN = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(5,150,105,0.2); }
        50% { box-shadow: 0 0 40px rgba(5,150,105,0.4); }
    }
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes ripple {
        0% { transform: scale(0.8); opacity: 1; }
        100% { transform: scale(2.4); opacity: 0; }
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 25%, #047857 50%, #059669 75%, #10B981 100%) !important;
        min-height: 100vh;
    }

    /* Ocultar elementos de Streamlit en login */
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none !important;}

    /* Contenedor principal del login */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
    }

    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3), 0 0 40px rgba(5, 150, 105, 0.15);
        animation: fadeInUp 0.6s ease;
        position: relative;
        overflow: hidden;
    }

    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #059669, #10B981, #34D399, #10B981, #059669);
        animation: shimmer 3s linear infinite;
        background-size: 200% 100%;
    }

    .login-card::after {
        content: '';
        position: absolute;
        top: -50%; right: -30%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(5,150,105,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }

    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }

    .login-logo-icon {
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #059669, #10B981);
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(5, 150, 105, 0.35);
        animation: float 3s ease-in-out infinite;
    }

    .login-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #064E3B;
        margin: 0;
        letter-spacing: -0.03em;
        animation: fadeIn 0.8s ease;
    }

    .login-subtitle {
        color: #6B7280;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        animation: fadeIn 1s ease;
    }

    .login-form {
        position: relative;
        z-index: 1;
        animation: fadeInUp 0.8s ease 0.2s both;
    }

    .login-input-group {
        margin-bottom: 1.25rem;
        animation: slideInLeft 0.5s ease 0.3s both;
    }

    .login-input-group:nth-child(2) {
        animation: slideInRight 0.5s ease 0.4s both;
    }

    .login-input-label {
        display: block;
        font-size: 0.85rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
        letter-spacing: 0.02em;
    }

    .login-input {
        width: 100%;
        padding: 0.85rem 1.1rem;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        font-size: 0.95rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: #F9FAFB;
        box-sizing: border-box;
    }

    .login-input:focus {
        outline: none;
        border-color: #059669;
        box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.12);
        background: #FFFFFF;
    }

    .login-input::placeholder {
        color: #9CA3AF;
    }

    .login-btn {
        width: 100%;
        padding: 0.9rem;
        background: linear-gradient(135deg, #059669, #10B981);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.35);
        margin-top: 0.5rem;
        animation: bounceIn 0.6s ease 0.5s both;
        letter-spacing: 0.02em;
    }

    .login-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(5, 150, 105, 0.45);
        background: linear-gradient(135deg, #047857, #059669);
    }

    .login-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(5, 150, 105, 0.3);
    }

    .login-divider {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        animation: fadeIn 1s ease 0.6s both;
    }

    .login-divider::before,
    .login-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
    }

    .login-divider span {
        padding: 0 1rem;
        color: #9CA3AF;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .login-footer {
        text-align: center;
        margin-top: 1.5rem;
        animation: fadeIn 1s ease 0.7s both;
    }

    .login-footer p {
        color: #9CA3AF;
        font-size: 0.82rem;
        margin: 0;
        line-height: 1.6;
    }

    .login-footer strong {
        color: #059669;
    }

    .login-error {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1.25rem;
        color: #DC2626;
        font-size: 0.88rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: fadeInUp 0.3s ease;
    }

    .login-error::before {
        content: '!';
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px; height: 22px;
        background: #FEE2E2;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }

    .login-success {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1.25rem;
        color: #065F46;
        font-size: 0.88rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: fadeInUp 0.3s ease;
    }

    .login-success::before {
        content: '';
        display: inline-block;
        width: 22px; height: 22px;
        background: #D1FAE5;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* Floating particles */
    .particle {
        position: fixed;
        width: 6px; height: 6px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    .particle:nth-child(1) { top: 10%; left: 15%; animation-delay: 0s; }
    .particle:nth-child(2) { top: 20%; right: 20%; animation-delay: 1s; width: 8px; height: 8px; }
    .particle:nth-child(3) { bottom: 25%; left: 10%; animation-delay: 2s; width: 4px; height: 4px; }
    .particle:nth-child(4) { bottom: 15%; right: 15%; animation-delay: 3s; }
    .particle:nth-child(5) { top: 50%; left: 5%; animation-delay: 4s; width: 10px; height: 10px; }
</style>
"""


def esta_autenticado():
    return st.session_state.get("autenticado", False)


def cerrar_sesion():
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario", None)
    st.session_state.pop("modulo", None)


def render_login():
    st.set_page_config(page_title="SIG-LOG - Login", layout="centered",
                       initial_sidebar_state="collapsed")
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)

    st.markdown("""
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <div class="login-logo">
                <div class="login-logo-icon">S</div>
                <h1 class="login-title">SIG-LOG</h1>
                <p class="login-subtitle">Sistema Integral de Gestion Logistica</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 1.5, 1])
    with col_centro:
        modo = st.session_state.get("auth_modo", "login")

        if "login_error" in st.session_state and st.session_state["login_error"]:
            st.markdown(f"""
            <div class="login-error">{st.session_state["login_error"]}</div>
            """, unsafe_allow_html=True)

        if "login_exito" in st.session_state and st.session_state["login_exito"]:
            st.markdown(f"""
            <div class="login-success">{st.session_state["login_exito"]}</div>
            """, unsafe_allow_html=True)

        if modo == "login":
            with st.form("login_form", clear_on_submit=False):
                st.markdown("""
                <div class="login-form">
                    <div class="login-input-group">
                        <label class="login-input-label">Usuario</label>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario",
                                        label_visibility="collapsed")

                st.markdown("""
                <div class="login-form">
                    <div class="login-input-group">
                        <label class="login-input-label">Contrasena</label>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                password = st.text_input("Contrasena", type="password",
                                         placeholder="Ingresa tu contrasena",
                                         label_visibility="collapsed")

                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                enviado = st.form_submit_button("Iniciar sesion", type="primary",
                                                use_container_width=True)

                if enviado:
                    if not usuario or not password:
                        st.session_state["login_error"] = "Ingresa tu usuario y contrasena."
                        st.rerun()
                    else:
                        user = verificar_usuario(usuario, password)
                        if user:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario"] = user
                            st.session_state["login_error"] = None
                            st.rerun()
                        else:
                            st.session_state["login_error"] = ("Usuario o contrasena "
                                                               "incorrectos. Intenta de nuevo.")
                            st.rerun()

            if st.button("Crear cuenta nueva", use_container_width=True):
                st.session_state["auth_modo"] = "registro"
                st.session_state["login_error"] = None
                st.session_state["login_exito"] = None
                st.rerun()

        else:
            with st.form("registro_form", clear_on_submit=False):
                st.markdown("**Crear cuenta nueva**")
                nombre = st.text_input("Nombre completo", placeholder="Tu nombre")
                usuario_r = st.text_input("Usuario", placeholder="Elige un usuario",
                                          key="reg_user")
                password_r = st.text_input("Contrasena", type="password",
                                           placeholder="Elige una contrasena",
                                           key="reg_pass")
                password_r2 = st.text_input("Confirmar contrasena", type="password",
                                            placeholder="Repite la contrasena",
                                            key="reg_pass2")

                enviado_r = st.form_submit_button("Crear cuenta", type="primary",
                                                   use_container_width=True)

                if enviado_r:
                    if not nombre or not usuario_r or not password_r:
                        st.session_state["login_error"] = "Todos los campos son obligatorios."
                        st.rerun()
                    elif len(password_r) < 4:
                        st.session_state["login_error"] = "La contrasena debe tener al menos 4 caracteres."
                        st.rerun()
                    elif password_r != password_r2:
                        st.session_state["login_error"] = "Las contrasenas no coinciden."
                        st.rerun()
                    else:
                        ok = crear_usuario(usuario_r, password_r, nombre)
                        if ok:
                            st.session_state["login_exito"] = "Cuenta creada. Ahora puedes iniciar sesion."
                            st.session_state["auth_modo"] = "login"
                            st.session_state["login_error"] = None
                            st.rerun()
                        else:
                            st.session_state["login_error"] = "Ese usuario ya existe. Elige otro."
                            st.rerun()

            if st.button("Volver al login", use_container_width=True):
                st.session_state["auth_modo"] = "login"
                st.session_state["login_error"] = None
                st.session_state["login_exito"] = None
                st.rerun()

        st.markdown("""
        <div class="login-footer">
            <p>
                <strong>Admin:</strong> admin / admin123<br>
                <strong>Operador:</strong> operador / operador123
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_usuario_header():
    user = st.session_state.get("usuario", {})
    nombre = user.get("nombre", "Usuario")
    rol = user.get("rol", "operador")
    emoji_rol = "Administrador" if rol == "admin" else "Operador"
    return nombre, emoji_rol
