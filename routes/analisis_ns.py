import pandas as pd
import streamlit as st

from services import crud


def render():
    st.markdown("<div class='modulo-header'><h1>Analisis no supervisado</h1>"
                "<p>Clustering expandido: DBSCAN, jerarquico, Gaussian Mixture "
                "y t-SNE para visualizacion.</p></div>",
                unsafe_allow_html=True)

    import plotly.graph_objects as go

    entregas = crud.leer_tabla("entregas")
    rutas = crud.leer_tabla("rutas")

    tabs = st.tabs([
        "1. K-Means (codo + silueta)",
        "2. DBSCAN",
        "3. Clustering jerarquico",
        "4. Gaussian Mixture Models",
        "5. t-SNE (visualizacion)",
        "6. Metricas de calidad",
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
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        from sklearn.mixture import GaussianMixture
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import (silhouette_score, calinski_harabasz_score,
                                     davies_bouldin_score)

        resumen = entregas.merge(rutas, left_on="ruta_id", right_on="id",
                                 suffixes=("", "_ruta"))
        resumen = resumen.groupby("ruta_id").agg(
            distancia_km=("distancia_km", "first"),
            num_entregas=("id", "count"),
            retraso_prom=("retraso_min", "mean") if "retraso_min" in resumen.columns
            else ("minutos_reales", "mean"),
        ).reset_index()

        if "retraso_prom" not in resumen.columns:
            resumen["retraso_prom"] = 0

        if len(resumen) < 4:
            st.warning("Se necesitan al menos 4 rutas con entregas para hacer "
                       "analisis no supervisado.")
            return

        X = resumen[["distancia_km", "num_entregas"]].copy()
        if "retraso_prom" in resumen.columns:
            X["retraso_prom"] = resumen["retraso_prom"]
        X_esc = StandardScaler().fit_transform(X)

        pca = PCA(n_components=2)
        comp = pca.fit_transform(X_esc)
        resumen["pca_1"] = comp[:, 0]
        resumen["pca_2"] = comp[:, 1]

        # ----------------------------------------------------------------
        # Tab 1: K-Means
        # ----------------------------------------------------------------
        with tabs[0]:
            st.subheader("K-Means: metodo del codo e indice de silueta")
            st.caption("Determina el numero optimo de clusters y visualiza la agrupacion.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">K-Means</div>
                <div class="info-box-text">Divide los datos en K grupos minimizando
                la distancia de cada punto al centro de su grupo. El metodo del codo
                y la silueta ayudan a elegir el K optimal.</div>
            </div>
            """, unsafe_allow_html=True)

            max_k = min(7, len(resumen))
            rango_k = list(range(1, max_k + 1))
            inercias = []
            siluetas = []
            for k in rango_k:
                km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_esc)
                inercias.append(km.inertia_)
                if k >= 2:
                    siluetas.append(silhouette_score(X_esc, km.labels_))
                else:
                    siluetas.append(0)

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                fig_codo = go.Figure(go.Scatter(
                    x=rango_k, y=inercias, mode="lines+markers",
                    line=dict(color="#059669", width=2.5), marker=dict(size=8)))
                estilo(fig_codo, "Metodo del codo", "Inercia vs numero de clusters",
                       "K", "Inercia", altura=350)
                st.plotly_chart(fig_codo, width="stretch")
            with col_c2:
                fig_sil = go.Figure(go.Scatter(
                    x=rango_k, y=siluetas, mode="lines+markers",
                    line=dict(color="#8B5CF6", width=2.5), marker=dict(size=8)))
                estilo(fig_sil, "Indice de silueta", "Mayor = mejor separacion",
                       "K", "Silueta", altura=350)
                st.plotly_chart(fig_sil, width="stretch")

            mejor_k = rango_k[int(pd.Series(siluetas[1:]).idxmax()) + 1] if len(siluetas) > 1 else 2
            n_clusters = st.slider("Numero de clusters", 2, max_k, mejor_k, key="kmeans_k")

            km_final = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
            resumen["grupo_km"] = km_final.fit_predict(X_esc)
            sil_final = silhouette_score(X_esc, resumen["grupo_km"])

            m1, m2, m3 = st.columns(3)
            m1.metric("Clusters", n_clusters)
            m2.metric("Silueta", f"{sil_final:.3f}")
            m3.metric("Rutas", len(resumen))

            fig_pca = go.Figure()
            for g in sorted(resumen["grupo_km"].unique()):
                sub = resumen[resumen["grupo_km"] == g]
                fig_pca.add_trace(go.Scatter(
                    x=sub["pca_1"], y=sub["pca_2"], mode="markers",
                    name=f"Grupo {g}",
                    marker=dict(size=10, color=PALETA[g % len(PALETA)],
                                opacity=0.8, line=dict(width=1, color="white")),
                    text=sub["distancia_km"].apply(lambda x: f"{x:.0f} km"),
                    hovertemplate="PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<br>%{text}<extra></extra>",
                ))
            estilo(fig_pca, f"K-Means: {n_clusters} grupos (PCA)",
                   f"Silueta={sil_final:.3f} | {pca.explained_variance_ratio_.sum():.1%} varianza explicada",
                   "Componente 1", "Componente 2")
            st.plotly_chart(fig_pca, width="stretch")
            st.dataframe(resumen[["distancia_km", "num_entregas", "grupo_km"]],
                         width="stretch", hide_index=True)

        # ----------------------------------------------------------------
        # Tab 2: DBSCAN
        # ----------------------------------------------------------------
        with tabs[1]:
            st.subheader("DBSCAN: clustering basado en densidad")
            st.caption("Encuentra grupos de forma automatica sin definir K. "
                       "Los puntos ruidosos se marcan como -1 (ruido).")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">DBSCAN</div>
                <div class="info-box-text">Agrupa puntos que estan cercanos entre si
                (alta densidad) y marca como ruido los que estan aislados. No necesita
                definir K, pero si eps (distancia maxima) y min_samples.</div>
            </div>
            """, unsafe_allow_html=True)

            eps_val = st.slider("eps (distancia maxima)", 0.1, 3.0, 0.8, step=0.05, key="eps")
            min_samp = st.slider("min_samples (puntos minimos por grupo)", 2, 10, 3,
                                 key="min_samp")

            db = DBSCAN(eps=eps_val, min_samples=min_samp)
            resumen["grupo_db"] = db.fit_predict(X_esc)

            n_ruidosos = (resumen["grupo_db"] == -1).sum()
            n_grupos = len(set(resumen["grupo_db"])) - (1 if -1 in resumen["grupo_db"].values else 0)

            m1, m2, m3 = st.columns(3)
            m1.metric("Grupos encontrados", n_grupos)
            m2.metric("Puntos de ruido", n_ruidosos)
            m3.metric("Rutas totales", len(resumen))

            fig_db = go.Figure()
            for g in sorted(resumen["grupo_db"].unique()):
                sub = resumen[resumen["grupo_db"] == g]
                nombre = "Ruido" if g == -1 else f"Grupo {g}"
                color = "#9CA3AF" if g == -1 else PALETA[g % len(PALETA)]
                fig_db.add_trace(go.Scatter(
                    x=sub["pca_1"], y=sub["pca_2"], mode="markers",
                    name=nombre,
                    marker=dict(size=10, color=color, opacity=0.7,
                                symbol="x" if g == -1 else "circle",
                                line=dict(width=1, color="white")),
                    hovertemplate="PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<extra></extra>",
                ))
            estilo(fig_db, f"DBSCAN: eps={eps_val}, min_samples={min_samp}",
                   f"{n_grupos} grupos | {n_ruidosos} puntos ruidosos",
                   "Componente 1", "Componente 2")
            st.plotly_chart(fig_db, width="stretch")

            if n_ruidosos > 0:
                st.markdown("**Rutas clasificadas como ruido:**")
                st.dataframe(resumen[resumen["grupo_db"] == -1][
                    ["distancia_km", "num_entregas"]], width="stretch", hide_index=True)
            st.markdown("**Conclusion:** DBSCAN es ideal cuando los grupos no tienen "
                        "forma esferica o cuando hay ruido. Ajustar eps y min_samples "
                        "cambia la sensibilidad del algoritmo.")

        # ----------------------------------------------------------------
        # Tab 3: Clustering jerarquico
        # ----------------------------------------------------------------
        with tabs[2]:
            st.subheader("Clustering jerarquico (Agglomerative)")
            st.caption("Construye los grupos de abajo hacia arriba, fusionando "
                       "los mas similares en cada paso.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Clustering jerarquico</div>
                <div class="info-box-text">Comienza con cada punto como su propio grupo
                y va fusionando los mas cercanos hasta formar un solo grupo. El dendrograma
                muestra este proceso de fusion.</div>
            </div>
            """, unsafe_allow_html=True)

            linkage = st.selectbox("Tipo de enlace (linkage)",
                                   ["ward", "complete", "average", "single"],
                                   key="linkage")

            n_clust_j = st.slider("Numero de clusters", 2, min(6, len(resumen)),
                                  3, key="n_clust_jer")

            agg = AgglomerativeClustering(n_clusters=n_clust_j, linkage=linkage)
            resumen["grupo_jer"] = agg.fit_predict(X_esc)
            sil_jer = silhouette_score(X_esc, resumen["grupo_jer"])

            m1, m2, m3 = st.columns(3)
            m1.metric("Clusters", n_clust_j)
            m2.metric("Silueta", f"{sil_jer:.3f}")
            m3.metric("Linkage", linkage)

            fig_jer = go.Figure()
            for g in sorted(resumen["grupo_jer"].unique()):
                sub = resumen[resumen["grupo_jer"] == g]
                fig_jer.add_trace(go.Scatter(
                    x=sub["pca_1"], y=sub["pca_2"], mode="markers",
                    name=f"Grupo {g}",
                    marker=dict(size=10, color=PALETA[g % len(PALETA)],
                                opacity=0.8, line=dict(width=1, color="white")),
                ))
            estilo(fig_jer, f"Clustering jerarquico ({linkage})",
                   f"Silueta={sil_jer:.3f}",
                   "Componente 1", "Componente 2")
            st.plotly_chart(fig_jer, width="stretch")

            st.divider()
            st.markdown("**Dendrograma (simplificado):**")
            st.caption("Muestra como se van fusionando los grupos. Cortar la "
                       "linea vertical mas larga sugiere el numero de clusters.")

            try:
                from scipy.cluster.hierarchy import dendrogram, linkage as scipy_linkage
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                import numpy as np

                Z = scipy_linkage(X_esc, method=linkage)
                fig_dend, ax = plt.subplots(figsize=(10, 4))
                dendrogram(Z, labels=resumen["distancia_km"].apply(
                    lambda x: f"{x:.0f}km").values, ax=ax,
                    leaf_rotation=45, leaf_font_size=8)
                ax.set_title(f"Dendrograma ({linkage})", fontsize=13, color="#064E3B")
                ax.set_xlabel("Ruta (distancia km)")
                ax.set_ylabel("Distancia de fusion")
                plt.tight_layout()
                st.pyplot(fig_dend)
                plt.close(fig_dend)
            except ImportError:
                st.info("Para ver el dendrograma completa instala scipy: pip install scipy")

            st.markdown("**Conclusion:** El clustering jerarquico no requiere "
                        "definir K de antemano. El dendrograma revela la estructura "
                        "natural de los datos. Ward minimiza la varianza dentro de "
                        "cada grupo y suele producir clusters mas compactos.")

        # ----------------------------------------------------------------
        # Tab 4: Gaussian Mixture Models
        # ----------------------------------------------------------------
        with tabs[3]:
            st.subheader("Gaussian Mixture Models (GMM)")
            st.caption("Asigna probabilidades de pertenencia a cada cluster, "
                       "en vez de una asignacion rigida como K-Means.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">GMM</div>
                <div class="info-box-text">Asume que los datos son una mezcla de
                distribuciones gaussianas. Cada punto tiene una probabilidad de
                pertenecer a cada grupo, lo que permite clasificaciones suaves.</div>
            </div>
            """, unsafe_allow_html=True)

            n_gmm = st.slider("Numero de componentes", 2, min(6, len(resumen)),
                              3, key="n_gmm")

            gmm = GaussianMixture(n_components=n_gmm, random_state=42)
            resumen["grupo_gmm"] = gmm.fit_predict(X_esc)
            probs = gmm.predict_proba(X_esc)
            resumen["prob_max"] = probs.max(axis=1)

            sil_gmm = silhouette_score(X_esc, resumen["grupo_gmm"])
            m1, m2, m3 = st.columns(3)
            m1.metric("Componentes", n_gmm)
            m2.metric("Silueta", f"{sil_gmm:.3f}")
            m3.metric("Prob. promedio", f"{resumen['prob_max'].mean():.2f}")

            fig_gmm = go.Figure()
            for g in sorted(resumen["grupo_gmm"].unique()):
                sub = resumen[resumen["grupo_gmm"] == g]
                fig_gmm.add_trace(go.Scatter(
                    x=sub["pca_1"], y=sub["pca_2"], mode="markers",
                    name=f"Grupo {g}",
                    marker=dict(size=10, color=PALETA[g % len(PALETA)],
                                opacity=0.8, line=dict(width=1, color="white")),
                    text=sub.apply(lambda r: f"Grupo {r['grupo_gmm']}<br>"
                                   f"Prob: {r['prob_max']:.2f}", axis=1),
                    hovertemplate="%{text}<br>PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<extra></extra>",
                ))
            estilo(fig_gmm, f"GMM: {n_gmm} componentes",
                   f"Silueta={sil_gmm:.3f} | Probabilidad promedio={resumen['prob_max'].mean():.2f}",
                   "Componente 1", "Componente 2")
            st.plotly_chart(fig_gmm, width="stretch")

            st.divider()
            st.markdown("**Distribucion de probabilidades por grupo:**")
            fig_prob = go.Figure()
            for g in sorted(resumen["grupo_gmm"].unique()):
                sub = resumen[resumen["grupo_gmm"] == g]
                fig_prob.add_trace(go.Box(y=sub["prob_max"], name=f"Grupo {g}",
                                          marker_color=PALETA[g % len(PALETA)]))
            estilo(fig_prob, "Confianza de asignacion por grupo",
                   "Cerca de 1.0 = alta certeza; cerca de 0.5 = ambiguedad",
                   "", "Probabilidad maxima", altura=350)
            st.plotly_chart(fig_prob, width="stretch")
            st.markdown("**Conclusion:** GMM es ideal cuando los clusters se "
                        "solapan. Las probabilidades indican que tan seguro esta "
                        "el modelo de la asignacion de cada ruta.")

        # ----------------------------------------------------------------
        # Tab 5: t-SNE
        # ----------------------------------------------------------------
        with tabs[4]:
            st.subheader("t-SNE: visualizacion no lineal")
            st.caption("Reduce los datos a 2 dimensiones preservando las relaciones "
                       "de vecindad. Excelente para ver la estructura real.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">t-SNE</div>
                <div class="info-box-text">A diferencia de PCA (lineal), t-SNE es una
                tecnica no lineal que preserva las relaciones locales: puntos cercanos
                en el espacio original permanecen cercanos en 2D. Ideal para visualizar
                estructura de clusters.</div>
            </div>
            """, unsafe_allow_html=True)

            perplexity = st.slider("Perplexity (vecindad)", 3, min(30, len(resumen) - 1),
                                   5, key="perplexity")
            tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42,
                        n_iter=1000)
            comp_tsne = tsne.fit_transform(X_esc)
            resumen["tsne_1"] = comp_tsne[:, 0]
            resumen["tsne_2"] = comp_tsne[:, 1]

            color_by = st.selectbox("Colorear por",
                                    ["K-Means", "DBSCAN", "Jerarquico", "GMM", "Distancia"],
                                    key="tsne_color")

            color_map = {
                "K-Means": "grupo_km",
                "DBSCAN": "grupo_db",
                "Jerarquico": "grupo_jer",
                "GMM": "grupo_gmm",
                "Distancia": "distancia_km",
            }
            col_col = color_map[color_by]

            fig_tsne = go.Figure()
            if color_by == "Distancia":
                fig_tsne.add_trace(go.Scatter(
                    x=resumen["tsne_1"], y=resumen["tsne_2"], mode="markers",
                    marker=dict(size=10, color=resumen[col_col],
                                colorscale="Viridis", opacity=0.8,
                                line=dict(width=1, color="white"),
                                colorbar=dict(title="km")),
                    text=resumen["distancia_km"].apply(lambda x: f"{x:.0f} km"),
                    hovertemplate="t-SNE1: %{x:.2f}<br>t-SNE2: %{y:.2f}<br>%{text}<extra></extra>",
                ))
            else:
                for g in sorted(resumen[col_col].unique()):
                    sub = resumen[resumen[col_col] == g]
                    nombre = "Ruido" if g == -1 else f"Grupo {g}"
                    color = "#9CA3AF" if g == -1 else PALETA[g % len(PALETA)]
                    fig_tsne.add_trace(go.Scatter(
                        x=sub["tsne_1"], y=sub["tsne_2"], mode="markers",
                        name=nombre,
                        marker=dict(size=10, color=color, opacity=0.8,
                                    symbol="x" if g == -1 else "circle",
                                    line=dict(width=1, color="white")),
                    ))
            estilo(fig_tsne, f"t-SNE: estructura de los datos (perplexity={perplexity})",
                   f"Coloreado por: {color_by}",
                   "t-SNE componente 1", "t-SNE componente 2")
            st.plotly_chart(fig_tsne, width="stretch")

            st.divider()
            st.markdown("**Comparacion PCA vs t-SNE:**")
            comp_cols = st.columns(2)
            with comp_cols[0]:
                fig_pca2 = go.Figure(go.Scatter(
                    x=resumen["pca_1"], y=resumen["pca_2"], mode="markers",
                    marker=dict(size=8, color=resumen["grupo_km"],
                                colorscale="Viridis", opacity=0.7)))
                estilo(fig_pca2, "PCA", "Reduccion lineal",
                       "PC1", "PC2", altura=300)
                st.plotly_chart(fig_pca2, width="stretch")
            with comp_cols[1]:
                fig_tsne2 = go.Figure(go.Scatter(
                    x=resumen["tsne_1"], y=resumen["tsne_2"], mode="markers",
                    marker=dict(size=8, color=resumen["grupo_km"],
                                colorscale="Viridis", opacity=0.7)))
                estilo(fig_tsne2, "t-SNE", "Reduccion no lineal",
                       "t-SNE1", "t-SNE2", altura=300)
                st.plotly_chart(fig_tsne2, width="stretch")

            st.markdown("**Conclusion:** t-SNE revela la estructura real de los "
                        "grupos mejor que PCA, pero es mas costoso computacionalmente "
                        "y no es reproducible al 100% entre corridas.")

        # ----------------------------------------------------------------
        # Tab 6: Metricas de calidad
        # ----------------------------------------------------------------
        with tabs[5]:
            st.subheader("Metricas de calidad de clusters")
            st.caption("Compara diferentes algoritmos con metricas objetivas "
                       "para elegir el mejor.")

            st.markdown("""
            <div class="info-box" style="margin-bottom:1rem;">
                <div class="info-box-title">Metricas de evaluacion</div>
                <div class="info-box-text">Como no hay variables objetivo, se usan
                metricas internas: cohesion (cuan compactos), separacion (cuan alejados)
                y silueta (balance de ambos).</div>
            </div>
            """, unsafe_allow_html=True)

            n_comp = st.selectbox("Numero de clusters para comparar", [2, 3, 4, 5],
                                  index=1, key="n_comp_cal")

            algoritmos = {}
            km_c = KMeans(n_clusters=n_comp, n_init=10, random_state=42)
            algoritmos["K-Means"] = km_c.fit_predict(X_esc)

            agg_c = AgglomerativeClustering(n_clusters=n_comp, linkage="ward")
            algoritmos["Jerarquico"] = agg_c.fit_predict(X_esc)

            gmm_c = GaussianMixture(n_components=n_comp, random_state=42)
            algoritmos["GMM"] = gmm_c.fit_predict(X_esc)

            db_c = DBSCAN(eps=0.8, min_samples=3).fit_predict(X_esc)
            if len(set(db_c)) > 1 and -1 not in db_c:
                algoritmos["DBSCAN"] = db_c

            metricas = []
            for nombre, labels in algoritmos.items():
                sil = silhouette_score(X_esc, labels)
                ch = calinski_harabasz_score(X_esc, labels)
                db_score = davies_bouldin_score(X_esc, labels)
                metricas.append({
                    "Algoritmo": nombre,
                    "Silueta": round(sil, 4),
                    "Calinski-Harabasz": round(ch, 1),
                    "Davies-Bouldin": round(db_score, 3),
                })

            met_df = pd.DataFrame(metricas).sort_values("Silueta", ascending=False)
            st.dataframe(met_df, width="stretch", hide_index=True)

            st.divider()
            st.markdown("""
            | Metrica | Que mide | Mejor valor |
            |---|---|---|
            | **Silueta** (-1 a 1) | Cohesion y separacion | Mas alto |
            | **Calinski-Harabasz** (>=0) | Ratio varianza entre/dentro clusters | Mas alto |
            | **Davies-Bouldin** (>=0) | Similitud entre clusters | Mas bajo |
            """)

            mejor = met_df.iloc[0]["Algoritmo"]
            st.success(f"**Mejor algoritmo por silueta:** {mejor}")

            st.divider()
            st.markdown("**Resumen:**")
            st.markdown("""
            | Algoritmo | Ventaja | Desventaja |
            |---|---|---|
            | **K-Means** | Rapido, escalable | Requiere definir K, asume clusters esfericos |
            | **DBSCAN** | Detecta ruido, formas arbitrarias | Sensible a eps y min_samples |
            | **Jerarquico** | Dendrograma visual, no necesita K fijo | Costoso con muchos datos |
            | **GMM** | Probabilidades suaves, clusters elipticos | Puede converger a local optimum |
            """)

    except ImportError:
        st.error("Falta instalar scikit-learn: pip install scikit-learn")
