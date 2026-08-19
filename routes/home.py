import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from services import crud
from front.constants import MODULOS, DESCRIPCIONES, COLORES_MODULOS


def navegar_a(modulo):
    st.session_state["modulo"] = modulo


def render():
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">Sistema de gestion logistica v1.0</div>
        <h1>Bienvenido a SIG-LOG</h1>
        <p>Administra clientes, vehiculos, operadores, rutas, entregas, combustible y mantenimiento.
        Consulta reportes y analisis para tomar mejores decisiones operativas.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    df_clientes = crud.leer_tabla("clientes")
    df_vehiculos = crud.leer_tabla("vehiculos")
    df_operadores = crud.leer_tabla("operadores")
    df_entregas = crud.leer_tabla("entregas")
    df_rutas = crud.leer_tabla("rutas")
    df_combustible = crud.leer_tabla("combustible")
    df_mantenimiento = crud.leer_tabla("mantenimiento")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes", len(df_clientes))
    c2.metric("Vehiculos", len(df_vehiculos))
    c3.metric("Operadores", len(df_operadores))
    c4.metric("Entregas", len(df_entregas))

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    if not df_entregas.empty:
        total = len(df_entregas)
        entregadas = (df_entregas["estatus"] == "Entregado").sum()
        retrasadas = (df_entregas["estatus"] == "Retrasado").sum()
        canceladas = (df_entregas["estatus"] == "Cancelado").sum()

        pct_entregadas = entregadas / total * 100
        pct_retrasadas = retrasadas / total * 100

        df_entregas["_fecha"] = pd.to_datetime(df_entregas["fecha"], errors="coerce")
        df_recientes = df_entregas.dropna(subset=["_fecha"]).nlargest(7, "_fecha")

        if not df_recientes.empty:
            st.markdown("### Indicadores de la ultima semana")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Entregas esta semana", len(df_recientes))
            k2.metric("A tiempo", f"{(df_recientes['estatus']=='Entregado').mean()*100:.0f}%")
            k3.metric("Retrasadas", f"{(df_recientes['estatus']=='Retrasado').sum()}")
            k4.metric("Canceladas", f"{(df_recientes['estatus']=='Cancelado').sum()}")
            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go

            st.markdown("### Actividad operativa reciente")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                df_entregas_validas = df_entregas.dropna(subset=["_fecha"]).copy()
                if not df_entregas_validas.empty:
                    tendencia = df_entregas_validas.set_index("_fecha").resample("D").size()
                    tendencia = tendencia[tendencia > 0]

                    fig_tend = go.Figure(go.Scatter(
                        x=tendencia.index,
                        y=tendencia.values,
                        mode="lines+markers",
                        line=dict(color="#059669", width=2.5),
                        marker=dict(size=5, color="#047857"),
                        fill="tozeroy",
                        fillcolor="rgba(5,150,105,0.1)",
                        hovertemplate="%{x|%d/%m/%Y}<br>Entregas: %{y}<extra></extra>",
                    ))
                    fig_tend.update_layout(
                        title={"text": "Tendencia diaria de entregas", "x": 0.5,
                               "font": {"size": 14, "color": "#064E3B"}},
                        template="plotly_white",
                        height=320,
                        margin=dict(l=50, r=20, t=50, b=40),
                        xaxis_title="",
                        yaxis_title="Entregas",
                        hoverlabel={"bgcolor": "#064E3B", "font": {"color": "white"}},
                    )
                    fig_tend.update_xaxes(showgrid=False)
                    fig_tend.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
                    st.plotly_chart(fig_tend, width="stretch",
                                    config={"displayModeBar": False})

            with col_chart2:
                estatus_counts = df_entregas["estatus"].value_counts()
                colores_map = {"Entregado": "#059669", "Retrasado": "#EF4444", "Cancelado": "#9CA3AF"}
                fig_pie = go.Figure(go.Pie(
                    labels=estatus_counts.index.tolist(),
                    values=estatus_counts.values.tolist(),
                    marker=dict(
                        colors=[colores_map.get(e, "#6B7280") for e in estatus_counts.index],
                        line=dict(color="white", width=2),
                    ),
                    textinfo="label+percent",
                    hole=0.45,
                    hovertemplate="%{label}: %{value} entregas (%{percent})<extra></extra>",
                ))
                fig_pie.update_layout(
                    title={"text": "Distribucion por estatus", "x": 0.5,
                           "font": {"size": 14, "color": "#064E3B"}},
                    template="plotly_white",
                    height=320,
                    margin=dict(l=20, r=20, t=50, b=20),
                    showlegend=True,
                    legend={"orientation": "h", "y": -0.05, "x": 0.5, "xanchor": "center",
                            "font": {"size": 11}},
                    hoverlabel={"bgcolor": "#064E3B", "font": {"color": "white"}},
                )
                st.plotly_chart(fig_pie, width="stretch",
                                config={"displayModeBar": False})

            if not df_combustible.empty:
                col_chart3, col_chart4 = st.columns(2)

                with col_chart3:
                    df_comb = df_combustible.copy()
                    df_comb["_fecha"] = pd.to_datetime(df_comb["fecha"], errors="coerce")
                    df_comb = df_comb.dropna(subset=["_fecha"])
                    if not df_comb.empty:
                        cost_x_dia = df_comb.set_index("_fecha")["costo"].resample("D").sum()
                        cost_x_dia = cost_x_dia[cost_x_dia > 0]
                        if not cost_x_dia.empty:
                            fig_cost = go.Figure(go.Scatter(
                                x=cost_x_dia.index,
                                y=cost_x_dia.values,
                                mode="lines",
                                line=dict(color="#D97706", width=2),
                                fill="tozeroy",
                                fillcolor="rgba(217,119,6,0.1)",
                                hovertemplate="%{x|%d/%m/%Y}<br>Costo: $%{y:,.0f}<extra></extra>",
                            ))
                            fig_cost.update_layout(
                                title={"text": "Costo diario de combustible", "x": 0.5,
                                       "font": {"size": 14, "color": "#064E3B"}},
                                template="plotly_white",
                                height=320,
                                margin=dict(l=60, r=20, t=50, b=40),
                                yaxis_title="Costo ($)",
                                hoverlabel={"bgcolor": "#064E3B", "font": {"color": "white"}},
                            )
                            fig_cost.update_xaxes(showgrid=False)
                            fig_cost.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
                            st.plotly_chart(fig_cost, width="stretch",
                                            config={"displayModeBar": False})

                with col_chart4:
                    if not df_mantenimiento.empty:
                        df_mant = df_mantenimiento.copy()
                        df_mant["_fecha"] = pd.to_datetime(df_mant["fecha"], errors="coerce")
                        df_mant = df_mant.dropna(subset=["_fecha"])
                        if not df_mant.empty:
                            tipo_counts = df_mant["tipo"].value_counts()
                            fig_mant = go.Figure(go.Bar(
                                x=tipo_counts.index.tolist(),
                                y=tipo_counts.values.tolist(),
                                marker_color=["#059669", "#EF4444"][:len(tipo_counts)],
                                text=tipo_counts.values.tolist(),
                                textposition="outside",
                                hovertemplate="%{x}: %{y} servicios<extra></extra>",
                            ))
                            fig_mant.update_layout(
                                title={"text": "Mantenimiento por tipo", "x": 0.5,
                                       "font": {"size": 14, "color": "#064E3B"}},
                                template="plotly_white",
                                height=320,
                                margin=dict(l=50, r=20, t=50, b=40),
                                yaxis_title="Servicios",
                                hoverlabel={"bgcolor": "#064E3B", "font": {"color": "white"}},
                            )
                            fig_mant.update_xaxes(showgrid=False)
                            fig_mant.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
                            st.plotly_chart(fig_mant, width="stretch",
                                            config={"displayModeBar": False})

        except ImportError:
            pass

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    st.markdown("### Acceso rapido a modulos")

    mods = [m for m in MODULOS if m != "Inicio"]
    for i in range(0, len(mods), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(mods):
                m = mods[i + j]
                color_principal, color_fondo = COLORES_MODULOS.get(m, ("#6B7280", "#F3F4F6"))
                conteo = ""
                if m in contadores():
                    conteo = f"""<span style="display:inline-block; background:{color_fondo}; color:{color_principal};
                    font-size:0.72rem; font-weight:700; padding:0.15rem 0.55rem; border-radius:999px;
                    margin-top:0.4rem;">{contadores()[m]} registros</span>"""
                with cols[j]:
                    st.markdown(f"""
                    <div class="card" style="border-top: 3px solid {color_principal};">
                        <div class="card-module">
                            <div class="card-title" style="color: {color_principal};">{m}</div>
                            <div class="card-text">{DESCRIPCIONES[m]}</div>
                            {conteo}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Entrar a {m}", key=f"go_{m}", width="stretch",
                                 on_click=navegar_a, args=(m,)):
                        pass

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    st.markdown("### Como usar el sistema")

    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">Guia rapida de uso</div>
        <ol class="pasos">
            <li>Elige un <b>modulo</b> en el menu lateral izquierdo.</li>
            <li>Veras una <b>tabla</b> con los registros actuales y un formulario para agregar.</li>
            <li>Completa el formulario y presiona <b>Guardar registro</b>.</li>
            <li>Para corregir o eliminar, selecciona el registro en el panel derecho y
                presiona <b>Actualizar</b> o <b>Eliminar</b>.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


def contadores():
    try:
        return {
            "Clientes": len(crud.leer_tabla("clientes")),
            "Vehiculos": len(crud.leer_tabla("vehiculos")),
            "Operadores": len(crud.leer_tabla("operadores")),
            "Rutas": len(crud.leer_tabla("rutas")),
            "Entregas": len(crud.leer_tabla("entregas")),
            "Combustible": len(crud.leer_tabla("combustible")),
            "Mantenimiento": len(crud.leer_tabla("mantenimiento")),
        }
    except Exception:
        return {}
