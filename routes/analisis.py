import pandas as pd
import streamlit as st

from services import crud


def render():
    st.markdown("<div class='modulo-header'><h1>Analisis supervisado</h1>"
                "<p>Regresion polinomial, validacion cruzada, curvas de aprendizaje "
                "y comparacion de modelos.</p></div>",
                unsafe_allow_html=True)

    import plotly.graph_objects as go

    entregas = crud.leer_tabla("entregas")
    rutas = crud.leer_tabla("rutas")

    tabs = st.tabs([
        "1. Regresion polinomial",
        "2. Validacion cruzada (K-Fold)",
        "3. Curvas de aprendizaje",
        "4. Comparacion de modelos",
        "5. Feature importance",
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

    try:
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.preprocessing import PolynomialFeatures, StandardScaler
        from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
        from sklearn.pipeline import Pipeline

        datos = entregas.merge(rutas, left_on="ruta_id", right_on="id", suffixes=("", "_ruta"))
        datos = datos.dropna(subset=["minutos_reales"])

        if len(datos) < 10:
            st.warning("Se necesitan al menos 10 entregas completas para analizar.")
            return

        X = datos[["distancia_km", "minutos_estimados"]]
        y = datos["minutos_reales"]

        # ----------------------------------------------------------------
        # Tab 1: Regresion polinomial
        # ----------------------------------------------------------------
        with tabs[0]:
            st.subheader("Regresion polinomial: grado 1 a 5")
            st.caption("Compara modelos polinomiales de diferentes grados para "
                       "encontrar el que mejor ajusta sin sobreajustarse.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Regresion polinomial</div>
                <div class="info-box-text">Extiende la regresion lineal agregando
                terminos cuadraticos, cubicos, etc. Permite capturar relaciones
                no lineales manteniendo un modelo lineal en los parametros.</div>
            </div>
            """, unsafe_allow_html=True)

            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

            resultados = []
            predicciones = {}
            for g in range(1, 6):
                pipe = Pipeline([
                    ("poly", PolynomialFeatures(degree=g, include_bias=False)),
                    ("scaler", StandardScaler()),
                    ("model", LinearRegression()),
                ])
                pipe.fit(Xtr, ytr)
                pred_g = pipe.predict(Xte)
                predicciones[g] = pred_g
                resultados.append({
                    "Grado": g,
                    "Features": PolynomialFeatures(degree=g, include_bias=False)
                    .fit_transform(Xtr).shape[1],
                    "R2": round(r2_score(yte, pred_g), 4),
                    "MAE": round(mean_absolute_error(yte, pred_g), 1),
                    "RMSE": round(mean_squared_error(yte, pred_g) ** 0.5, 1),
                })

            res_df = pd.DataFrame(resultados)
            st.dataframe(res_df, width="stretch", hide_index=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=res_df["Grado"].astype(str), y=res_df["R2"],
                                 marker_color=PALETA[:len(res_df)],
                                 text=res_df["R2"].astype(str), textposition="outside",
                                 name="R2"))
            estilo(fig, "R2 por grado del polinomio",
                   "Mientras mas alto el R2 (max 1.0), mejor ajusta el modelo",
                   "Grado", "R2")
            st.plotly_chart(fig, width="stretch")

            st.divider()
            grado_sel = st.selectbox("Grado para ver dispersion", [1, 2, 3, 4, 5], index=1,
                                     key="grado_disp")
            pred_sel = predicciones[grado_sel]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=yte, y=pred_sel, mode="markers",
                                      name="Predicciones",
                                      marker=dict(color="#059669", size=7, opacity=0.7)))
            mn, mx = min(yte.min(), pred_sel.min()), max(yte.max(), pred_sel.max())
            fig2.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines",
                                      name="Ideal (y=x)",
                                      line=dict(color="#EF4444", dash="dash")))
            estilo(fig2, f"Regresion polinomial grado {grado_sel}: real vs predicho",
                   f"R2={r2_score(yte, pred_sel):.3f} | MAE={mean_absolute_error(yte, pred_sel):.1f} min",
                   "Minutos reales", "Minutos predichos")
            st.plotly_chart(fig2, width="stretch")
            st.markdown("**Conclusion:** El grado optimo平衡a complejidad con capacidad "
                        "de generalizacion. Un grado muy alto puede sobreajustar.")

        # ----------------------------------------------------------------
        # Tab 2: Validacion cruzada K-Fold
        # ----------------------------------------------------------------
        with tabs[1]:
            st.subheader("Validacion cruzada K-Fold")
            st.caption("Evalua la estabilidad del modelo dividiendo los datos en K "
                       "partes y rotando cual se usa para prueba.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Validacion cruzada</div>
                <div class="info-box-text">En vez de una sola division entrenar/prueba,
                K-Fold divide los datos en K partes. El modelo se entrena K veces,
                cada vez usando una parte distinta como prueba. El promedio es mas
                confiable que una sola medicion.</div>
            </div>
            """, unsafe_allow_html=True)

            k_folds = st.slider("Numero de folds (K)", 3, 10, 5, key="k_folds")
            grado_cv = st.selectbox("Grado del polinomio", [1, 2, 3], index=1, key="grado_cv")

            pipe_cv = Pipeline([
                ("poly", PolynomialFeatures(degree=grado_cv, include_bias=False)),
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ])

            scores_r2 = cross_val_score(pipe_cv, X, y, cv=k_folds, scoring="r2")
            scores_neg_mae = cross_val_score(pipe_cv, X, y, cv=k_folds, scoring="neg_mean_absolute_error")
            scores_mae = -scores_neg_mae

            c1, c2, c3 = st.columns(3)
            c1.metric("R2 promedio", f"{scores_r2.mean():.3f}",
                      help="Promedio del R2 en los K folds")
            c2.metric("R2 desv. std", f"{scores_r2.std():.3f}",
                      help="Desviacion estandar: menor = mas estable")
            c3.metric("MAE promedio", f"{scores_mae.mean():.1f} min")

            fig = go.Figure()
            folds_labels = [f"Fold {i+1}" for i in range(k_folds)]
            fig.add_trace(go.Bar(x=folds_labels, y=scores_r2, name="R2",
                                 marker_color="#059669",
                                 text=[f"{v:.3f}" for v in scores_r2],
                                 textposition="outside"))
            fig.add_hline(y=scores_r2.mean(), line_dash="dash", line_color="#EF4444",
                          annotation_text=f"Promedio: {scores_r2.mean():.3f}")
            estilo(fig, f"R2 por fold (K={k_folds}, grado={grado_cv})",
                   "Cada fold usa una parte distinta como prueba",
                   "Fold", "R2")
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Comparacion de estabilidad por grado:**")
            estab = []
            for g in range(1, 5):
                pg = Pipeline([
                    ("poly", PolynomialFeatures(degree=g, include_bias=False)),
                    ("scaler", StandardScaler()),
                    ("model", LinearRegression()),
                ])
                s_r2 = cross_val_score(pg, X, y, cv=k_folds, scoring="r2")
                s_mae = -cross_val_score(pg, X, y, cv=k_folds, scoring="neg_mean_absolute_error")
                estab.append({
                    "Grado": g,
                    "R2 promedio": round(s_r2.mean(), 4),
                    "R2 std": round(s_r2.std(), 4),
                    "MAE promedio": round(s_mae.mean(), 1),
                    "MAE std": round(s_mae.std(), 1),
                })
            st.dataframe(pd.DataFrame(estab), width="stretch", hide_index=True)
            st.markdown("**Conclusion:** El grado con mejor balance entre R2 alto "
                        "y baja desviacion estandar es el mas confiable para "
                        "generalizar con datos nuevos.")

        # ----------------------------------------------------------------
        # Tab 3: Curvas de aprendizaje
        # ----------------------------------------------------------------
        with tabs[2]:
            st.subheader("Curvas de aprendizaje")
            st.caption("Muestra como mejora (o no) el modelo a medida que recibe "
                       "mas datos de entrenamiento.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Que son las curvas de aprendizaje?</div>
                <div class="info-box-text">Grafican el rendimiento del modelo segun la
                cantidad de datos de entrenamiento. Si la curva de entrenamiento es alta
                pero la de validacion es baja, hay sobreajuste. Si ambas son bajas,
                hay subajuste.</div>
            </div>
            """, unsafe_allow_html=True)

            grado_lc = st.selectbox("Grado del polinomio", [1, 2, 3], index=1, key="grado_lc")

            pipe_lc = Pipeline([
                ("poly", PolynomialFeatures(degree=grado_lc, include_bias=False)),
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ])

            tamano_rel = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            train_sizes_abs, train_scores, val_scores = learning_curve(
                pipe_lc, X, y, train_sizes=tamano_rel, cv=5,
                scoring="r2", random_state=42)

            train_mean = train_scores.mean(axis=1)
            train_std = train_scores.std(axis=1)
            val_mean = val_scores.mean(axis=1)
            val_std = val_scores.std(axis=1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(train_mean),
                mode="lines+markers", name="Entrenamiento",
                line=dict(color="#059669", width=2.5),
                marker=dict(size=7),
            ))
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(train_mean + train_std),
                mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(train_mean - train_std),
                mode="lines", line=dict(width=0), fill="tonexty",
                fillcolor="rgba(5,150,105,0.15)", showlegend=False))
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(val_mean),
                mode="lines+markers", name="Validacion",
                line=dict(color="#F59E0B", width=2.5),
                marker=dict(size=7),
            ))
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(val_mean + val_std),
                mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(
                x=list(train_sizes_abs), y=list(val_mean - val_std),
                mode="lines", line=dict(width=0), fill="tonexty",
                fillcolor="rgba(245,158,11,0.15)", showlegend=False))
            estilo(fig, f"Curva de aprendizaje (grado {grado_lc})",
                   "Entrenamiento (verde) vs Validacion (amarillo)",
                   "Muestras de entrenamiento", "R2")
            st.plotly_chart(fig, width="stretch")

            brecha = train_mean[-1] - val_mean[-1]
            st.markdown(f"**Brecha final (train - val):** {brecha:.3f}")
            if brecha > 0.15:
                st.warning("La brecha es alta: el modelo probablemente esta sobreajustando "
                           "(memoriza entrenamiento pero no generaliza bien).")
            elif val_mean[-1] < 0.5:
                st.warning("El R2 de validacion es bajo: el modelo puede estar "
                           "subajustando (no captura el patron de los datos).")
            else:
                st.success("El modelo muestra un buen balance entre ajuste y generalizacion.")

        # ----------------------------------------------------------------
        # Tab 4: Comparacion de modelos
        # ----------------------------------------------------------------
        with tabs[3]:
            st.subheader("Comparacion de modelos: Linear, Ridge y Lasso")
            st.caption("Compara regresion lineal con sus variantes regularizadas "
                       "para ver cual generaliza mejor.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Regularizacion</div>
                <div class="info-box-text">Ridge (L2) y Lasso (L1) penalizan los
                coeficientes grandes para evitar sobreajuste. Lasso ademas puede
                eliminar variables irrelevantes (coeficiente = 0).</div>
            </div>
            """, unsafe_allow_html=True)

            alpha_val = st.slider("Valor de alpha (regularizacion)", 0.01, 10.0, 1.0, key="alpha")

            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

            modelos = {
                "LinearRegression": LinearRegression(),
                f"Ridge (alpha={alpha_val})": Ridge(alpha=alpha_val),
                f"Lasso (alpha={alpha_val})": Lasso(alpha=alpha_val, max_iter=10000),
            }

            res_modelos = []
            preds_modelos = {}
            for nombre, modelo in modelos.items():
                pipe = Pipeline([
                    ("scaler", StandardScaler()),
                    ("model", modelo),
                ])
                pipe.fit(Xtr, ytr)
                pred_m = pipe.predict(Xte)
                preds_modelos[nombre] = pred_m

                scores_cv = cross_val_score(pipe, X, y, cv=5, scoring="r2")
                res_modelos.append({
                    "Modelo": nombre,
                    "R2 test": round(r2_score(yte, pred_m), 4),
                    "MAE test": round(mean_absolute_error(yte, pred_m), 1),
                    "R2 CV promedio": round(scores_cv.mean(), 4),
                    "R2 CV std": round(scores_cv.std(), 4),
                })

            st.dataframe(pd.DataFrame(res_modelos), width="stretch", hide_index=True)

            fig = go.Figure()
            for i, (nombre, pred_m) in enumerate(preds_modelos.items()):
                fig.add_trace(go.Scatter(x=yte, y=pred_m, mode="markers",
                                         name=nombre,
                                         marker=dict(color=PALETA[i], size=6, opacity=0.6)))
            mn, mx = min(yte.min(), min(p.min() for p in preds_modelos.values())), \
                      max(yte.max(), max(p.max() for p in preds_modelos.values()))
            fig.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines",
                                     name="Ideal", line=dict(color="#6B7280", dash="dash")))
            estilo(fig, "Comparacion: real vs predicho por modelo",
                   f"alpha={alpha_val} para Ridge y Lasso",
                   "Minutos reales", "Minutos predichos")
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Efecto de alpha en Ridge y Lasso:**")
            alphas = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            efecto = []
            for a in alphas:
                for nombre_m, cls_m in [("Ridge", Ridge), ("Lasso", Lasso)]:
                    pm = Pipeline([
                        ("scaler", StandardScaler()),
                        ("model", cls_m(alpha=a, max_iter=10000)),
                    ])
                    pm.fit(Xtr, ytr)
                    s_cv = cross_val_score(pm, X, y, cv=5, scoring="r2")
                    efecto.append({
                        "alpha": a,
                        "Modelo": nombre_m,
                        "R2 CV": round(s_cv.mean(), 4),
                    })
            efecto_df = pd.DataFrame(efecto)
            fig2 = go.Figure()
            for nombre_m in ["Ridge", "Lasso"]:
                sub = efecto_df[efecto_df["Modelo"] == nombre_m]
                fig2.add_trace(go.Scatter(x=sub["alpha"], y=sub["R2 CV"],
                                          mode="lines+markers", name=nombre_m))
            estilo(fig2, "Efecto de alpha en R2 de validacion cruzada",
                   "Mayor alpha = mas regularizacion",
                   "Alpha", "R2 CV promedio")
            st.plotly_chart(fig2, width="stretch")
            st.markdown("**Conclusion:** Ridge mantiene todas las variables con "
                        "coeficientes reducidos; Lasso puede eliminar las menos "
                        "importantes. Un alpha muy alto sousa todos los modelos.")

        # ----------------------------------------------------------------
        # Tab 5: Feature importance
        # ----------------------------------------------------------------
        with tabs[4]:
            st.subheader("Importancia de variables (coeficientes)")
            st.caption("Analiza cuales variables tienen mayor influencia en la "
                       "prediccion del tiempo de entrega.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Coeficientes como importancia</div>
                <div class="info-box-text">En modelos lineales, el valor absoluto del
                coeficiente indica cuanta influencia tiene cada variable en la prediccion.
                Para comparar, las variables deben estar escaladas (ya se hace con StandardScaler).</div>
            </div>
            """, unsafe_allow_html=True)

            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

            pipe_fi = Pipeline([
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ])
            pipe_fi.fit(Xtr, ytr)
            coef_df = pd.DataFrame({
                "Variable": X.columns,
                "Coeficiente": pipe_fi.named_steps["model"].coef_,
                "Abs(Coef)": abs(pipe_fi.named_steps["model"].coef_),
            }).sort_values("Abs(Coef)", ascending=True)

            fig = go.Figure(go.Bar(
                y=coef_df["Variable"], x=coef_df["Coeficiente"],
                orientation="h",
                marker_color=["#059669" if v > 0 else "#EF4444"
                              for v in coef_df["Coeficiente"]],
                text=[f"{v:.2f}" for v in coef_df["Coeficiente"]],
                textposition="outside",
            ))
            estilo(fig, "Coeficientes del modelo (variables escaladas)",
                   "Positivo = sube el tiempo; Negativo = baja el tiempo",
                   "Coeficiente (efecto en minutos)", "", altura=300)
            st.plotly_chart(fig, width="stretch")

            st.divider()
            st.markdown("**Coeficientes con Ridge y Lasso:**")
            col_r, col_l = st.columns(2)
            for nombre_m, cls_m, col in [("Ridge", Ridge, col_r), ("Lasso", Lasso, col_l)]:
                pm = Pipeline([
                    ("scaler", StandardScaler()),
                    ("model", cls_m(alpha=1.0, max_iter=10000)),
                ])
                pm.fit(Xtr, ytr)
                coefs = pd.DataFrame({
                    "Variable": X.columns,
                    "Coeficiente": pm.named_steps["model"].coef_,
                }).sort_values("Coeficiente", ascending=True)
                with col:
                    st.markdown(f"**{nombre_m}**")
                    fig_c = go.Figure(go.Bar(
                        y=coefs["Variable"], x=coefs["Coeficiente"],
                        orientation="h",
                        marker_color=["#3B82F6" if v > 0 else "#F59E0B"
                                      for v in coefs["Coeficiente"]],
                        text=[f"{v:.2f}" for v in coefs["Coeficiente"]],
                        textposition="outside",
                    ))
                    fig_c.update_layout(template="plotly_white", height=250,
                                        margin=dict(l=120, r=30, t=10, b=40))
                    st.plotly_chart(fig_c, width="stretch")

            st.markdown("**Conclusion:** Los coeficientes mas grandes (en valor absoluto) "
                        "son las variables que mas influyen en el tiempo real de entrega. "
                        "Lasso puede reducir alguno a cero si no es relevante.")

    except ImportError:
        st.error("Falta instalar scikit-learn: pip install scikit-learn")
