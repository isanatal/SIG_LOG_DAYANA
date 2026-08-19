import pandas as pd
import streamlit as st

from services import crud


def render():
    st.markdown("<div class='modulo-header'><h1>Procesamiento de datos</h1>"
                "<p>ETL con sklearn: escalado, imputacion, pipelines y calidad de datos.</p></div>",
                unsafe_allow_html=True)

    import plotly.graph_objects as go

    entregas = crud.leer_tabla("entregas")
    rutas = crud.leer_tabla("rutas")
    vehiculos = crud.leer_tabla("vehiculos")
    operadores = crud.leer_tabla("operadores")
    clientes = crud.leer_tabla("clientes")

    tabs = st.tabs([
        "1. Calidad de datos",
        "2. Imputacion de nulos",
        "3. Escalado de variables",
        "4. Features polinomiales",
        "5. Pipeline ETL",
    ])

    PALETA = ["#059669", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6",
              "#14B8A6", "#F97316", "#6B7280", "#DB2777", "#0EA5E9"]

    def estilo(fig, titulo, subtitulo, xlabel="", ylabel="", altura=420):
        fig.update_layout(
            title={"text": titulo, "x": 0.5, "xanchor": "center",
                   "font": {"size": 15, "color": "#064E3B", "family": "Inter, Segoe UI, sans-serif"}},
            annotations=[{"text": subtitulo, "xref": "paper", "yref": "paper",
                          "x": 0.5, "y": -0.20, "showarrow": False, "xanchor": "center",
                          "font": {"size": 11, "color": "#6B7280", "family": "Inter, Segoe UI, sans-serif"}}],
            xaxis_title=xlabel, yaxis_title=ylabel,
            template="plotly_white", height=altura,
            margin=dict(l=70, r=30, t=60, b=100),
            hoverlabel={"bgcolor": "#064E3B", "bordercolor": "#064E3B",
                        "font": {"color": "white", "family": "Inter, Segoe UI, sans-serif"}},
        )
        fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
        fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
        return fig

    # ----------------------------------------------------------------
    # Tab 1: Calidad de datos
    # ----------------------------------------------------------------
    with tabs[0]:
        st.subheader("Analisis de calidad de datos")
        st.caption("Revisa el estado de tus datos antes de procesarlos: nulos, duplicados, "
                   "tipos de dato y valores atipicos.")

        datos = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                               suffixes=("", "_ruta"))
        datos = datos.dropna(subset=["minutos_reales"])
        datos["hora_num"] = datos["hora_salida"].str.slice(0, 2).astype(float)
        datos["retraso_min"] = datos["minutos_reales"] - datos["minutos_estimados"]

        st.markdown("**Resumen general del dataset de entregas:**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registros totales", len(datos))
        c2.metric("Columnas", len(datos.columns))
        c3.metric("Duplicados", datos.duplicated().sum())
        c4.metric("Nulos totales", datos.isnull().sum().sum())

        st.divider()
        st.markdown("**Valores nulos por columna:**")
        nulos = datos.isnull().sum()
        nulos = nulos[nulos > 0]
        if not nulos.empty:
            fig = go.Figure(go.Bar(
                x=nulos.index, y=nulos.values,
                marker_color="#EF4444",
                text=nulos.values, textposition="outside",
            ))
            estilo(fig, "Columnas con valores nulos",
                   "Cuantos registros faltantes hay por columna",
                   "Columna", "Cantidad de nulos")
            st.plotly_chart(fig, width="stretch")
        else:
            st.success("No hay valores nulos en el dataset.")

        st.divider()
        st.markdown("**Tipos de dato detectados:**")
        tipos = pd.DataFrame({
            "columna": datos.columns,
            "tipo": [str(t) for t in datos.dtypes],
            "nunicos": [datos[c].nunique() for c in datos.columns],
            "ejemplo": [str(datos[c].dropna().iloc[0]) if not datos[c].dropna().empty else ""
                        for c in datos.columns],
        })
        st.dataframe(tipos, width="stretch", hide_index=True)

        st.divider()
        st.markdown("**Deteccion de valores atipicos (metodo IQR):**")
        col_num = st.selectbox("Columna numerica para detectar atipicos",
                               ["distancia_km", "minutos_estimados", "minutos_reales", "retraso_min"],
                               key="col_outlier")
        if col_num in datos.columns:
            vals = datos[col_num].dropna()
            q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
            iqr = q3 - q1
            lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            atipicos = datos[(datos[col_num] < lim_inf) | (datos[col_num] > lim_sup)]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Q1", f"{q1:.1f}")
            c2.metric("Q3", f"{q3:.1f}")
            c3.metric("IQR", f"{iqr:.1f}")
            c4.metric("Atipicos", f"{len(atipicos)} ({len(atipicos)/len(datos)*100:.1f}%)")

            fig = go.Figure()
            fig.add_trace(go.Box(y=datos[col_num], name="Todos",
                                 marker_color="#059669", boxmean=True))
            fig.add_trace(go.Box(y=atipicos[col_num] if not atipicos.empty else [],
                                 name="Atipicos", marker_color="#EF4444"))
            estilo(fig, f"Boxplot de {col_num}",
                   f"Valores fuera de [{lim_inf:.1f}, {lim_sup:.1f}] se consideran atipicos",
                   "", col_num, altura=350)
            st.plotly_chart(fig, width="stretch")
            if not atipicos.empty:
                st.dataframe(atipicos.head(10), width="stretch")

    # ----------------------------------------------------------------
    # Tab 2: Imputacion de nulos
    # ----------------------------------------------------------------
    with tabs[1]:
        st.subheader("Imputacion de valores faltantes")
        st.caption(" sklearn SimpleImputer: sustituye nulos con media, mediana o moda.")

        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Que es la imputacion?</div>
            <div class="info-box-text">Cuando faltan datos, en vez de borrar la fila completa,
            se puede rellenar con un valor representativo (media, mediana, moda, constante).
            sklearn SimpleImputer hace esto automaticamente.</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            from sklearn.impute import SimpleImputer
            from sklearn.compose import ColumnTransformer
            from sklearn.pipeline import Pipeline

            df_imp = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                                    suffixes=("", "_ruta"))
            df_imp = df_imp[["minutos_estimados", "minutos_reales", "distancia_km"]].copy()

            nulos_antes = df_imp.isnull().sum().sum()
            st.markdown(f"**Nulos antes de imputar:** {nulos_antes}")

            col_imp = st.selectbox("Estrategia de imputacion",
                                   ["Media", "Mediana", "Moda", "Constante (0)"],
                                   key="estrategia_imp")
            valor_const = st.number_input("Valor constante", value=0.0,
                                          key="valor_const") if col_imp == "Constante (0)" else None

            estrategia_map = {
                "Media": "mean", "Mediana": "median",
                "Moda": "most_frequent", "Constante (0)": "constant",
            }
            kwargs = {"strategy": estrategia_map[col_imp]}
            if col_imp == "Constante (0)":
                kwargs["fill_value"] = valor_const

            imputer = SimpleImputer(**kwargs)
            df_imputed = pd.DataFrame(
                imputer.fit_transform(df_imp),
                columns=df_imp.columns,
            )

            nulos_despues = df_imputed.isnull().sum().sum()
            st.markdown(f"**Nulos despues de imputar:** {nulos_despues}")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Antes de imputar (primeras 10 filas):**")
                st.dataframe(df_imp.head(10), width="stretch")
            with c2:
                st.markdown("**Despues de imputar (primeras 10 filas):**")
                st.dataframe(df_imputed.head(10), width="stretch")

            st.divider()
            st.markdown("**Comparacion de distribucion antes/despues:**")
            col_comp = st.selectbox("Variable a comparar", df_imp.columns, key="col_comp_imp")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df_imp[col_comp].dropna(), name="Antes",
                                       marker_color="#059669", opacity=0.6, nbinsx=20))
            fig.add_trace(go.Histogram(x=df_imputed[col_comp], name="Despues",
                                       marker_color="#F59E0B", opacity=0.6, nbinsx=20))
            fig.update_layout(barmode="overlay", template="plotly_white", height=400,
                              legend={"orientation": "h", "y": 1.02},
                              hoverlabel={"bgcolor": "#064E3B"})
            estilo(fig, f"Distribucion de {col_comp} antes/despues de imputar",
                   f"Estrategia: {col_imp}", col_comp, "Frecuencia")
            st.plotly_chart(fig, width="stretch")
            st.markdown(f"**Conclusion:** La imputacion por {col_imp.lower()} "
                        "mantiene la forma general de la distribucion mientras rellena los vacios.")

        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")

    # ----------------------------------------------------------------
    # Tab 3: Escalado de variables
    # ----------------------------------------------------------------
    with tabs[2]:
        st.subheader("Escalado y normalizacion de variables")
        st.caption("StandardScaler, MinMaxScaler y RobustScaler: compara como transforman "
                   "las distribuciones.")

        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Por que escalar?</div>
            <div class="info-box-text">Algunos modelos (KNN, K-means, regresion logistica)
            son sensibles a la magnitud de las variables. Escalar pone todas en la misma
            escala para que ninguna domine por su unidad de medida.</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

            df_esc = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                                    suffixes=("", "_ruta"))
            df_esc = df_esc.dropna(subset=["minutos_reales"])
            cols_num = ["distancia_km", "minutos_estimados", "minutos_reales"]
            X_esc = df_esc[cols_num].copy()

            escaladores = {
                "Original": X_esc,
                "StandardScaler (z-score)": pd.DataFrame(
                    StandardScaler().fit_transform(X_esc), columns=cols_num),
                "MinMaxScaler (0-1)": pd.DataFrame(
                    MinMaxScaler().fit_transform(X_esc), columns=cols_num),
                "RobustScaler (mediana)": pd.DataFrame(
                    RobustScaler().fit_transform(X_esc), columns=cols_num),
            }

            col_ver = st.selectbox("Variable a visualizar", cols_num, key="col_esc")
            fig = go.Figure()
            for i, (nombre, df_s) in enumerate(escaladores.items()):
                fig.add_trace(go.Box(y=df_s[col_ver], name=nombre,
                                     marker_color=PALETA[i], boxmean=True))
            fig.update_layout(template="plotly_white", height=400,
                              showlegend=True,
                              legend={"orientation": "h", "y": 1.02},
                              hoverlabel={"bgcolor": "#064E3B"})
            estilo(fig, f"Comparacion de escalados: {col_ver}",
                   "Cada metodo transforma los datos de forma distinta",
                   "", col_ver, altura=400)
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Tabla resumen de estadisticas por escalador:**")
            resumen = []
            for nombre, df_s in escaladores.items():
                for c in cols_num:
                    resumen.append({
                        "Escalador": nombre,
                        "Variable": c,
                        "Min": f"{df_s[c].min():.2f}",
                        "Max": f"{df_s[c].max():.2f}",
                        "Media": f"{df_s[c].mean():.2f}",
                        "Std": f"{df_s[c].std():.2f}",
                    })
            st.dataframe(pd.DataFrame(resumen), width="stretch", hide_index=True)

            st.markdown("""
            **Conclusion:**
            - **StandardScaler**: media=0, std=1 (z-score). Ideal para modelos que asumen normalidad.
            - **MinMaxScaler**: rango [0,1]. Ideal para redes neuronales y cuando los limites son conocidos.
            - **RobustScaler**: usa mediana e IQR. Mas resistente a valores atipicos.
            """)

        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")

    # ----------------------------------------------------------------
    # Tab 4: Features polinomiales
    # ----------------------------------------------------------------
    with tabs[3]:
        st.subheader("Generacion de features polinomiales")
        st.caption("PolynomialFeatures crea interacciones y terminos cuadraticos "
                   "que pueden mejorar la precision de los modelos.")

        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Que son las features polinomiales?</div>
            <div class="info-box-text">Si la relacion entre variables no es lineal,
            PolynomialFeatures genera nuevas columnas como x1^2, x2^2, x1*x2, etc.
            Esto permite que un modelo lineal capture patrones no lineales.</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score, mean_absolute_error

            df_poly = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                                     suffixes=("", "_ruta"))
            df_poly = df_poly.dropna(subset=["minutos_reales"])

            grado = st.slider("Grado del polinomio", 1, 4, 2, key="grado_poly")

            X = df_poly[["distancia_km", "minutos_estimados"]]
            y = df_poly["minutos_reales"]

            poly = PolynomialFeatures(degree=grado, include_bias=False)
            X_poly = poly.fit_transform(X)
            nombres = poly.get_feature_names_out(X.columns)

            st.markdown(f"**Columnas generadas ({len(nombres)}):**")
            st.code(", ".join(nombres))

            Xtr, Xte, ytr, yte = train_test_split(X_poly, y, test_size=0.25, random_state=42)
            modelo = LinearRegression().fit(Xtr, ytr)
            pred = modelo.predict(Xte)

            c1, c2 = st.columns(2)
            c1.metric("R2", f"{r2_score(yte, pred):.3f}")
            c2.metric("MAE", f"{mean_absolute_error(yte, pred):.1f} min")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yte, y=pred, mode="markers", name="Predicciones",
                                     marker=dict(color="#059669", size=7, opacity=0.7)))
            min_v, max_v = min(yte.min(), pred.min()), max(yte.max(), pred.max())
            fig.add_trace(go.Scatter(x=[min_v, max_v], y=[min_v, max_v], mode="lines",
                                     name="Ideal (y=x)", line=dict(color="#EF4444", dash="dash")))
            estilo(fig, f"Regresion con features polinomiales (grado {grado})",
                   f"{len(nombres)} features usadas para entrenar",
                   "Minutos reales", "Minutos predichos")
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Comparacion entre grados:**")
            resultados = []
            for g in range(1, 6):
                pg = PolynomialFeatures(degree=g, include_bias=False)
                Xg = pg.fit_transform(X)
                Xtr_g, Xte_g, ytr_g, yte_g = train_test_split(Xg, y, test_size=0.25,
                                                                 random_state=42)
                mg = LinearRegression().fit(Xtr_g, ytr_g)
                pred_g = mg.predict(Xte_g)
                resultados.append({
                    "Grado": g,
                    "Features": Xg.shape[1],
                    "R2": round(r2_score(yte_g, pred_g), 4),
                    "MAE": round(mean_absolute_error(yte_g, pred_g), 1),
                })
            res_df = pd.DataFrame(resultados)
            st.dataframe(res_df, width="stretch", hide_index=True)

            fig2 = go.Figure(go.Bar(x=res_df["Grado"].astype(str), y=res_df["R2"],
                                    marker_color=PALETA[:len(res_df)],
                                    text=res_df["R2"].astype(str), textposition="outside"))
            estilo(fig2, "R2 por grado del polinomio",
                   "A mayor grado, mas features y posible sobreajuste",
                   "Grado", "R2")
            st.plotly_chart(fig2, width="stretch")
            st.markdown("**Conclusion:** Un grado mayor no siempre es mejor: si el R2 "
                        "no mejora significativamente, el modelo mas simple es preferible "
                        "(principio de parsimonia).")

        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")

    # ----------------------------------------------------------------
    # Tab 5: Pipeline ETL
    # ----------------------------------------------------------------
    with tabs[4]:
        st.subheader("Pipeline ETL con sklearn")
        st.caption("Visualiza el flujo completo de transformacion de datos como un "
                   "pipeline de scikit-learn.")

        st.markdown("""
        <div class="info-box" style="margin-bottom:1rem;">
            <div class="info-box-title">Pipeline de sklearn</div>
            <div class="info-box-text">Un Pipeline encadena pasos de transformacion
            y un modelo final. Esto garantiza que los datos de prueba se procesan
            igual que los de entrenamiento, evitando data leakage.</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            from sklearn.pipeline import Pipeline
            from sklearn.impute import SimpleImputer
            from sklearn.preprocessing import StandardScaler, PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score, mean_absolute_error

            df_pipe = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                                     suffixes=("", "_ruta"))
            df_pipe = df_pipe.dropna(subset=["minutos_reales"])

            st.markdown("**Paso 1: Seleccion de variables**")
            X = df_pipe[["distancia_km", "minutos_estimados"]]
            y = df_pipe["minutos_reales"]
            st.dataframe(X.head(5), width="stretch")

            use_imputer = st.checkbox("Incluir imputacion de nulos", value=False)
            use_poly = st.checkbox("Incluir features polinomiales", value=True)
            grado = st.slider("Grado polinomial (si aplica)", 2, 3, 2, key="grado_pipe") if use_poly else 2

            pasos = []
            pasos_info = []
            if use_imputer:
                pasos.append(("imputer", SimpleImputer(strategy="median")))
                pasos_info.append("SimpleImputer(strategy='median')")
            pasos.append(("scaler", StandardScaler()))
            pasos_info.append("StandardScaler()")
            if use_poly:
                pasos.append(("poly", PolynomialFeatures(degree=grado, include_bias=False)))
                pasos_info.append(f"PolynomialFeatures(degree={grado})")
            pasos.append(("model", LinearRegression()))
            pasos_info.append("LinearRegression()")

            st.divider()
            st.markdown("**Paso 2: Pipeline construido**")
            for i, info in enumerate(pasos_info, 1):
                st.markdown(f"  `{i}. {info}`")

            st.divider()
            st.markdown("**Paso 3: Entrenar y evaluar**")
            pipeline = Pipeline(pasos)
            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
            pipeline.fit(Xtr, ytr)
            pred = pipeline.predict(Xte)

            c1, c2, c3 = st.columns(3)
            c1.metric("R2", f"{r2_score(yte, pred):.3f}")
            c2.metric("MAE", f"{mean_absolute_error(yte, pred):.1f} min")
            c3.metric("Pasos", len(pasos))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yte, y=pred, mode="markers", name="Predicciones",
                                     marker=dict(color="#0D9488", size=7, opacity=0.7)))
            mn, mx = min(yte.min(), pred.min()), max(yte.max(), pred.max())
            fig.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines",
                                     name="Ideal", line=dict(color="#EF4444", dash="dash")))
            estilo(fig, "Pipeline ETL: real vs predicho",
                   f"{' + '.join(pasos_info)}",
                   "Minutos reales", "Minutos predichos")
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Paso 4: Predecir con datos nuevos**")
            dist_n = st.number_input("Distancia (km)", value=100.0, key="dist_pipe")
            min_n = st.number_input("Minutos estimados", value=120.0, key="min_pipe")
            if st.button("Predecir con el pipeline", type="primary"):
                resultado = pipeline.predict([[dist_n, min_n]])[0]
                st.info(f"Prediccion: **{resultado:.1f} minutos reales**")
                st.caption("El pipeline aplica todas las transformaciones automaticamente "
                           "antes de predecir.")

            st.divider()
            st.markdown("**Ventajas del Pipeline:**")
            st.markdown("""
            | Ventaja | Descripcion |
            |---|---|
            | Sin data leakage | Se ajusta solo con datos de entrenamiento |
            | Reproducible | Mismos pasos en entrenamiento y produccion |
            | Modular | Se pueden agregar/quitar pasos facilmente |
            | Serializable | Se puede guardar con joblib para produccion |
            """)

        except ImportError:
            st.error("Falta instalar scikit-learn: pip install scikit-learn")
