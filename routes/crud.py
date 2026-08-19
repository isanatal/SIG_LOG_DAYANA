import streamlit as st

from services import crud
from utils.ui import modulo_crud, status_badge
from models.schemas import (
    CAMPOS_CLIENTES, CAMPOS_VEHICULOS, CAMPOS_OPERADORES,
    CAMPOS_RUTAS, CAMPOS_ENTREGAS, CAMPOS_COMBUSTIBLE, CAMPOS_MANTENIMIENTO,
)


def indicadores_modulo(nombre_tabla):
    try:
        df = crud.leer_tabla(nombre_tabla)
    except Exception:
        return

    if df.empty:
        return

    if nombre_tabla == "vehiculos":
        total = len(df)
        activos = (df["estatus"] == "Activo").sum()
        mantenimiento = (df["estatus"] == "Mantenimiento").sum()
        pct_activos = activos / total * 100 if total else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total unidades", total)
        c2.metric("Activas", f"{activos} ({pct_activos:.0f}%)")
        c3.metric("En mantenimiento", mantenimiento)

        if total > 0:
            st.markdown(f"""
            <div class="progress-bar-container">
                <div class="progress-bar-fill{" warning" if pct_activos < 80 else ""}"
                     style="width: {pct_activos}%;"></div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Disponibilidad de la flota: {pct_activos:.0f}%")
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    elif nombre_tabla == "entregas":
        total = len(df)
        if total > 0:
            entregadas = (df["estatus"] == "Entregado").sum()
            retrasadas = (df["estatus"] == "Retrasado").sum()
            canceladas = (df["estatus"] == "Cancelado").sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", total)
            c2.metric("Entregadas", entregadas)
            c3.metric("Retrasadas", retrasadas)
            c4.metric("Canceladas", canceladas)

            if "minutos_reales" in df.columns:
                validas = df.dropna(subset=["minutos_reales"])
                if not validas.empty:
                    promedio = validas["minutos_reales"].mean()
                    st.metric("Tiempo promedio real", f"{promedio:.0f} min")

            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    elif nombre_tabla == "combustible":
        if "costo" in df.columns:
            total_costo = df["costo"].sum()
            promedio = df["costo"].mean()
            c1, c2 = st.columns(2)
            c1.metric("Costo total", f"${total_costo:,.0f}")
            c2.metric("Costo promedio por carga", f"${promedio:,.0f}")
            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    elif nombre_tabla == "mantenimiento":
        if "costo" in df.columns:
            total_costo = df["costo"].sum()
            tipos = df["tipo"].value_counts()
            c1, c2, c3 = st.columns(3)
            c1.metric("Costo total", f"${total_costo:,.0f}")
            c2.metric("Preventivos", tipos.get("Preventivo", 0))
            c3.metric("Correctivos", tipos.get("Correctivo", 0))
            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    elif nombre_tabla == "clientes":
        c1, c2 = st.columns(2)
        c1.metric("Total clientes", len(df))
        if "direccion" in df.columns:
            ciudades = df["direccion"].dropna().nunique()
            c2.metric("Ciudades", ciudades)
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    elif nombre_tabla == "rutas":
        c1, c2 = st.columns(2)
        c1.metric("Total rutas", len(df))
        if "distancia_km" in df.columns:
            dist_prom = df["distancia_km"].mean()
            c2.metric("Distancia promedio", f"{dist_prom:.0f} km")
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)


def render(opcion):
    modulos_config = {
        "Clientes": ("clientes", "Clientes",
                     "Registra y administra a los clientes de la empresa y sus datos de contacto.",
                     CAMPOS_CLIENTES, "nombre"),
        "Vehiculos": ("vehiculos", "Vehiculos",
                      "Administra la flota: placas, modelo, capacidad y estatus de cada unidad.",
                      CAMPOS_VEHICULOS, "placas"),
        "Operadores": ("operadores", "Operadores",
                       "Da de alta a los operadores que conducen las unidades.",
                       CAMPOS_OPERADORES, "nombre"),
        "Rutas": ("rutas", "Rutas",
                  "Define las rutas de la empresa con origen, destino y distancia.",
                  CAMPOS_RUTAS, lambda r: f"{r['origen']} -> {r['destino']}"),
        "Entregas": ("entregas", "Entregas",
                     "Registra cada entrega: cliente, vehiculo, operador, ruta y tiempos.",
                     CAMPOS_ENTREGAS, lambda r: f"{r['fecha']} | {r['estatus']}"),
        "Combustible": ("combustible", "Combustible",
                        "Lleva el control de litros y costos de combustible por vehiculo.",
                        CAMPOS_COMBUSTIBLE, "vehiculo_id"),
        "Mantenimiento": ("mantenimiento", "Mantenimiento",
                          "Controla los servicios y costos de mantenimiento de cada vehiculo.",
                          CAMPOS_MANTENIMIENTO, "vehiculo_id"),
    }

    config = modulos_config.get(opcion)
    if not config:
        return

    nombre_tabla, titulo, descripcion, campos, selector = config

    indicadores_modulo(nombre_tabla)
    modulo_crud(nombre_tabla, titulo, descripcion, campos, selector=selector)
