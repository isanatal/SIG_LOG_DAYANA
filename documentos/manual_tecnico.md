# Manual Tecnico -- SIG-LOG

## 1. Descripcion general

SIG-LOG es una aplicacion web construida con:

| Tecnologia | Version | Funcion |
|---|---|---|
| Python | 3.10+ | Lenguaje de programacion |
| Streamlit | >= 1.32 | Interfaz de usuario web |
| SQLite | (incluido en Python) | Base de datos relacional |
| pandas | >= 2.0 | Manipulacion y analisis de datos |
| scikit-learn | >= 1.3 | Modelos de machine learning |
| Plotly | >= 5.24 | Graficas interactivas |
| numpy | >= 1.24 | Operaciones numericas |

---

## 2. Arquitectura del proyecto

```
sig_log/
├── app.py                    # Punto de entrada: sidebar, routing entre modulos
├── database.py               # Creacion de tablas SQLite y datos de ejemplo
├── requirements.txt          # Dependencias de Python
├── .streamlit/
│   └── config.toml           # Configuracion de Streamlit
├── data/
│   └── sig_log.db            # Base de datos (se genera automaticamente)
├── docs/
│   ├── manual_usuario.md     # Manual de usuario
│   └── manual_tecnico.md     # Este documento
├── front/
│   ├── __init__.py           # Marcador de paquete
│   ├── constants.py          # Constantes: MODULOS, DESCRIPCIONES, COLORES_MODULOS
│   └── styles.py             # Estilos CSS globales (~400 lineas)
├── models/
│   ├── __init__.py           # Marcador de paquete
│   └── schemas.py            # Definicion de campos por tabla (CAMPOS_*)
├── routes/
│   ├── __init__.py           # Marcador de paquete
│   ├── crud.py               # Indicadores por modulo + routing CRUD
│   ├── home.py               # Dashboard de inicio con KPIs y charts
│   └── reports.py            # 6 pestanas de analisis y modelos ML (~940 lineas)
├── services/
│   ├── __init__.py           # Marcador de paquete
│   └── crud.py               # Capa de acceso a datos: leer, insertar, actualizar, eliminar
└── utils/
    ├── __init__.py           # Marcador de paquete
    ├── forms.py              # Widgets de formulario reutilizables (campo_fk, widget_campo)
    └── ui.py                 # Funciones de UI: modulo_crud, busqueda, filtros, status_badge
```

---

## 3. Responsabilidad de cada archivo

### Capa de presentacion (front/)

| Archivo | Funcion |
|---|---|
| `front/constants.py` | Define la lista `MODULOS`, las `DESCRIPCIONES` de cada modulo y los `COLORES_MODULOS` |
| `front/styles.py` | Contiene toda la hoja de estilos CSS inyectada al inicio de la app: animaciones, tarjetas, metricas, botones, sidebar, tabs, badges, formularios |

### Capa de rutas (routes/)

| Archivo | Funcion |
|---|---|
| `routes/home.py` | Renderiza el dashboard de inicio: hero, KPIs generales, indicadores de la ultima semana, 4 graficas Plotly (tendencia, estatus, combustible, mantenimiento), acceso rapido a modulos |
| `routes/crud.py` | Contiene `indicadores_modulo()` que genera metricas especificas por tabla (disponibilidad de flota, costos, etc.) y `render()` que enruta al CRUD generico |
| `routes/reports.py` | Archivo mas grande del proyecto (~940 lineas). Implementa las 6 pestanas de analisis: Metodologia, ETL, Reportes descriptivos, Regresion, Clasificacion, Clustering |

### Capa de servicios (services/)

| Archivo | Funcion |
|---|---|
| `services/crud.py` | Capa de acceso a datos con 4 operaciones: `leer_tabla()`, `insertar()`, `actualizar()`, `eliminar()`. Usa SQLite con `check_same_thread=False` |

### Capa de modelos (models/)

