"""
SIG-LOG: Sistema Integral de Gestion Logistica
Aplicacion principal (Streamlit).

Para ejecutar:
    pip install -r requirements.txt
    streamlit run app.py
"""
import os

import streamlit as st

from database import inicializar
from services import crud
from front.styles import CSS
from front.constants import MODULOS, COLORES_MODULOS
from routes import home, crud as crud_routes, reports, procesamiento, analisis, analisis_ns
from routes.auth import esta_autenticado, render_login, cerrar_sesion, render_usuario_header

if not esta_autenticado():
    render_login()
    st.stop()

st.set_page_config(page_title="SIG-LOG", layout="wide", initial_sidebar_state="expanded")

st.markdown(CSS, unsafe_allow_html=True)

os.makedirs("data", exist_ok=True)
conn = inicializar()
crud.init(conn)

with st.sidebar:
    nombre_usuario, rol_usuario = render_usuario_header()
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="brand-name">SIG-LOG</div>
        <div class="brand-sub">Sistema Integral de Gestion Logistica</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.12); border-radius:10px; padding:0.6rem 0.9rem;
                margin-bottom:0.5rem; display:flex; align-items:center; gap:0.5rem;">
        <div style="width:32px; height:32px; border-radius:50%; background:rgba(255,255,255,0.2);
                    display:flex; align-items:center; justify-content:center; font-size:0.85rem;
                    color:#D1FAE5; font-weight:700;">{nombre_usuario[0].upper()}</div>
        <div>
            <div style="color:#FFFFFF; font-size:0.88rem; font-weight:600;">{nombre_usuario}</div>
            <div style="color:#A7F3D0; font-size:0.75rem;">{rol_usuario}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar sesion", key="btn_logout", use_container_width=True):
        cerrar_sesion()
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    try:
        contadores = {
            "Clientes": len(crud.leer_tabla("clientes")),
            "Vehiculos": len(crud.leer_tabla("vehiculos")),
            "Operadores": len(crud.leer_tabla("operadores")),
            "Rutas": len(crud.leer_tabla("rutas")),
            "Entregas": len(crud.leer_tabla("entregas")),
            "Combustible": len(crud.leer_tabla("combustible")),
            "Mantenimiento": len(crud.leer_tabla("mantenimiento")),
        }
    except Exception:
        contadores = {}

    opciones_con_badges = []
    for m in MODULOS:
        if m in contadores:
            opciones_con_badges.append(f"{m}  [{contadores[m]}]")
        else:
            opciones_con_badges.append(m)

    idx_actual = MODULOS.index(st.session_state.get("modulo", "Inicio"))
    seleccion_texto = st.radio(
        "Navegacion",
        opciones_con_badges,
        index=idx_actual,
        key="modulo_raw",
        label_visibility="collapsed",
    )

    seleccion_limpia = seleccion_texto.split("  [")[0]
    st.session_state["modulo"] = seleccion_limpia
    opcion = seleccion_limpia

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    try:
        total_entregas = len(crud.leer_tabla("entregas"))
        df_ent = crud.leer_tabla("entregas")
        if not df_ent.empty:
            pct_ok = (df_ent["estatus"] == "Entregado").mean() * 100
            indicator_html = f"""
            <div style="padding: 0.75rem 0;">
                <div style="font-size: 0.78rem; color: rgba(255,255,255,0.5); margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Resumen operativo</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-size: 0.82rem; color: #A7F3D0;">Entregas a tiempo</span>
                    <span style="font-size: 0.82rem; color: #FFFFFF; font-weight: 700;">{pct_ok:.0f}%</span>
                </div>
                <div class="progress-bar-container" style="height: 4px; background: rgba(255,255,255,0.15);">
                    <div class="progress-bar-fill" style="width: {pct_ok}%; height: 4px;"></div>
                </div>
            </div>
            """
            st.markdown(indicator_html, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("""
    <div class="sidebar-footer">
        <strong>SIG-LOG</strong> v1.0<br>
        Datos guardados en <code>data/sig_log.db</code>
    </div>
    """, unsafe_allow_html=True)

if opcion == "Inicio":
    home.render()
elif opcion == "Reportes y analisis":
    reports.render()
elif opcion == "Procesamiento":
    procesamiento.render()
elif opcion == "Analisis":
    analisis.render()
elif opcion == "Analisis no supervisado":
    analisis_ns.render()
elif opcion in ("Clientes", "Vehiculos", "Operadores", "Rutas", "Entregas", "Combustible", "Mantenimiento"):
    crud_routes.render(opcion)
