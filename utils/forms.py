from datetime import date, time

import pandas as pd
import streamlit as st

from services import crud


def es_vacio(valor):
    if valor is None:
        return True
    try:
        return bool(pd.isna(valor)) or str(valor).strip() == ""
    except (TypeError, ValueError):
        return False


def campo_fk(tabla, etiqueta, ayuda, formato=None, label_col=None):
    return {"tipo": "fk", "tabla": tabla, "etiqueta": etiqueta, "ayuda": ayuda,
            "formato": formato, "label_col": label_col}


def construir_opciones_fk(campos):
    opciones, vacias = {}, {}
    for campo, config in campos.items():
        if config.get("tipo") != "fk":
            continue
        ref = crud.leer_tabla(config["tabla"])
        if ref.empty:
            vacias[campo] = config
            continue
        if config.get("formato"):
            etiquetas = ref.apply(config["formato"], axis=1).astype(str)
        elif config.get("label_col"):
            etiquetas = ref[config["label_col"]].astype(str)
        else:
            etiquetas = ref["id"].astype(str)
        opciones[campo] = list(zip(etiquetas.tolist(), ref["id"].astype(int).tolist()))
    return opciones, vacias


def widget_campo(campo, config, prefijo, valor_actual=None, opciones_fk=None):
    tipo = config.get("tipo", "text")
    etiqueta = config.get("etiqueta", campo.replace("_", " ").title())
    ayuda = config.get("ayuda", "")
    clave = f"{prefijo}_{campo}"

    if tipo == "number":
        valor = st.number_input(etiqueta, value=float(valor_actual) if not es_vacio(valor_actual) else 0.0,
                                step=1.0, key=clave)
        if config.get("permite_vacio") and float(valor) == 0:
            valor = None

    elif tipo == "date":
        inicial = date.today() if es_vacio(valor_actual) else pd.to_datetime(valor_actual).date()
        valor = str(st.date_input(etiqueta, value=inicial, key=clave))

    elif tipo == "time":
        inicial = time(8, 0) if es_vacio(valor_actual) else pd.to_datetime(valor_actual).time()
        valor = str(st.time_input(etiqueta, value=inicial, key=clave))

    elif tipo == "select":
        opciones = list(config["opciones"])
        idx = opciones.index(valor_actual) if (not es_vacio(valor_actual) and valor_actual in opciones) else 0
        valor = st.selectbox(etiqueta, opciones, index=idx, key=clave)

    elif tipo == "fk":
        pares = opciones_fk.get(campo, [])
        if not pares:
            st.warning(f"No hay opciones disponibles para <<{etiqueta}>>.")
            return None
        etiquetas = [p[0] for p in pares]
        ids = [p[1] for p in pares]
        idx = ids.index(valor_actual) if (not es_vacio(valor_actual) and valor_actual in ids) else 0
        seleccion = st.selectbox(etiqueta, etiquetas, index=idx, key=clave)
        valor = ids[etiquetas.index(seleccion)]

    else:
        valor = st.text_input(etiqueta, value=str(valor_actual or ""), key=clave)

    if ayuda:
        st.caption(ayuda)
    return valor
