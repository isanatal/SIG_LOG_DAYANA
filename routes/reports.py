from datetime import date

import pandas as pd
import streamlit as st

from services import crud


def render():
    st.markdown("<div class='modulo-header'><h1>Reportes y analisis</h1>"
                "<p>Graficas y modelos que te ayudan a entender mejor la operacion logistica.</p></div>",
                unsafe_allow_html=True)

    import plotly.graph_objects as go

    entregas = crud.leer_tabla("entregas")
    rutas = crud.leer_tabla("rutas")
    vehiculos = crud.leer_tabla("vehiculos")
    operadores = crud.leer_tabla("operadores")
    clientes = crud.leer_tabla("clientes")
    combustible = crud.leer_tabla("combustible")
    mantenimiento = crud.leer_tabla("mantenimiento")

    total_registros = (len(entregas) + len(rutas) + len(vehiculos) +
                       len(operadores) + len(clientes))
    st.markdown(f"""
    <div style="display:flex; gap:1rem; margin-bottom:1rem; flex-wrap:wrap;">
        <div style="background:#ECFDF5; border-radius:12px; padding:0.6rem 1.2rem;
                    border:1px solid #A7F3D0; font-size:0.85rem;">
            <span style="color:#6B7280;">Base de datos:</span>
            <strong style="color:#064E3B;">{total_registros} registros</strong>
        </div>
        <div style="background:#EFF6FF; border-radius:12px; padding:0.6rem 1.2rem;
                    border:1px solid #BFDBFE; font-size:0.85rem;">
            <span style="color:#6B7280;">Modelos:</span>
            <strong style="color:#1E40AF;">Regresion, Clasificacion, Clustering</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    PALETA_MODELOS = ["#059669", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6",
                       "#14B8A6", "#F97316", "#6B7280", "#DB2777", "#0EA5E9"]

    def estilo_modelo(fig, titulo, subtitulo, xlabel="", ylabel="", altura=440):
        """Aplica titulo, subtitulo y etiquetas de ejes a una figura Plotly,
        con el mismo lenguaje visual usado en Reportes descriptivos."""
        fig.update_layout(
            title={"text": titulo, "x": 0.5, "xanchor": "center",
                   "font": {"size": 15, "color": "#064E3B", "family": "Inter, Segoe UI, sans-serif"}},
            annotations=[{"text": subtitulo, "xref": "paper", "yref": "paper",
                          "x": 0.5, "y": -0.20, "showarrow": False, "xanchor": "center",
                          "font": {"size": 11, "color": "#6B7280", "family": "Inter, Segoe UI, sans-serif"}}],
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            template="plotly_white",
            height=altura,
            margin=dict(l=70, r=30, t=60, b=100),
            hoverlabel={"bgcolor": "#064E3B", "bordercolor": "#064E3B",
                        "font": {"color": "white", "family": "Inter, Segoe UI, sans-serif"}},
        )
        fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
        fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
        return fig

    def mostrar_modelo_chart(fig, conclusion):
        """Renderiza una figura Plotly de la seccion de modelos junto con su conclusion."""
        st.plotly_chart(fig, width="stretch",
                        config={"displayModeBar": True,
                                "toImageButtonOptions": {"format": "png", "scale": 2}})
        st.markdown(f"**Conclusion:** {conclusion}")

    def grafica_dispersion_modelo(x, y, titulo, subtitulo, xlabel, ylabel, conclusion,
                                  color_serie=None, nombre_color="Grupo", linea_tendencia=None):
        """Dispersion interactiva reutilizada en regresion y clustering. Si se pasa
        color_serie, cada valor distinto se dibuja como una serie/color independiente
        (por ejemplo, cada cluster)."""
        fig = go.Figure()
        if color_serie is not None:
            for grupo in sorted(pd.Series(color_serie).unique()):
                mascara = color_serie == grupo
                fig.add_trace(go.Scatter(
                    x=pd.Series(x)[mascara], y=pd.Series(y)[mascara], mode="markers",
                    name=f"{nombre_color} {grupo}",
                    marker=dict(size=9, color=PALETA_MODELOS[int(grupo) % len(PALETA_MODELOS)],
                               opacity=0.8, line=dict(width=1, color="white")),
                    hovertemplate=f"{xlabel}: %{{x:.2f}}<br>{ylabel}: %{{y:.2f}}<extra></extra>",
                ))
            fig.update_layout(legend={"title": nombre_color, "orientation": "h", "y": 1.05,
                                      "x": 0, "xanchor": "left", "font": {"size": 11}})
        else:
            fig.add_trace(go.Scatter(
                x=x, y=y, mode="markers", name="Datos",
                marker=dict(size=8, color="#059669", opacity=0.7, line=dict(width=1, color="white")),
                hovertemplate=f"{xlabel}: %{{x:.2f}}<br>{ylabel}: %{{y:.2f}}<extra></extra>",
            ))
        if linea_tendencia is not None:
            lx, ly = linea_tendencia
            fig.add_trace(go.Scatter(
                x=lx, y=ly, mode="lines", name="Prediccion ideal",
                line=dict(color="#DC2626", width=2, dash="dash"),
                hoverinfo="skip",
            ))
        estilo_modelo(fig, titulo, subtitulo, xlabel, ylabel)
        mostrar_modelo_chart(fig, conclusion)

    def grafica_linea_modelo(x, y, titulo, subtitulo, xlabel, ylabel, conclusion, color="#059669"):
        fig = go.Figure(go.Scatter(
            x=list(x), y=list(y), mode="lines+markers",
            line=dict(color=color, width=2.5), marker=dict(size=8, color=color),
            hovertemplate=f"{xlabel}: %{{x}}<br>{ylabel}: %{{y:.3f}}<extra></extra>",
        ))
        estilo_modelo(fig, titulo, subtitulo, xlabel, ylabel, altura=380)
        mostrar_modelo_chart(fig, conclusion)

    def matriz_confusion_modelo(cm, titulo, subtitulo, conclusion, etiquetas=("A tiempo", "Tarde")):
        texto = [[str(v) for v in fila] for fila in cm]
        fig = go.Figure(go.Heatmap(
            z=cm, x=list(etiquetas), y=list(etiquetas),
            colorscale=[[0, "#ECFDF5"], [1, "#059669"]],
            text=texto, texttemplate="%{text}", textfont=dict(size=18, color="#064E3B"),
            hovertemplate="Real: %{y}<br>Prediccion: %{x}<br>Casos: %{z}<extra></extra>",
            colorbar=dict(title="Casos"),
        ))
        fig.update_yaxes(autorange="reversed")
        estilo_modelo(fig, titulo, subtitulo, "Prediccion del modelo", "Valor real", altura=380)
        mostrar_modelo_chart(fig, conclusion)

    tabs = st.tabs([
        "0. Metodologia (CRISP-DM / KDD)",
        "1. ETL - Preparacion de datos",
        "2. Reportes descriptivos",
        "3. Regresion (supervisado)",
        "4. Clasificacion (supervisado)",
        "5. Clustering (no supervisado)",
    ])

    # ---------------- Unidad I: Metodologia ----------------
    with tabs[0]:
        st.subheader("Las 5 unidades del curso aplicadas en SIG-LOG")
        st.markdown("""
| Unidad | Tema | Evidencia en SIG-LOG |
|---|---|---|
| 1 | Base de datos y SQL | 7 tablas con llaves foraneas, esquema de estrella, operaciones CRUD completas |
| 2 | ETL / Preparacion de datos | Limpieza de nulos, calculo de columnas derivadas (`retraso_min`, `retrasado`) |
| 3 | Reportes descriptivos | 12+ graficas interactivas con Plotly, filtros por periodo, KPIs |
| 4 | Aprendizaje supervisado | Regresion lineal (simple y multiple) + Clasificacion logistica con matriz de confusion |
| 5 | Aprendizaje no supervisado | Clustering K-means con PCA, metodo del codo e indice de silueta |
        """)

        st.divider()
        st.subheader("Metodologias aplicadas: KDD y CRISP-DM")
        st.markdown("""
        Este proyecto sigue el proceso de **KDD (Knowledge Discovery in
        Databases)**, apoyado en el ciclo de **CRISP-DM**:

        | Fase CRISP-DM | Que se hizo en SIG-LOG |
        |---|---|
        | Comprension del negocio | Caso de estudio: empresa de transporte con datos dispersos (ver planteamiento del problema) |
        | Comprension de los datos | Modulos CRUD: clientes, vehiculos, operadores, rutas, entregas, combustible, mantenimiento |
        | Preparacion de los datos | Pestana "ETL - Preparacion de datos": limpieza de nulos, calculo de columnas derivadas |
        | Modelado | Pestanas de Regresion, Clasificacion y Clustering |
        | Evaluacion | Metricas de cada modelo (MAE, RMSE, R2, exactitud, matriz de confusion, silueta) |
        | Despliegue | La aplicacion Streamlit misma: reportes y predicciones usables por el usuario |

        **KDD** es el proceso completo (seleccion, preprocesamiento,
        transformacion, mineria de datos e interpretacion) del que CRISP-DM
        es una metodologia concreta y guiada por negocio.
        """)

        st.subheader("ETL vs ELT en este sistema")
        st.markdown("""
        - **ETL (Extract, Transform, Load)** \u2014 es lo que usa este proyecto:
          1. **Extract**: se extraen los datos de las tablas SQLite (`entregas`, `rutas`, etc.) con `pandas.read_sql_query`.
          2. **Transform**: se limpian nulos, se calculan columnas derivadas (`retraso_min`, `retrasado`) y se unen tablas (`merge`).
          3. **Load**: los datos ya transformados se "cargan" directamente a los modelos de scikit-learn para entrenarlos.
        - **ELT (Extract, Load, Transform)** seria cargar los datos crudos primero a un almacen grande (p. ej. un data warehouse) y transformarlos despues, dentro de ese almacen \u2014 util con grandes volumenes de datos, que no es el caso de este proyecto academico.
        """)

        st.subheader("Modelo de Data Warehouse (esquema de estrella)")
        st.markdown("""
        Los datos de SIG-LOG tambien pueden entenderse como un **almacen de
        datos (data warehouse)** con estructura de **esquema de estrella**:
        una tabla central de **hechos** rodeada de tablas de **dimensiones**
        que la describen.

        | Tabla | Rol en el esquema de estrella |
        |---|---|
        | `entregas` | **Tabla de hechos**: registra cada entrega con sus metricas (minutos estimados y reales) y sus llaves foraneas |
        | `clientes` | **Dimension**: quien recibe la entrega |
        | `vehiculos` | **Dimension**: que unidad la realiza |
        | `operadores` | **Dimension**: quien la conduce |
        | `rutas` | **Dimension**: por donde viaja (origen, destino, distancia) |
        """)

        st.markdown("**Esquema de estrella con los datos reales (en vivo):**")
        st.caption("Los datos se leen directamente de la base en cada actualizacion "
                   "(se refrescan solos cada 10 segundos y con cualquier clic). Si agregas "
                   "o modificas clientes, vehiculos, operadores, rutas o entregas, aqui "
                   "aparece el cambio de inmediato.")

        @st.fragment(run_every="10s")
        def vista_esquema():
            clientes_act = crud.leer_tabla("clientes")
            vehiculos_act = crud.leer_tabla("vehiculos")
            operadores_act = crud.leer_tabla("operadores")
            rutas_act = crud.leer_tabla("rutas")
            entregas_act = crud.leer_tabla("entregas")

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("ENTREGAS \u00b7 hechos", len(entregas_act))
            m2.metric("CLIENTES", len(clientes_act))
            m3.metric("VEHICULOS", len(vehiculos_act))
            m4.metric("OPERADORES", len(operadores_act))
            m5.metric("RUTAS", len(rutas_act))

            st.divider()

            if entregas_act.empty:
                st.info("Aun no hay entregas registradas; agrega una en el modulo Entregas "
                        "para ver aqui como se une la tabla de hechos con sus dimensiones.")
            else:
                estrella = entregas_act.merge(
                    clientes_act, left_on="cliente_id", right_on="id", suffixes=("", "_cli"))
                estrella = estrella.merge(
                    vehiculos_act, left_on="vehiculo_id", right_on="id", suffixes=("", "_veh"))
                estrella = estrella.merge(
                    operadores_act, left_on="operador_id", right_on="id", suffixes=("", "_op"))
                estrella = estrella.merge(
                    rutas_act, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))

                estrella["cliente"] = estrella["nombre"]
                estrella["vehiculo"] = estrella["placas"] + " \u00b7 " + estrella["modelo"]
                estrella["operador"] = estrella["nombre_op"]
                estrella["ruta"] = estrella["origen"] + " \u2192 " + estrella["destino"]

                st.markdown("**Tabla de hechos unida a sus 4 dimensiones** \u2014 cada fila es una "
                            "entrega real con el detalle de su cliente, vehiculo, operador y ruta:")
                st.dataframe(estrella[["fecha", "cliente", "vehiculo", "operador", "ruta",
                                       "minutos_estimados", "minutos_reales", "estatus"]].tail(15),
                             width="stretch")

            st.divider()
            st.markdown("**Registros reales de cada dimension:**")
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**clientes (dimension)**")
                st.dataframe(clientes_act, width="stretch", height=220)
                st.markdown("**operadores (dimension)**")
                st.dataframe(operadores_act, width="stretch", height=220)
            with colB:
                st.markdown("**vehiculos (dimension)**")
                st.dataframe(vehiculos_act, width="stretch", height=220)
                st.markdown("**rutas (dimension)**")
                st.dataframe(rutas_act, width="stretch", height=220)

        vista_esquema()

        st.markdown("""
        **Por que esquema de estrella?**
        - **Hechos** (tabla central): los eventos medibles del negocio; en
          SIG-LOG cada fila de `entregas` es una entrega real con sus tiempos.
        - **Dimensiones** (alrededor): el contexto descriptivo que permite
          filtrar y agrupar los reportes (por cliente, vehiculo, operador o ruta).
        - **Ventajas**: consultas de reportes mas rapidas y faciles de
          entender; cada entrega se relaciona con una sola fila por dimension.
        """)

    # ---------------- Unidad II: ETL / Preparacion de datos ----------------
    with tabs[1]:
        st.subheader("Extraccion, transformacion y limpieza de datos")
        st.caption("En esta pestana se muestra como se preparan los datos antes de analizarlos.")

        st.markdown("**Extract** \u2014 datos crudos extraidos de la tabla `entregas`:")
        st.dataframe(entregas.head(5), width="stretch")

        st.markdown("**Transform** \u2014 valores nulos detectados antes de limpiar:")
        st.dataframe(entregas.isnull().sum().rename("valores nulos"))

        entregas_limpio = entregas.dropna(subset=["minutos_reales"]).copy()
        entregas_limpio["retraso_min"] = entregas_limpio["minutos_reales"] - entregas_limpio["minutos_estimados"]
        entregas_limpio["retrasado"] = (entregas_limpio["retraso_min"] > 15).astype(int)
        st.caption("Se eliminaron las entregas canceladas (sin minutos_reales) y se "
                   "calcularon las columnas derivadas `retraso_min` y `retrasado`.")

        st.markdown("**Load** \u2014 datos ya listos para modelar:")
        st.dataframe(entregas_limpio.head(10), width="stretch")

    # ---------------- Reportes descriptivos ----------------
    with tabs[2]:
        st.subheader("Reportes e indicadores")
        st.caption("Graficas interactivas: pasa el cursor sobre cualquier punto o barra para "
                   "ver el valor exacto y usa la lupa para acercarte. Filtra por periodo de "
                   "fechas y descarga un reporte con la fecha, dia y hora de generacion.")

        st.markdown("**Preguntas del caso de estudio que responde esta seccion:**")
        st.markdown("""
| Pregunta del caso de estudio | Reporte / Grafica |
|---|---|
| Que rutas son mas utilizadas? | Entregas por ruta (barras/pastel configurable) |
| Que vehiculos generan mayores costos? | Costo total por vehiculo: combustible + mantenimiento |
| Que operadores realizan mas entregas? | Entregas por operador (barras/pastel configurable) |
| Que rutas presentan mayores retrasos? | Retraso promedio por ruta (barras) |
| Que vehiculos consumen mas combustible? | Costo de combustible por vehiculo (barras) |
| Cuales son las causas principales de retraso? | Correlacion entre variables + Dispersion distancia vs tiempo |
| Que vehiculos requieren mantenimiento? | Vehiculos con estatus distinto a Activo |
| Horarios de mayor saturacion? | Mapa de calor: dia de semana x hora de salida |
        """)

        entregas["_fecha"] = pd.to_datetime(entregas["fecha"], errors="coerce")
        fechas_validas = entregas["_fecha"].dropna()
        if fechas_validas.empty:
            fecha_min = fecha_max = date.today()
        else:
            fecha_min = fechas_validas.min().date()
            fecha_max = fechas_validas.max().date()

        c_f1, c_f2 = st.columns(2)
        f1 = c_f1.date_input("Fecha de inicio del periodo",
                             value=fecha_min, min_value=fecha_min, max_value=fecha_max)
        f2 = c_f2.date_input("Fecha de fin del periodo",
                             value=fecha_max, min_value=fecha_min, max_value=fecha_max)

        if f1 > f2:
            st.error("La fecha de inicio no puede ser posterior a la de fin; se invirtieron.")
            f1, f2 = f2, f1

        ts1, ts2 = pd.Timestamp(f1), pd.Timestamp(f2)
        entregas_f = entregas[entregas["_fecha"].between(ts1, ts2)].copy()
        combustible_f = (combustible[pd.to_datetime(combustible["fecha"], errors="coerce")
                                     .between(ts1, ts2)].copy()
                         if not combustible.empty else combustible.copy())
        mantenimiento_f = (mantenimiento[pd.to_datetime(mantenimiento["fecha"], errors="coerce")
                                         .between(ts1, ts2)].copy()
                           if not mantenimiento.empty else mantenimiento.copy())

        n_ent = len(entregas_f)
        est = entregas_f["estatus"].value_counts()
        pct_entregadas = est.get("Entregado", 0) / n_ent * 100 if n_ent else 0
        pct_retrasadas = est.get("Retrasado", 0) / n_ent * 100 if n_ent else 0
        pct_canceladas = est.get("Cancelado", 0) / n_ent * 100 if n_ent else 0
        reales_prom = entregas_f["minutos_reales"].dropna().mean()
        tiempo_prom = reales_prom if pd.notna(reales_prom) else 0

        sub_periodo = f"Periodo: {f1} al {f2} \u00b7 {n_ent} entregas"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F0FDF4, #ECFDF5); border-radius:16px;
                    padding:1rem 1.5rem; margin-bottom:1rem; border:1px solid #BBF7D0;">
            <div style="font-size:0.78rem; color:#6B7280; text-transform:uppercase;
                        letter-spacing:0.05em; font-weight:600; margin-bottom:0.75rem;">
                Indicadores del periodo {f1} al {f2}
            </div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Entregas", n_ent)
        m2.metric("Entregadas", f"{pct_entregadas:.1f}%")
        m3.metric("Retrasadas", f"{pct_retrasadas:.1f}%")
        m4.metric("Canceladas", f"{pct_canceladas:.1f}%")
        m5.metric("Tiempo promedio", f"{tiempo_prom:.0f} min")
        st.divider()

        # ------------------------------------------------------------------
        # Coleccion de graficas interactivas (Plotly)
        # ------------------------------------------------------------------
        import plotly.graph_objects as go

        reportes = []
        PALETA = ["#059669", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6",
                  "#14B8A6", "#F97316", "#6B7280", "#DB2777", "#0EA5E9"]

        def anadir_reporte(fig, titulo, subtitulo, conclusion):
            reportes.append({"titulo": titulo, "subtitulo": subtitulo,
                             "conclusion": conclusion, "fig": fig})

        def estilo_fig(fig, titulo, subtitulo, xlabel="", ylabel=""):
            fig.update_layout(
                title={"text": titulo, "x": 0.5, "xanchor": "center",
                       "font": {"size": 15, "color": "#064E3B", "family": "Inter, Segoe UI, sans-serif"}},
                annotations=[{"text": subtitulo, "xref": "paper", "yref": "paper",
                              "x": 0.5, "y": -0.18, "showarrow": False, "xanchor": "center",
                              "font": {"size": 11, "color": "#6B7280", "family": "Inter, Segoe UI, sans-serif"}}],
                xaxis_title=xlabel,
                yaxis_title=ylabel,
                template="plotly_white",
                height=450,
                margin=dict(l=70, r=30, t=60, b=95),
                hoverlabel={"bgcolor": "#064E3B", "bordercolor": "#064E3B",
                            "font": {"color": "white", "family": "Inter, Segoe UI, sans-serif"}},
            )
            fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
            fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
            return fig

        def titulo_pie(fig, titulo, subtitulo):
            fig.update_layout(
                title={"text": titulo, "x": 0.5, "xanchor": "center",
                       "font": {"size": 15, "color": "#064E3B", "family": "Inter, Segoe UI, sans-serif"}},
                annotations=[{"text": subtitulo, "xref": "paper", "yref": "paper",
                              "x": 0.5, "y": -0.16, "showarrow": False, "xanchor": "center",
                              "font": {"size": 11, "color": "#6B7280", "family": "Inter, Segoe UI, sans-serif"}}],
                template="plotly_white",
                height=430,
                margin=dict(l=40, r=40, t=60, b=80),
                showlegend=True,
                legend={"orientation": "h", "y": -0.05, "x": 0.5, "xanchor": "center",
                        "font": {"size": 11, "color": "#374151"}},
                hoverlabel={"bgcolor": "#064E3B", "bordercolor": "#064E3B",
                            "font": {"color": "white"}},
            )
            return fig

        def grafica_barras_v(serie, titulo, subtitulo, xlabel, ylabel, conclusion,
                             color="#059669", formato="n", top=None):
            s = serie.sort_values(ascending=False)
            if top:
                s = s.head(top)
            fig = go.Figure(go.Bar(
                x=s.index.astype(str), y=s.values, marker_color=color,
                text=[f"{v:,.0f}" if formato == "n" else f"${v:,.0f}" for v in s.values],
                textposition="outside",
                hovertemplate=f"<b>%{{x}}</b><br>{ylabel}: %{{y:,.2f}}<extra></extra>",
            ))
            estilo_fig(fig, titulo, subtitulo, xlabel, ylabel)
            fig.update_xaxes(tickangle=40)
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_barras_h(serie, titulo, subtitulo, xlabel, conclusion,
                             color="#059669", top=None):
            s = serie.sort_values(ascending=True)
            if top:
                s = s.tail(top)
            fig = go.Figure(go.Bar(
                y=s.index.astype(str), x=s.values, orientation="h",
                marker_color=color, text=[f"{v:,.0f}" for v in s.values],
                textposition="outside",
                hovertemplate=f"<b>%{{y}}</b><br>{xlabel}: %{{x:,.0f}}<extra></extra>",
            ))
            estilo_fig(fig, titulo, subtitulo, "", xlabel)
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_pastel(serie, titulo, subtitulo, conclusion, top=None):
            s = serie.sort_values(ascending=False)
            if top and len(s) > top:
                resto = s.iloc[top:].sum()
                s = pd.concat([s.head(top), pd.Series({"Otros": resto})])
            fig = go.Figure(go.Pie(
                labels=s.index.astype(str), values=s.values,
                marker=dict(colors=PALETA[:len(s)], line=dict(color="white", width=1.5)),
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} entregas (%{percent})<extra></extra>",
            ))
            fig.update_traces(textposition="outside",
                              textfont=dict(size=11, color="#374151"))
            titulo_pie(fig, titulo, subtitulo)
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_linea_t(series, titulo, subtitulo, conclusion, ylabel="Entregas"):
            fig = go.Figure(go.Scatter(
                x=series.index, y=series.values, mode="lines+markers",
                line=dict(color="#059669", width=2.5),
                marker=dict(size=6, color="#047857"),
                fill="tozeroy", fillcolor="rgba(5,150,105,0.12)",
                hovertemplate=f"%{{x}}<br>{ylabel}: %{{y:,.0f}}<extra></extra>",
            ))
            estilo_fig(fig, titulo, subtitulo, "Fecha", ylabel)
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_area_t(series, titulo, subtitulo, conclusion):
            acum = series.cumsum()
            fig = go.Figure(go.Scatter(
                x=series.index, y=acum.values, mode="lines",
                line=dict(color="#047857", width=2.5),
                fill="tozeroy", fillcolor="rgba(5,150,105,0.45)",
                hovertemplate="%{x}<br>Acumulado: %{y:,.0f}<extra></extra>",
            ))
            estilo_fig(fig, titulo, subtitulo, "Fecha", "Entregas acumuladas")
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def dispersion_plotly(df, titulo, subtitulo, conclusion):
            fig = go.Figure()
            colores_est = {"Entregado": "#059669", "Retrasado": "#EF4444", "Cancelado": "#9CA3AF"}
            for estatus, color in colores_est.items():
                sub = df[df["estatus"] == estatus]
                if not sub.empty:
                    fig.add_trace(go.Scatter(
                        x=sub["distancia_km"], y=sub["minutos_reales"], mode="markers",
                        name=estatus, marker=dict(color=color, size=7, opacity=0.7),
                        customdata=sub[["cliente_nombre", "operador_nombre", "ruta_nombre"]],
                        hovertemplate=("<b>%{customdata[2]}</b><br>Distancia: %{x:.0f} km"
                                       "<br>Minutos reales: %{y:.0f} min"
                                       "<br>Cliente: %{customdata[0]}<br>Operador: %{customdata[1]}"
                                       "<extra></extra>"),
                    ))
            fig.update_layout(
                legend={"title": "Estatus", "orientation": "h", "y": 1.02, "x": 0,
                        "xanchor": "left", "yanchor": "bottom", "font": {"size": 11}},
            )
            estilo_fig(fig, titulo, subtitulo, "Distancia de la ruta (km)", "Minutos reales de la entrega")
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_heatmap_dh(piv, titulo, subtitulo, conclusion):
            fig = go.Figure(go.Heatmap(
                z=piv.values, x=[f"{h}:00" for h in piv.columns], y=piv.index,
                colorscale="Greens", hoverongaps=False,
                hovertemplate="Dia: %{y}<br>Hora: %{x}<br>Entregas: %{z}<extra></extra>",
            ))
            fig.update_layout(coloraxis_colorbar={"title": "Entregas"})
            estilo_fig(fig, titulo, subtitulo, "Hora de salida", "Dia de la semana")
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        def grafica_heatmap_corr(df, titulo, subtitulo, conclusion):
            num = df[["distancia_km", "minutos_estimados", "minutos_reales"]].dropna()
            corr = num.corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.index,
                zmin=-1, zmax=1, colorscale="RdYlGn",
                text=[["%.2f" % v for v in row] for row in corr.values],
                texttemplate="%{text}", textfont=dict(size=11),
                hovertemplate="%{y} x %{x}: %{z:.2f}<extra></extra>",
            ))
            fig.update_layout(coloraxis_colorbar={"title": "Correlacion"})
            estilo_fig(fig, titulo, subtitulo, "Variable", "Variable")
            anadir_reporte(fig, titulo, subtitulo, conclusion)

        if entregas_f.empty:
            st.warning("No hay entregas en el periodo seleccionado; elige otro rango de fechas "
                       "para ver las graficas.")
        else:
            em = entregas_f.merge(clientes, left_on="cliente_id", right_on="id", suffixes=("", "_cli"))
            em = em.merge(rutas, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))
            em = em.merge(vehiculos, left_on="vehiculo_id", right_on="id", suffixes=("", "_veh"))
            em = em.merge(operadores, left_on="operador_id", right_on="id", suffixes=("", "_op"))

            em["cliente_nombre"] = em["nombre"]
            em["operador_nombre"] = em["nombre_op"]
            em["vehiculo_nombre"] = em["placas"] + " \u00b7 " + em["modelo"]
            em["ruta_nombre"] = em["origen"] + " \u2192 " + em["destino"]

            # ---------- Grafica principal configurable ----------
            st.markdown("### Configura tu grafica principal")
            col_c1, col_c2, col_c3 = st.columns(3)
            var_sel = col_c1.selectbox("Variable a graficar",
                                       ["Ruta", "Operador", "Cliente", "Vehiculo"])
            tipo_sel = col_c2.selectbox("Tipo de grafica",
                                        ["Barras verticales", "Barras horizontales", "Pastel"])
            top_sel = col_c3.slider("Mostrar top N categorias", 3, 20, 10)

            variables = {
                "Ruta": em["ruta_nombre"].value_counts(),
                "Operador": em["operador_nombre"].value_counts(),
                "Cliente": em["cliente_nombre"].value_counts(),
                "Vehiculo": em["vehiculo_nombre"].value_counts(),
            }
            serie_sel = variables[var_sel]
            sub_principal = f"Datos reales agrupados por {var_sel.lower()} \u00b7 {sub_periodo}"
            if tipo_sel == "Barras verticales":
                grafica_barras_v(serie_sel,
                                 f"Entregas por {var_sel} (barras interactivas)",
                                 sub_principal, var_sel, "Numero de entregas",
                                 f"La categoria con la barra mas alta concentra el mayor volumen "
                                 f"de entregas por {var_sel.lower()} en el periodo.",
                                 top=top_sel)
            elif tipo_sel == "Barras horizontales":
                grafica_barras_h(serie_sel,
                                 f"Entregas por {var_sel} (barras horizontales)",
                                 sub_principal, "Numero de entregas",
                                 f"El {var_sel.lower()} con mas entregas soporta la mayor carga "
                                 "de trabajo en el periodo; sirve para repartir de forma mas pareja.",
                                 top=top_sel)
            else:
                grafica_pastel(serie_sel,
                               f"Distribucion por {var_sel} (pastel con %)",
                               f"Participacion porcentual de cada {var_sel.lower()} \u00b7 {sub_periodo}",
                               f"El {var_sel.lower()} con mayor porcentaje es el mas importante "
                               "de la operacion en el periodo; conviene cuidar su nivel de servicio.",
                               top=top_sel)

            st.divider()
            st.markdown("### Mas graficas interactivas")

            grafica_pastel(em["estatus"].value_counts(),
                           "Distribucion por estatus (pastel con %)",
                           f"Porcentaje de entregas segun su resultado \u00b7 {sub_periodo}",
                           "El porcentaje de entregas entregadas frente a retrasadas/canceladas "
                           "indica la calidad del servicio; un % alto de retraso apunta a "
                           "problemas de planeacion.")

            gran_sel = st.selectbox("Granularidad de la tendencia",
                                    ["Por dia", "Por semana", "Por mes"], key="gran_tend")
            tend_raw = em.set_index("_fecha")
            if gran_sel == "Por dia":
                tendencia = tend_raw["id"].resample("D").count()
            elif gran_sel == "Por semana":
                tendencia = tend_raw["id"].resample("W").count()
            else:
                tendencia = tend_raw["id"].resample("MS").count()
            tendencia = tendencia[tendencia > 0]

            grafica_linea_t(tendencia,
                            f"Tendencia de entregas (linea) \u2014 {gran_sel}",
                            f"Cantidad de entregas por periodo de tiempo \u00b7 {sub_periodo}",
                            "Muestra los picos y valles de la operacion; sirve para anticipar "
                            "demanda y asignar la flota a tiempo.",
                            ylabel=f"Entregas {gran_sel}")

            grafica_area_t(tendencia,
                           "Entregas acumuladas (area)",
                           f"Total de entregas sumadas a lo largo del periodo \u00b7 {sub_periodo}",
                           "La pendiente de la curva indica el ritmo de la operacion: mientras "
                           "mas empinada, mas entregas concentradas en menos tiempo.")

            dispersion_plotly(em,
                              "Distancia vs tiempo real (dispersion interactiva)",
                               f"Cada punto es una entrega real, coloreada por su estatus \u00b7 {sub_periodo}",
                               "A mayor distancia se tarda mas; los puntos rojos (retrasadas) "
                               "fuera de la tendencia son entregas a revisar.")

            piv_dh = em.copy()
            piv_dh["dia_semana"] = piv_dh["_fecha"].dt.dayofweek
            piv_dh["hora"] = piv_dh["hora_salida"].str.slice(0, 2).astype(int)
            horas = sorted(piv_dh["hora"].unique())
            piv = piv_dh.pivot_table(index="dia_semana", columns="hora", values="id",
                                     aggfunc="count", fill_value=0)
            piv = piv.reindex(index=range(7), columns=horas, fill_value=0)
            piv.index = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
            grafica_heatmap_dh(piv,
                               "Entregas por dia y hora de salida (mapa de calor)",
                               f"Celda mas oscura = mas entregas en ese dia y hora \u00b7 {sub_periodo}",
                               "Las celdas mas intensas muestran cuando hay mas operacion; "
                               "conviene programar descansos y carga fuera de esas horas.")

            grafica_heatmap_corr(em,
                                 "Correlacion entre variables (mapa de calor)",
                                 "Verde = positiva, rojo = negativa; mas intenso = mas fuerte.",
                                 "Las correlaciones altas y positivas (p. ej. distancia con "
                                 "minutos reales) confirman que variables sirven para predecir "
                                 "los tiempos de entrega.")

            em_ok = em.dropna(subset=["minutos_reales"]).copy()
            if not em_ok.empty:
                em_ok["retraso_min"] = em_ok["minutos_reales"] - em_ok["minutos_estimados"]
                grafica_barras_v(em_ok.groupby("ruta_nombre")["retraso_min"].mean(),
                                 "Retraso promedio por ruta (barras)",
                                 f"Minutos de retraso promedio por ruta \u00b7 {sub_periodo}",
                                 "Ruta", "Minutos de retraso",
                                 "Una ruta con retraso alto puede indicar transito o tiempos de "
                                 "carga largos; sirve para planear mejor las salidas.")

        if not combustible_f.empty:
            costo_veh = combustible_f.merge(vehiculos, left_on="vehiculo_id", right_on="id",
                                            suffixes=("", "_veh"))
            grafica_barras_v(costo_veh.groupby("placas")["costo"].sum(),
                             "Costo de combustible por vehiculo (barras)",
                             f"Suma del costo de combustible en el periodo \u00b7 {sub_periodo}",
                             "Vehiculo", "Costo ($)",
                             "Las unidades en la parte superior consumen mas dinero; son "
                             "candidatas a revision de consumo o mantenimiento.",
                             formato="$")

        costo_comb = (combustible_f.groupby("vehiculo_id")["costo"].sum()
                      if not combustible_f.empty else pd.Series(dtype=float))
        costo_mant = (mantenimiento_f.groupby("vehiculo_id")["costo"].sum()
                      if not mantenimiento_f.empty else pd.Series(dtype=float))
        costo_total = pd.concat([costo_comb, costo_mant], axis=1).fillna(0)
        costo_total.columns = ["costo_combustible", "costo_mantenimiento"]
        costo_total["costo_total"] = costo_total.sum(axis=1)
        costo_total = costo_total.merge(vehiculos[["id", "placas"]], left_index=True, right_on="id")
        costo_total = costo_total.sort_values("costo_total", ascending=False)

        if not costo_total.empty:
            grafica_barras_v(costo_total.set_index("placas")["costo_total"],
                             "Costo total por vehiculo: combustible + mantenimiento (barras)",
                             f"Suma de costos del periodo \u00b7 {sub_periodo}",
                             "Vehiculo", "Costo total ($)",
                             "Los vehiculos en la parte superior concentran el mayor gasto y "
                             "son candidatos a revisar o reasignar.",
                             color="#064E3B", formato="$")

        # ------------------------------------------------------------------
        # Mostrar las graficas en la interfaz
        # ------------------------------------------------------------------
        def mostrar_reporte(rep, numero):
            with st.expander(f"{numero}. {rep['titulo']}", expanded=False):
                st.markdown(f"*{rep['subtitulo']}*")
                st.plotly_chart(rep["fig"], width="stretch",
                                config={"displayModeBar": True,
                                        "toImageButtonOptions": {"format": "png", "scale": 2}})
                st.markdown(f"**Conclusion:** {rep['conclusion']}")

        st.markdown("### Todas las graficas del periodo")
        for i in range(0, len(reportes), 2):
            col_a, col_b = st.columns(2)
            with col_a:
                mostrar_reporte(reportes[i], i + 1)
            if i + 1 < len(reportes):
                with col_b:
                    mostrar_reporte(reportes[i + 1], i + 2)

        if not reportes:
            st.info("No hay graficas que mostrar para el periodo seleccionado.")

        # ------------------------------------------------------------------
        # Tablas del periodo
        # ------------------------------------------------------------------
        st.divider()
        st.markdown("### Tablas del periodo")

        st.markdown(f"**Detalle de costos por vehiculo** \u2014 datos del periodo {f1} al {f2}.")
        st.dataframe(costo_total, width="stretch")
        st.caption("Conclusion: los vehiculos en la parte superior concentran el mayor gasto "
                   "en el periodo; son candidatos a revisar o reasignar.")

        st.markdown(f"**Vehiculos no disponibles para operar** \u2014 estatus al dia {f2}.")
        st.dataframe(vehiculos[vehiculos["estatus"] != "Activo"], width="stretch")
        st.caption("Conclusion: las unidades con estatus distinto a Activo no estan "
                   "disponibles para operar; planea su atencion o retiro.")

        # ------------------------------------------------------------------
        # Reporte descargable (HTML interactivo) con fecha, dia y hora
        # ------------------------------------------------------------------
        st.divider()
        st.markdown("### Generar reporte descargable")
        st.caption("El reporte conserva las graficas interactivas (puedes pasarte con el cursor "
                   "y acercar la vista) e incluye la fecha, el dia y la hora de generacion, el "
                   "periodo seleccionado y los indicadores.")

        def construir_html_reporte():
            from datetime import datetime

            ahora = datetime.now()
            dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                     "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            fecha_gen = (f"{dias_semana[ahora.weekday()]}, {ahora.day} de {meses[ahora.month - 1]} "
                         f"de {ahora.year}, a las {ahora.strftime('%H:%M:%S')} hrs.")

            partes = [f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Reporte SIG-LOG</title>
<style>
body{{font-family:'Inter','Segoe UI',Arial,sans-serif;color:#1F2937;margin:32px;background:#F9FAFB;}}
h1{{color:#064E3B;border-bottom:3px solid #059669;padding-bottom:8px;}}
h2{{color:#065F46;margin-top:34px;}}
.meta{{color:#6B7280;font-size:14px;margin:4px 0;}}
.grafica{{margin:24px 0;background:#fff;padding:20px;border-radius:12px;border:1px solid #E5E7EB;box-shadow:0 1px 3px rgba(0,0,0,0.04);}}
.conclusion{{background:#F0FDF4;border-left:4px solid #059669;padding:8px 12px;border-radius:6px;margin-top:8px;}}
.sub{{color:#6B7280;font-size:13px;}}
table{{border-collapse:collapse;width:100%;font-size:13px;}}
th,td{{border:1px solid #E5E7EB;padding:6px 10px;text-align:left;}}
th{{background:#ECFDF5;color:#064E3B;}}
</style></head><body>
<h1>Reporte SIG-LOG \u2014 Reportes y analisis</h1>
<p class="meta"><b>Generado:</b> {fecha_gen}</p>
<p class="meta"><b>Periodo de los datos:</b> {f1} al {f2}</p>
<p class="meta"><b>Indicadores:</b> {n_ent} entregas \u00b7 entregadas {pct_entregadas:.1f}% \u00b7 retrasadas {pct_retrasadas:.1f}% \u00b7 canceladas {pct_canceladas:.1f}% \u00b7 tiempo real promedio {tiempo_prom:.0f} min</p>
"""]

            for i, rep in enumerate(reportes, 1):
                div_html = rep["fig"].to_html(
                    full_html=False, include_plotlyjs=("cdn" if i == 1 else False),
                    div_id=f"grafica_{i}", default_height="430px",
                    config={"displayModeBar": True})
                partes.append(f"""<div class="grafica">
<h2>{i}. {rep['titulo']}</h2>
<p class="sub">{rep['subtitulo']}</p>
{div_html}
<p class="conclusion"><b>Conclusion:</b> {rep['conclusion']}</p>
</div>""")

            if not costo_total.empty:
                filas = "".join(
                    f"<tr><td>{r['placas']}</td><td>${r['costo_combustible']:,.2f}</td>"
                    f"<td>${r['costo_mantenimiento']:,.2f}</td><td>${r['costo_total']:,.2f}</td></tr>"
                    for _, r in costo_total.iterrows())
                partes.append(f"""<div class="grafica">
<h2>Tabla: Costo total por vehiculo</h2>
<p class="sub">Datos del periodo {f1} al {f2}</p>
<table><thead><tr><th>Vehiculo</th><th>Combustible</th><th>Mantenimiento</th><th>Total</th></tr></thead>
<tbody>{filas}</tbody></table>
</div>""")

            partes.append("</body></html>")
            return "".join(partes)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-radius:16px;
                    padding:1rem 1.5rem; margin-bottom:0.75rem; border:1px solid #BFDBFE;">
            <div style="font-size:0.85rem; color:#1E40AF; font-weight:600;">
                El reporte conserva las graficas interactivas y se puede abrir en cualquier navegador.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_gen, col_desc = st.columns([1, 1])
        with col_gen:
            if st.button("Generar reporte descargable", type="primary", width="stretch"):
                st.session_state["reporte_html"] = construir_html_reporte()
        with col_desc:
            if st.session_state.get("reporte_html"):
                st.download_button("Descargar reporte (HTML)",
                                   data=st.session_state["reporte_html"],
                                   file_name=f"reporte_siglog_{f1}_al_{f2}.html",
                                   mime="text/html", width="stretch")

    # ---------------- Unidad III: Regresion (lineal y multiple) ----------------
    with tabs[3]:
        st.subheader("Regresion lineal simple y multiple")
        st.caption("Objetivo: predecir los minutos reales que tardara una entrega.")
        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Como funciona este modelo</div>
            <div class="info-box-text">La regresion busca una formula que relacione variables de entrada
            (distancia, hora, etc.) con el tiempo real de entrega. Mientras mejor sea el R2, mas preciso
            es el modelo.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

            datos = entregas.merge(rutas, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))
            datos = datos.dropna(subset=["minutos_reales"])
            datos["hora_num"] = datos["hora_salida"].str.slice(0, 2).astype(float)

            if len(datos) > 10:
                st.markdown("### Regresion lineal simple")
                st.write("Variable independiente: `distancia_km` \u2192 Variable dependiente: `minutos_reales`")
                X1 = datos[["distancia_km"]]
                y = datos["minutos_reales"]
                X1_tr, X1_te, y1_tr, y1_te = train_test_split(X1, y, test_size=0.25, random_state=42)
                modelo_simple = LinearRegression().fit(X1_tr, y1_tr)
                pred1 = modelo_simple.predict(X1_te)

                c1, c2, c3 = st.columns(3)
                c1.metric("MAE", f"{mean_absolute_error(y1_te, pred1):.1f} min",
                          help="Error absoluto promedio: promedio de las diferencias entre prediccion y realidad")
                c2.metric("RMSE", f"{mean_squared_error(y1_te, pred1) ** 0.5:.1f} min",
                          help="Error cuadratico medio: penaliza mas los errores grandes")
                c3.metric("R2", f"{r2_score(y1_te, pred1):.2f}",
                          help="Coeficiente de determinacion: que tan bien explica el modelo los datos (1.0 = perfecto)")

                orden = X1_te["distancia_km"].argsort()
                linea_x = X1_te["distancia_km"].to_numpy()[orden]
                linea_y = pred1[orden]
                grafica_dispersion_modelo(
                    X1_te["distancia_km"], y1_te,
                    "Regresion lineal simple: distancia vs minutos reales",
                    f"Puntos de prueba (25% de los datos, no usados para entrenar) \u00b7 n={len(y1_te)}",
                    "Distancia de la ruta (km)", "Minutos reales de la entrega",
                    f"R2 = {r2_score(y1_te, pred1):.2f}: entre mas cercano a 1, mejor explica la distancia "
                    "el tiempo real; los puntos alejados de la linea roja son entregas atipicas.",
                    linea_tendencia=(linea_x, linea_y))

                st.divider()
                st.markdown("### Regresion multiple")
                st.write("Variables independientes: `distancia_km`, `minutos_estimados`, `hora_num` (hora de salida)")
                X2 = datos[["distancia_km", "minutos_estimados", "hora_num"]]
                X2_tr, X2_te, y2_tr, y2_te = train_test_split(X2, y, test_size=0.25, random_state=42)
                modelo_mult = LinearRegression().fit(X2_tr, y2_tr)
                pred2 = modelo_mult.predict(X2_te)

                c1, c2, c3 = st.columns(3)
                c1.metric("MAE", f"{mean_absolute_error(y2_te, pred2):.1f} min",
                          help="Error absoluto promedio del modelo multiple")
                c2.metric("RMSE", f"{mean_squared_error(y2_te, pred2) ** 0.5:.1f} min",
                          help="Error cuadratico medio del modelo multiple")
                c3.metric("R2", f"{r2_score(y2_te, pred2):.2f}",
                          help="R2 del modelo multiple: incluye mas variables para mejorar la prediccion")

                mejora = r2_score(y2_te, pred2) - r2_score(y1_te, pred1)
                grafica_dispersion_modelo(
                    y2_te, pred2,
                    "Regresion multiple: valor real vs prediccion",
                    f"Cada punto compara lo que realmente paso contra lo que predijo el modelo \u00b7 n={len(y2_te)}",
                    "Minutos reales (real)", "Minutos reales (prediccion del modelo)",
                    ("El modelo multiple mejora el R2 en "
                     f"{mejora:+.2f} respecto al simple; los puntos cercanos a la diagonal ideal "
                     "son predicciones acertadas."),
                    linea_tendencia=(sorted(y2_te), sorted(y2_te)))

                st.markdown("**Coeficientes del modelo multiple:**")
                coef_df = pd.DataFrame({"variable": X2.columns, "coeficiente": modelo_mult.coef_})
                st.dataframe(coef_df, width="stretch")
                st.caption("Conclusion: un coeficiente positivo indica que al subir esa variable "
                           "tambien sube el tiempo real de entrega; uno negativo indica lo contrario. "
                           "El de mayor valor absoluto es el que mas influye en la prediccion.")

                st.divider()
                st.markdown("### Prueba y error: eligiendo el tamano del conjunto de prueba")
                st.caption("Metodologia de prueba y error: se entrena el mismo modelo con distintas "
                           "proporciones de datos de prueba y se compara el R2 para elegir la mejor.")
                proporciones = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
                r2_por_prop = []
                for p in proporciones:
                    Xp_tr, Xp_te, yp_tr, yp_te = train_test_split(X2, y, test_size=p, random_state=42)
                    mp = LinearRegression().fit(Xp_tr, yp_tr)
                    r2_por_prop.append(r2_score(yp_te, mp.predict(Xp_te)))
                mejor_prop = proporciones[int(pd.Series(r2_por_prop).idxmax())]
                grafica_linea_modelo(
                    [f"{int(p*100)}%" for p in proporciones], r2_por_prop,
                    "R2 del modelo multiple segun % de datos de prueba",
                    "Cada punto entrena y evalua el modelo con una particion distinta (prueba y error)",
                    "Porcentaje de datos usados para prueba", "R2 obtenido",
                    f"La proporcion con mejor R2 en esta corrida fue {int(mejor_prop*100)}%; "
                    "por eso el sistema usa 25% como valor por defecto, un balance entre datos "
                    "suficientes para entrenar y para evaluar.")
            else:
                st.warning("Aun no hay suficientes datos para entrenar el modelo.")
        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")

    # ---------------- Unidad IV: Clasificacion + matriz de confusion ----------------
    with tabs[4]:
        st.subheader("Es posible predecir si una entrega llegara tarde?")
        st.caption("El modelo aprende de entregas pasadas y despues puedes probarlo con datos nuevos.")
        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Como funciona la clasificacion</div>
            <div class="info-box-text">Clasifica cada entrega como "a tiempo" o "tarde" basandose en
            la distancia, el tiempo estimado y la hora de salida. La matriz de confusion muestra los
            aciertos y errores del modelo.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                          f1_score, confusion_matrix)

            datos = entregas.merge(rutas, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))
            datos = datos.dropna(subset=["minutos_reales"])
            datos["hora_num"] = datos["hora_salida"].str.slice(0, 2).astype(float)
            datos["retraso_min"] = datos["minutos_reales"] - datos["minutos_estimados"]
            datos["retrasado"] = (datos["retraso_min"] > 15).astype(int)

            X = datos[["distancia_km", "minutos_estimados", "hora_num"]]
            y = datos["retrasado"]

            if len(datos) > 10 and y.nunique() > 1:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.25, random_state=42, stratify=y)
                escalador = StandardScaler().fit(X_train)
                X_train_s = escalador.transform(X_train)
                X_test_s = escalador.transform(X_test)
                modelo = LogisticRegression(class_weight="balanced", max_iter=1000)
                modelo.fit(X_train_s, y_train)
                pred = modelo.predict(X_test_s)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Exactitud", f"{accuracy_score(y_test, pred):.2%}",
                          help="Porcentaje total de predicciones correctas")
                c2.metric("Precision", f"{precision_score(y_test, pred, zero_division=0):.2%}",
                          help="De las predichas como tarde, cuantas realmente lo fueron")
                c3.metric("Recall", f"{recall_score(y_test, pred, zero_division=0):.2%}",
                          help="De las que realmente fueron tarde, cuantas detecto el modelo")
                c4.metric("F1-score", f"{f1_score(y_test, pred, zero_division=0):.2%}",
                          help="Promedio harmonico entre precision y recall")

                cm = confusion_matrix(y_test, pred, labels=[0, 1])
                matriz_confusion_modelo(
                    cm, "Matriz de confusion del modelo de clasificacion",
                    f"Conjunto de prueba \u00b7 n={len(y_test)} entregas no usadas para entrenar",
                    "La diagonal (arriba-izquierda y abajo-derecha) son los aciertos; fuera de "
                    "la diagonal son los errores del modelo. Entre mas alto el numero fuera de "
                    "la diagonal, mas se equivoca el modelo en esa combinacion.")

                st.divider()
                st.markdown("### Prueba y error: eligiendo el umbral de decision")
                st.caption("El modelo calcula una probabilidad de retraso; el umbral decide a partir "
                           "de que probabilidad se clasifica como \"tarde\". Se prueban varios umbrales "
                           "y se compara F1-score para elegir el que mejor equilibra precision y recall.")
                proba_test = modelo.predict_proba(X_test_s)[:, 1]
                umbrales = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
                f1_por_umbral = []
                for u in umbrales:
                    pred_u = (proba_test >= u).astype(int)
                    f1_por_umbral.append(f1_score(y_test, pred_u, zero_division=0))
                mejor_umbral = umbrales[int(pd.Series(f1_por_umbral).idxmax())]
                grafica_linea_modelo(
                    umbrales, f1_por_umbral,
                    "F1-score del modelo segun el umbral de decision",
                    "Cada punto reclasifica el mismo conjunto de prueba con un umbral distinto (prueba y error)",
                    "Umbral de probabilidad para clasificar como \"tarde\"", "F1-score",
                    f"El umbral con mejor F1-score en esta corrida es {mejor_umbral:.2f}; subir el "
                    "umbral favorece la precision y bajarlo favorece detectar mas retrasos (recall).",
                    color="#3B82F6")

                st.divider()
                st.markdown("**Probar el modelo con datos nuevos:**")
                dist = st.number_input("Distancia (km)", value=100.0)
                minu = st.number_input("Minutos estimados", value=120.0)
                hora_in = st.number_input("Hora de salida (0-23)", value=8, min_value=0, max_value=23)
                if st.button("Predecir"):
                    entrada = escalador.transform([[dist, minu, hora_in]])
                    resultado = modelo.predict(entrada)[0]
                    st.info("Prediccion: **" + ("Llegara tarde" if resultado == 1 else "Llegara a tiempo") + "**")
            else:
                st.warning("Aun no hay suficientes datos variados para entrenar el modelo.")
        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")

    # ---------------- Unidad V: Clustering (PCA + K-means + codo + silueta) ----------------
    with tabs[5]:
        st.subheader("Podemos identificar grupos de rutas similares?")
        st.caption("El sistema agrupa las rutas segun su distancia y numero de entregas.")
        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Como funciona el clustering</div>
            <div class="info-box-text">Agrupa las rutas automaticamente segun sus caracteristicas
            (distancia y volumen de entregas). El metodo del codo y el indice de silueta ayudan a
            elegir el numero optimo de grupos.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score

            resumen_rutas = entregas.merge(rutas, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))
            resumen_rutas = resumen_rutas.groupby("ruta_id").agg(
                distancia_km=("distancia_km", "first"),
                num_entregas=("id", "count"),
            ).reset_index()

            if len(resumen_rutas) >= 4:
                X = resumen_rutas[["distancia_km", "num_entregas"]]
                X_esc = StandardScaler().fit_transform(X)

                # --- Metodo del codo (inercia): prueba y error sobre k ---
                st.markdown("### Metodo del codo (inercia vs numero de clusters)")
                st.caption("Metodologia de prueba y error: se entrena K-means con distintos valores "
                           "de k y se observa donde la inercia deja de bajar de forma importante.")
                inercias = []
                rango_k = list(range(1, min(7, len(resumen_rutas))))
                for k in rango_k:
                    km_prueba = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_esc)
                    inercias.append(km_prueba.inertia_)
                grafica_linea_modelo(
                    rango_k, inercias, "Metodo del codo: inercia por numero de clusters",
                    f"Suma de distancias al cuadrado dentro de cada grupo \u00b7 {len(resumen_rutas)} rutas analizadas",
                    "Numero de clusters (k)", "Inercia",
                    "El 'codo' de la curva (donde deja de bajar mucho) sugiere el numero optimo de "
                    "clusters: agregar mas grupos despues de ese punto ya no mejora mucho la agrupacion.")

                # --- Indice de silueta ---
                st.markdown("### Indice de silueta por numero de clusters")
                siluetas = []
                rango_k2 = list(range(2, min(7, len(resumen_rutas))))
                for k in rango_k2:
                    km_prueba = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_esc)
                    siluetas.append(silhouette_score(X_esc, km_prueba.labels_))
                mejor_k = rango_k2[int(pd.Series(siluetas).idxmax())]
                grafica_linea_modelo(
                    rango_k2, siluetas, "Indice de silueta por numero de clusters",
                    "Mide que tan bien separados y compactos quedan los grupos (rango -1 a 1)",
                    "Numero de clusters (k)", "Indice de silueta (mas alto = mejor)",
                    f"El valor de k con mejor silueta en esta corrida es {mejor_k}; un indice cercano "
                    "a 1 indica grupos bien definidos y separados entre si.", color="#8B5CF6")

                st.divider()
                n_clusters = st.slider("Numero de grupos (clusters) a usar", 2, min(6, len(resumen_rutas)), 3)
                km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                resumen_rutas["grupo"] = km.fit_predict(X_esc)
                sil_final = silhouette_score(X_esc, resumen_rutas["grupo"])

                m1, m2, m3 = st.columns(3)
                m1.metric("Clusters (k)", n_clusters)
                m2.metric("Indice de silueta", f"{sil_final:.2f}")
                m3.metric("Rutas analizadas", len(resumen_rutas))

                st.markdown("### PCA \u2014 reduccion a 2 dimensiones para visualizar")
                pca = PCA(n_components=2)
                componentes = pca.fit_transform(X_esc)
                resumen_rutas["pca_1"] = componentes[:, 0]
                resumen_rutas["pca_2"] = componentes[:, 1]
                varianza = pca.explained_variance_ratio_.sum()

                st.dataframe(resumen_rutas, width="stretch")
                grafica_dispersion_modelo(
                    resumen_rutas["pca_1"], resumen_rutas["pca_2"],
                    "Rutas agrupadas por similitud (PCA + K-means)",
                    f"Cada punto es una ruta; los 2 componentes de PCA explican {varianza:.1%} de la "
                    f"variacion original \u00b7 k={n_clusters}",
                    "Componente principal 1", "Componente principal 2",
                    "Los puntos del mismo color comparten caracteristicas de distancia y volumen de "
                    "entregas; sirve para asignar flota o promociones por grupo de rutas similares.",
                    color_serie=resumen_rutas["grupo"], nombre_color="Cluster")
            else:
                st.warning("Se necesitan al menos 4 rutas con entregas para agrupar.")
        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")
