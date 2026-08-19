import streamlit as st
import pandas as pd

from services import crud
from utils.forms import construir_opciones_fk, widget_campo


STATUS_COLORS = {
    "Activo": ("#059669", "#D1FAE5"),
    "Mantenimiento": ("#D97706", "#FEF3C7"),
    "Retirado": ("#DC2626", "#FEE2E2"),
    "Entregado": ("#059669", "#D1FAE5"),
    "Retrasado": ("#DC2626", "#FEE2E2"),
    "Cancelado": ("#6B7280", "#F3F4F6"),
    "Preventivo": ("#2563EB", "#DBEAFE"),
    "Correctivo": ("#DC2626", "#FEE2E2"),
}


def status_badge(texto):
    color, bg = STATUS_COLORS.get(str(texto), ("#6B7280", "#F3F4F6"))
    return (f'<span style="display:inline-block; background:{bg}; color:{color}; '
            f'font-size:0.75rem; font-weight:600; padding:0.2rem 0.6rem; '
            f'border-radius:999px; border:1px solid {color}20;">{texto}</span>')


def etiquetas_registro(df, selector):
    if callable(selector):
        return df.apply(selector, axis=1).astype(str)
    if isinstance(selector, str):
        return df[selector].astype(str)
    return df["id"].astype(str)


def buscar_dataframe(df, query, columnas=None):
    if not query or query.strip() == "":
        return df
    query = query.lower().strip()
    if columnas is None:
        columnas = df.columns.tolist()
    mascara = pd.Series([False] * len(df), index=df.index)
    for col in columnas:
        if col in df.columns:
            try:
                mascara |= df[col].astype(str).str.lower().str.contains(query, na=False)
            except Exception:
                pass
    return df[mascara]


def detectar_columnas_status(df):
    cols = []
    for c in df.columns:
        if c in ("estatus", "status", "estado"):
            cols.append(c)
    return cols


def modulo_crud(nombre_tabla, titulo, descripcion, campos, selector=None):
    st.markdown(f"<div class='modulo-header'><h1>{titulo}</h1><p>{descripcion}</p></div>",
                unsafe_allow_html=True)

    df = crud.leer_tabla(nombre_tabla)

    col_count, col_info = st.columns([1, 4])
    with col_count:
        st.metric("Registros", len(df))
    with col_info:
        st.caption(f"Registros actuales en la tabla de {titulo.lower()}.")

    if not df.empty:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            busqueda = st.text_input(
                "Buscar",
                placeholder=f"Buscar en {titulo.lower()}...",
                key=f"search_{nombre_tabla}",
                label_visibility="collapsed",
            )
        with filter_col:
            status_cols = detectar_columnas_status(df)
            filtro_status = None
            if status_cols:
                opciones_filtro = ["Todos"] + sorted(df[status_cols[0]].dropna().unique().tolist())
                filtro_status = st.selectbox(
                    "Filtrar por estatus",
                    opciones_filtro,
                    key=f"filter_{nombre_tabla}",
                    label_visibility="collapsed",
                )

        df_filtrado = df.copy()
        if busqueda:
            columnas_busqueda = [c for c in df.columns if c != "id"]
            df_filtrado = buscar_dataframe(df_filtrado, busqueda, columnas_busqueda)
        if filtro_status and filtro_status != "Todos" and status_cols:
            df_filtrado = df_filtrado[df_filtrado[status_cols[0]] == filtro_status]

        if busqueda or (filtro_status and filtro_status != "Todos"):
            st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} registros"
                       + (f' | Busqueda: "{busqueda}"' if busqueda else "")
                       + (f" | Estatus: {filtro_status}" if filtro_status and filtro_status != "Todos" else ""))

    st.dataframe(df, width="stretch", height=min(350, 40 + 35 * len(df)))
    st.divider()

    opciones_fk, tablas_vacias = construir_opciones_fk(campos)

    tab_agregar, tab_editar = st.tabs(["Agregar nuevo registro", "Editar o eliminar"])

    with tab_agregar:
        with st.form(f"form_add_{nombre_tabla}"):
            st.markdown("<div class='panel-titulo'>Agregar nuevo"
                        "<span>Completa los campos y presiona Guardar</span></div>",
                        unsafe_allow_html=True)
            if tablas_vacias:
                for config in tablas_vacias.values():
                    st.warning(f"Para elegir <<{config['etiqueta']}>> primero debes registrar "
                               f"datos en el modulo <<{config['tabla'].title()}>>.")
            else:
                valores = {}
                campos_lista = list(campos.items())
                for campo, config in campos_lista:
                    valores[campo] = widget_campo(campo, config, f"add_{nombre_tabla}",
                                                  opciones_fk=opciones_fk)
                enviado = st.form_submit_button("Guardar registro", type="primary", width="stretch")
                if enviado:
                    crud.insertar(nombre_tabla, valores)
                    st.toast(f"Registro guardado correctamente en {titulo}.")
                    st.rerun()

    with tab_editar:
        if df.empty:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-title">Sin registros</div>
                <div class="empty-state-text">Agrega el primer registro en la pestaña de agregar.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='panel-titulo' style='margin-bottom:1rem'>Selecciona un registro"
                        "<span>Modifica o elimina registros existentes</span></div>",
                        unsafe_allow_html=True)

            etiquetas = etiquetas_registro(df_filtrado if not df_filtrado.empty else df, selector)
            df_source = df_filtrado if not df_filtrado.empty else df
            parejas = list(zip(df_source["id"].astype(int).tolist(), etiquetas.tolist()))

            if not parejas:
                st.info("No se encontraron registros con los filtros aplicados.")
            else:
                sel = st.selectbox("Registro a editar", parejas,
                                   format_func=lambda p: f"#{p[0]} -- {p[1]}",
                                   key=f"sel_{nombre_tabla}")
                id_sel = sel[0]
                registro = df[df["id"] == id_sel].iloc[0]

                status_cols_edit = detectar_columnas_status(registro.to_frame().T)
                if status_cols_edit:
                    actual_status = registro[status_cols_edit[0]]
                    badge_html = status_badge(actual_status)
                    st.markdown(f"Estado actual: {badge_html}", unsafe_allow_html=True)
                    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

                with st.form(f"form_edit_{nombre_tabla}"):
                    nuevos = {}
                    for campo, config in campos.items():
                        nuevos[campo] = widget_campo(
                            campo, config, f"edit_{id_sel}_{nombre_tabla}",
                            valor_actual=registro[campo], opciones_fk=opciones_fk,
                        )
                    col_a, col_b = st.columns(2)
                    actualizar_btn = col_a.form_submit_button("Actualizar registro", type="primary",
                                                              width="stretch")
                    eliminar_btn = col_b.form_submit_button("Eliminar registro", width="stretch")
                    confirmar_eliminar = st.checkbox("Confirmo que quiero eliminar este registro",
                                                     key=f"conf_elim_{nombre_tabla}")
                    if actualizar_btn:
                        crud.actualizar(nombre_tabla, id_sel, nuevos)
                        st.toast("Registro actualizado correctamente.")
                        st.rerun()
                    if eliminar_btn:
                        if confirmar_eliminar:
                            crud.eliminar(nombre_tabla, id_sel)
                            st.toast("Registro eliminado.")
                            st.rerun()
                        else:
                            st.error("Marca la casilla de confirmacion para poder eliminar.")
