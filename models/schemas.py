from utils.forms import campo_fk

CAMPOS_CLIENTES = {
    "nombre": {"tipo": "text", "etiqueta": "Nombre", "ayuda": "Ej. Grupo Alfa"},
    "contacto": {"tipo": "text", "etiqueta": "Contacto", "ayuda": "Telefono o persona de contacto"},
    "direccion": {"tipo": "text", "etiqueta": "Direccion", "ayuda": "Calle, numero y ciudad"},
}

CAMPOS_VEHICULOS = {
    "placas": {"tipo": "text", "etiqueta": "Placas", "ayuda": "Ej. TOL-101-A"},
    "modelo": {"tipo": "text", "etiqueta": "Modelo", "ayuda": "Ej. Nissan NP300"},
    "capacidad_kg": {"tipo": "number", "etiqueta": "Capacidad (kg)", "ayuda": "Peso maximo de carga"},
    "estatus": {"tipo": "select", "opciones": ["Activo", "Mantenimiento", "Retirado"],
                "etiqueta": "Estatus", "ayuda": "Estado actual del vehiculo"},
}

CAMPOS_OPERADORES = {
    "nombre": {"tipo": "text", "etiqueta": "Nombre", "ayuda": "Nombre completo del operador"},
    "licencia": {"tipo": "text", "etiqueta": "Licencia", "ayuda": "Numero de licencia"},
    "telefono": {"tipo": "text", "etiqueta": "Telefono", "ayuda": "Ej. 722-111-0001"},
}

CAMPOS_RUTAS = {
    "origen": {"tipo": "text", "etiqueta": "Origen", "ayuda": "Ciudad de salida"},
    "destino": {"tipo": "text", "etiqueta": "Destino", "ayuda": "Ciudad de llegada"},
    "distancia_km": {"tipo": "number", "etiqueta": "Distancia (km)", "ayuda": "Kilometros de la ruta"},
}

CAMPOS_ENTREGAS = {
    "cliente_id": campo_fk("clientes", "Cliente", "Quien recibe la entrega", label_col="nombre"),
    "vehiculo_id": campo_fk("vehiculos", "Vehiculo", "Unidad que realiza la entrega",
                            formato=lambda r: f"{r['placas']} \u00b7 {r['modelo']}"),
    "operador_id": campo_fk("operadores", "Operador", "Quien conduce la unidad", label_col="nombre"),
    "ruta_id": campo_fk("rutas", "Ruta", "Origen y destino",
                        formato=lambda r: f"{r['origen']} \u2192 {r['destino']}"),
    "fecha": {"tipo": "date", "etiqueta": "Fecha", "ayuda": "Dia de la entrega"},
    "hora_salida": {"tipo": "time", "etiqueta": "Hora de salida", "ayuda": "Hora en que salio la unidad"},
    "minutos_estimados": {"tipo": "number", "etiqueta": "Minutos estimados",
                          "ayuda": "Tiempo previsto de la entrega"},
    "minutos_reales": {"tipo": "number", "etiqueta": "Minutos reales",
                       "ayuda": "Tiempo real (dejalo en 0 si la entrega se cancelo)",
                       "permite_vacio": True},
    "estatus": {"tipo": "select", "opciones": ["Entregado", "Retrasado", "Cancelado"],
                "etiqueta": "Estatus", "ayuda": "Como termino la entrega"},
}

CAMPOS_COMBUSTIBLE = {
    "vehiculo_id": campo_fk("vehiculos", "Vehiculo", "Unidad que cargo combustible",
                            formato=lambda r: f"{r['placas']} \u00b7 {r['modelo']}"),
    "fecha": {"tipo": "date", "etiqueta": "Fecha", "ayuda": "Dia de la carga"},
    "litros": {"tipo": "number", "etiqueta": "Litros", "ayuda": "Combustible cargado"},
    "costo": {"tipo": "number", "etiqueta": "Costo ($)", "ayuda": "Costo total en pesos"},
    "km_recorridos": {"tipo": "number", "etiqueta": "Km recorridos",
                      "ayuda": "Kilometros recorridos en ese periodo"},
}

CAMPOS_MANTENIMIENTO = {
    "vehiculo_id": campo_fk("vehiculos", "Vehiculo", "Unidad a la que se le da servicio",
                            formato=lambda r: f"{r['placas']} \u00b7 {r['modelo']}"),
    "fecha": {"tipo": "date", "etiqueta": "Fecha", "ayuda": "Dia del servicio"},
    "tipo": {"tipo": "select", "opciones": ["Preventivo", "Correctivo"],
             "etiqueta": "Tipo", "ayuda": "Preventivo = rutina; Correctivo = reparacion"},
    "costo": {"tipo": "number", "etiqueta": "Costo ($)", "ayuda": "Costo del servicio"},
    "descripcion": {"tipo": "text", "etiqueta": "Descripcion", "ayuda": "Detalle del trabajo realizado"},
}