| Archivo | Funcion |
|---|---|
| `models/schemas.py` | Define el diccionario de campos para cada tabla (`CAMPOS_CLIENTES`, `CAMPOS_VEHICULOS`, etc.). Cada campo especifica tipo, etiqueta, ayuda y opciones |

### Capa de utilidades (utils/)

| Archivo | Funcion |
|---|---|
| `utils/forms.py` | Funciones para construir formularios dinamicos: `widget_campo()` renderiza el widget correcto segun el tipo (texto, numero, fecha, hora, select, FK), `construir_opciones_fk()` carga las opciones de tablas relacionadas |
| `utils/ui.py` | Funcion principal `modulo_crud()` que genera la interfaz completa de un modulo CRUD: tabla, busqueda, filtros, formularios de agregar/editar/eliminar, badges de estatus |

### Archivos raiz

| Archivo | Funcion |
|---|---|
| `app.py` | Punto de entrada. Configura la pagina, inyecta CSS, inicializa la BD, renderiza el sidebar con badges de conteo y barra de progreso, enruta a home/crud/reports |
| `database.py` | Crea las 7 tablas con SQLite, genera 400 entregas, 150 registros de combustible y 45 de mantenimiento como datos de ejemplo |
| `requirements.txt` | Lista de dependencias con versiones minimas |

---

## 4. Modelo de datos

### 4.1 Diagrama entidad-relacion

```
clientes (1) ──────┬────── (N) entregas
                    │
vehiculos (1) ─────┼────── (N) entregas
                    │         │
                    │         ├── (N) combustible
                    │         └── (N) mantenimiento
                    │
operadores (1) ────┼────── (N) entregas
                    │
rutas (1) ─────────┴────── (N) entregas
```

### 4.2 Tablas y campos

| Tabla | Campos | Relaciones |
|---|---|---|
| `clientes` | id (PK), nombre, contacto, direccion | — |
| `vehiculos` | id (PK), placas, modelo, capacidad_kg, estatus | — |
| `operadores` | id (PK), nombre, licencia, telefono | — |
| `rutas` | id (PK), origen, destino, distancia_km | — |
| `entregas` | id (PK), cliente_id (FK), vehiculo_id (FK), operador_id (FK), ruta_id (FK), fecha, hora_salida, minutos_estimados, minutos_reales, estatus | FK a clientes, vehiculos, operadores, rutas |
| `combustible` | id (PK), vehiculo_id (FK), fecha, litros, costo, km_recorridos | FK a vehiculos |
| `mantenimiento` | id (PK), vehiculo_id (FK), fecha, tipo, costo, descripcion | FK a vehiculos |

### 4.3 Datos de ejemplo

La base de datos se genera automaticamente con:
- 10 clientes
- 8 vehiculos (6 activos, 2 en mantenimiento)
- 6 operadores
- 10 rutas
- 400 entregas simuladas (ultimos 90 dias)
- 150 registros de combustible
- 45 registros de mantenimiento

---

## 5. Modelo de Data Warehouse (esquema de estrella)

```
   clientes (DIMENSION)                vehiculos (DIMENSION)
 ┌─────────────────┐                ┌─────────────────┐
 │ id (PK)         │                │ id (PK)         │
 │ nombre          │                │ placas          │
 │ contacto        │                │ modelo          │
 │ direccion       │                │ capacidad_kg    │
 └───────┬─────────┘                │ estatus         │
         ▼                          └───────┬─────────┘
┌──────────────────────────────────────────────────────┐
│                      entregas                        │
│                   TABLA DE HECHOS                     │
│                                                      │
│  cliente_id  (FK)  ──► clientes                      │
│  vehiculo_id (FK)  ──► vehiculos                     │
│  operador_id (FK)  ──► operadores                    │
│  ruta_id     (FK)  ──► rutas                         │
│  fecha · hora_salida                                 │
│  minutos_estimados (metrica)                         │
│  minutos_reales    (metrica)                         │
│  estatus                                             │
└──────────────────────────────────────────────────────┘
         ▲                                 ▲
┌───────┴─────────┐                ┌───────┴─────────┐
│ id (PK)         │                │ id (PK)         │
│ nombre          │                │ origen          │
│ licencia        │                │ destino         │
│ telefono        │                │ distancia_km    │
└─────────────────┘                └─────────────────┘
   operadores (DIMENSION)              rutas (DIMENSION)
```

**Por que esquema de estrella?**
- **Hechos** (`entregas`): eventos medibles del negocio; cada fila es una entrega con
  sus metricas (minutos estimados y reales).
- **Dimensiones** (clientes, vehiculos, operadores, rutas): contexto descriptivo que
  permite filtrar y agrupar los reportes.
- **Ventajas**: consultas mas rapidas y faciles de entender; cada entrega se relaciona
  con una sola fila por dimension.

---

## 6. Mapeo de las 5 unidades del curso

| Unidad | Tema | Evidencia tecnica en SIG-LOG |
|---|---|---|
| 1 | Base de datos y SQL | 7 tablas con llaves foraneas, esquema de estrella, operaciones CRUD (INSERT, UPDATE, DELETE, SELECT), integridad referencial con `PRAGMA foreign_keys = ON` |
| 2 | ETL / Preparacion de datos | `reports.py` pestana 1: Extract de SQLite con `pandas.read_sql_query`, Transform con `dropna()`, creacion de columnas derivadas `retraso_min` y `retrasado`, Load a scikit-learn |
| 3 | Reportes descriptivos | `reports.py` pestana 2: 12+ graficas Plotly interactivas (barras, pastel, linea, area, dispersion, heatmap), filtros por periodo, KPIs, configuracion de variable/tipo/top N, reporte HTML descargable |
| 4 | Aprendizaje supervisado | `reports.py` pestanas 3-4: Regresion lineal simple (`LinearRegression` con 1 variable), Regresion multiple (3 variables + coeficientes), Clasificacion logistica (`LogisticRegression` con `StandardScaler`, matriz de confusion, metricas MAE/RMSE/R2/Exactitud/Precision/Recall/F1), predictor interactivo |
| 5 | Aprendizaje no supervisado | `reports.py` pestana 5: Clustering `KMeans` con 2-5 grupos, metodo del codo (inercia), indice de silueta, reduccion `PCA` a 2 dimensiones, visualizacion en grafica de dispersion |

---

## 7. Modelos de machine learning

### 7.1 Regresion lineal simple (Unidad 4)

- **Algoritmo**: `sklearn.linear_model.LinearRegression`
- **Variable independiente (X)**: `distancia_km`
- **Variable dependiente (Y)**: `minutos_reales`
- **Separacion**: 75% entrenamiento, 25% prueba (`train_test_split`, `random_state=42`)
- **Metricas**:
  - **MAE** (Mean Absolute Error): promedio de las diferencias absolutas entre prediccion y realidad. Mientras mas bajo, mejor.
  - **RMSE** (Root Mean Squared Error): raiz del error cuadratico medio. Penaliza mas los errores grandes.
  - **R2** (Coeficiente de determinacion): que tan bien explica el modelo los datos. Va de 0 a 1; 1.0 = prediccion perfecta.

### 7.2 Regresion multiple (Unidad 4)

- **Algoritmo**: `sklearn.linear_model.LinearRegression`
- **Variables independientes (X)**: `distancia_km`, `minutos_estimados`, `hora_num` (hora de salida en formato numerico)
- **Variable dependiente (Y)**: `minutos_reales`
- **Coeficientes**: tabla que muestra cuanto influye cada variable en la prediccion. Un coeficiente positivo significa que al aumentar esa variable, aumenta el tiempo real.
- **Metricas**: MAE, RMSE, R2 (comparar con el modelo simple para ver si mejora).

### 7.3 Clasificacion logistica (Unidad 4)

- **Algoritmo**: `sklearn.linear_model.LogisticRegression` (con `class_weight="balanced"`, `max_iter=1000`)
- **Variable objetivo (Y)**: `retrasado` (0 = a tiempo, 1 = tarde; umbral: >15 min de retraso)
- **Variables de entrada (X)**: `distancia_km`, `minutos_estimados`, `hora_num`
- **Preprocesamiento**: `StandardScaler` para normalizar las variables
- **Metricas**:
  - **Exactitud**: porcentaje total de predicciones correctas
  - **Precision**: de las predichas como "tarde", cuantas realmente lo fueron
  - **Recall**: de las que realmente fueron tarde, cuantas detecto el modelo
  - **F1-score**: promedio harmonico entre precision y recall (balance entre ambos)
- **Matriz de confusion**: tabla 2x2 que muestra verdaderos positivos, falsos positivos, verdaderos negativos y falsos negativos
- **Predictor interactivo**: el usuario ingresa distancia, minutos estimados y hora; el modelo devuelve "Llegara a tiempo" o "Llegara tarde"

### 7.4 Clustering K-means (Unidad 5)

- **Algoritmo**: `sklearn.cluster.KMeans` (con `n_init=10`, `random_state=42`)
- **Variables (X)**: `distancia_km` y `num_entregas` (agrupadas por ruta)
- **Preprocesamiento**: `StandardScaler` para normalizar
- **Numero optimo de clusters**:
  - **Metodo del codo**: grafica de inercia vs numero de clusters; el "codo" indica el punto optimo
  - **Indice de silueta**: mide que tan bien separados estan los grupos (va de -1 a 1; mas alto = mejor)
- **Reduccion de dimensiones**: `PCA` (Principal Component Analysis) reduce a 2 componentes para visualizar
- **Visualizacion**: grafica de dispersion con cada ruta como punto, coloreado por grupo
- **Slider interactivo**: el usuario puede cambiar el numero de clusters (2 a 5) y ver como cambia la agrupacion

---

## 8. Dependencias

```
streamlit>=1.32
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
plotly>=5.24
```

Para instalar todas las dependencias:
```
pip install -r requirements.txt
```

---

## 9. Instalacion paso a paso (para alguien sin conocimiento previo)

1. **Descargar/copiar** la carpeta `sig_log` completa a la computadora.
2. **Abrir una terminal** (CMD, PowerShell o Terminal) dentro de la carpeta:
   ```
   cd ruta/a/sig_log
   ```
3. **(Opcional) Crear entorno virtual** (recomendado para no mezclar dependencias):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
4. **Instalar dependencias**:
   ```
   pip install -r requirements.txt
   ```
   Esto descargara e instalara Streamlit, pandas, scikit-learn, Plotly y numpy.
5. **Ejecutar la aplicacion**:
   ```
   streamlit run app.py
   ```
6. **Se abrira el navegador** automaticamente en `http://localhost:8501`. Si no se abre
   solo, copia esa URL y pegala en tu navegador.
7. La primera vez, la base de datos se crea automaticamente en `data/sig_log.db` con
   datos de ejemplo.

---

## 10. Mantenimiento del sistema

### Reiniciar datos de ejemplo
Borrar el archivo `data/sig_log.db` y volver a ejecutar `streamlit run app.py`.
La base de datos se regenera automaticamente con los datos originales.

### Agregar un nuevo modulo
Seguir el patron de los modulos existentes:
1. Agregar la tabla en `database.py`
2. Definir los campos en `models/schemas.py`
3. Agregar el modulo al `modulo_crud()` en `routes/crud.py`
4. Agregar el nombre a `MODULOS` en `front/constants.py`

### Dependencias
Todas las dependencias estan en `requirements.txt`. No se requieren dependencias
adicionales para el funcionamiento base.

---

## 11. Limitaciones conocidas

- Aplicacion de un solo usuario (no tiene login ni permisos por rol).
- No esta pensada para produccion a gran escala, solo como prototipo academico.
- La base de datos SQLite es local (no soporta multiples conexiones simultaneas desde
  diferentes maquinas).
- Los modelos de ML se re-entrenan en cada carga de la pestana (con 400 registros es
  rapido, pero con millones de registros seria necesario cachear).
