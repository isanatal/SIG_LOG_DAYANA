# Manual de Usuario -- SIG-LOG

## 1. Presentacion del proyecto

### 1.1 Caso de estudio

Una empresa dedicada al transporte y distribucion de mercancias cuenta con una flotilla
de vehiculos que realiza entregas diariamente a diferentes clientes y destinos. Actualmente,
la empresa almacena informacion relacionada con vehiculos, operadores, clientes, rutas,
entregas, combustible y mantenimiento en diferentes archivos y sistemas.

Esta situacion dificulta responder preguntas clave como:

- **Que rutas son mas utilizadas?**
- **Que vehiculos generan mayores costos?**
- **Que operadores realizan mas entregas?**
- **Que rutas presentan mayores retrasos?**
- **Que vehiculos consumen mas combustible?**
- **Cuales son las causas principales de retraso?**
- **Que vehiculos requieren mantenimiento?**
- **Es posible predecir si una entrega llegara tarde?**
- **Podemos identificar grupos de rutas similares?**

Por ello, se requiere un sistema que permita administrar, procesar, analizar y visualizar
la informacion logistica, asi como aplicar tecnicas de extraccion de conocimiento.

### 1.2 Objetivo general

Disenar e implementar un sistema de informacion para una empresa de transporte que permita
administrar vehiculos, operadores, clientes, rutas, entregas, combustible y mantenimiento,
generando informacion util para optimizar las operaciones logisticas y apoyar la toma de
decisiones. El sistema identifica patrones relacionados con:

- Demanda de servicios
- Servicio con mayor demanda
- Horarios de mayor saturacion
- Mayor frecuencia
- Rutas con mayor numero de envios

### 1.3 Que es SIG-LOG

**SIG-LOG: Sistema Integral de Gestion Logistica** es una aplicacion web que administra
toda la informacion logistica de la empresa en un solo lugar: desde el registro de clientes
hasta el analisis predictivo de entregas, pasando por el control de flota, combustible,
mantenimiento y reportes interactivos con modelos de inteligencia artificial.

---

## 2. Como iniciar el sistema

### Requisitos previos
- Python 3.10 o superior instalado
- Acceso a internet la primera vez (para instalar dependencias)

### Instalacion
1. Abrir una terminal (CMD, PowerShell o Terminal) dentro de la carpeta del proyecto.
2. (Opcional) Crear un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Ejecutar la aplicacion:
   ```
   streamlit run app.py
   ```
5. Se abrira el navegador automaticamente en `http://localhost:8501`.

### Acceso
El sistema no requiere usuario ni contrasena. Al iniciar se muestra la pantalla de inicio
con un resumen general y acceso rapido a todos los modulos.

---

## 3. Navegacion general

En la **barra lateral izquierda** se encuentran todos los modulos:

| Modulo | Descripcion |
|---|---|
| Inicio | Dashboard con KPIs y acceso rapido |
| Clientes | Registro y admin de clientes |
| Vehiculos | Flota: placas, modelo, capacidad, estatus |
| Operadores | Altas de operadores y licencias |
| Rutas | Origen, destino y distancia |
| Entregas | Registro completo de cada entrega |
| Combustible | Control de litros y costos |
| Mantenimiento | Servicios preventivos y correctivos |
| Reportes y analisis | Graficas, indicadores y modelos de ML |

Cada modulo muestra en el sidebar el **numero de registros** actuales.

---

## 4. Modulos CRUD

Todos los modulos CRUD funcionan igual. Cada uno tiene:

- **Tabla** con todos los registros actuales
- **Barra de busqueda** para filtrar por cualquier campo
- **Filtro por estatus** (cuando aplica)
- **Pestana "Agregar nuevo registro"** con formulario
- **Pestana "Editar o eliminar"** con selector de registro

### 4.1 Clientes

Registra a los clientes de la empresa y sus datos de contacto.

| Campo | Tipo | Descripcion |
|---|---|---|
| Nombre | Texto | Nombre del cliente ( Ej. Grupo Alfa) |
| Contacto | Texto | Telefono o persona de contacto |
| Direccion | Texto | Calle, numero y ciudad |

**Indicadores:** Total de clientes, numero de ciudades atendidas.

### 4.2 Vehiculos

Administra la flota de unidades de transporte.

| Campo | Tipo | Descripcion |
|---|---|---|
| Placas | Texto | Identificador unico ( Ej. TOL-101-A) |
| Modelo | Texto | Marca y modelo ( Ej. Nissan NP300) |
| Capacidad (kg) | Numero | Peso maximo de carga |
| Estatus | Lista | Activo, Mantenimiento o Retirado |

**Indicadores:** Total de unidades, activas, en mantenimiento. Incluye una **barra de
disponibilidad** que muestra que porcentaje de la flota esta operativa.

**Filtro:** Puede filtrar por estatus para ver solo vehiculos activos, en mantenimiento
o retirados.

### 4.3 Operadores

Da de alta a los conductores de las unidades.

| Campo | Tipo | Descripcion |
|---|---|---|
| Nombre | Texto | Nombre completo del operador |
| Licencia | Texto | Numero de licencia de conducir |
| Telefono | Texto | Numero de contacto |

### 4.4 Rutas

Define las rutas de la empresa con origen, destino y distancia.

| Campo | Tipo | Descripcion |
|---|---|---|
| Origen | Texto | Ciudad de salida |
| Destino | Texto | Ciudad de llegada |
| Distancia (km) | Numero | Kilometros de la ruta |

**Indicadores:** Total de rutas, distancia promedio.

### 4.5 Entregas

Registra cada entrega realizada por la empresa. Es el modulo mas completo porque
relaciona cliente, vehiculo, operador y ruta.

| Campo | Tipo | Descripcion |
|---|---|---|
| Cliente | Lista (FK) | Quien recibe la entrega |
| Vehiculo | Lista (FK) | Unidad que realiza la entrega |
| Operador | Lista (FK) | Quien conduce la unidad |
| Ruta | Lista (FK) | Origen y destino |
| Fecha | Fecha | Dia de la entrega |
| Hora de salida | Hora | Hora en que salio la unidad |
| Minutos estimados | Numero | Tiempo previsto de la entrega |
| Minutos reales | Numero | Tiempo real (0 si se cancelo) |
| Estatus | Lista | Entregado, Retrasado o Cancelado |

**Indicadores:** Total de entregas, entregadas, retrasadas, canceladas, tiempo promedio real.

### 4.6 Combustible

Lleva el control de litros y costos de combustible por vehiculo.

| Campo | Tipo | Descripcion |
|---|---|---|
| Vehiculo | Lista (FK) | Unidad que cargo combustible |
| Fecha | Fecha | Dia de la carga |
| Litros | Numero | Combustible cargado |
| Costo ($) | Numero | Costo total en pesos |
| Km recorridos | Numero | Kilometros recorridos en ese periodo |

**Indicadores:** Costo total de combustible, costo promedio por carga.

### 4.7 Mantenimiento

Controla los servicios y costos de mantenimiento de cada vehiculo.

| Campo | Tipo | Descripcion |
|---|---|---|
| Vehiculo | Lista (FK) | Unidad a la que se le da servicio |
| Fecha | Fecha | Dia del servicio |
| Tipo | Lista | Preventivo (rutina) o Correctivo (reparacion) |
| Costo ($) | Numero | Costo del servicio |
| Descripcion | Texto | Detalle del trabajo realizado |

**Indicadores:** Costo total, preventivos, correctivos.

---

## 5. Reportes y analisis

El modulo de Reportes es el nucleo analitico del sistema. Tiene **6 pestanas** que cubren
desde la metodologia hasta los modelos de inteligencia artificial.

### Pestana 0: Metodologia (CRISP-DM / KDD)

Explica las metodologias aplicadas en el proyecto:

- **KDD** (Knowledge Discovery in Databases): proceso completo de descubrimiento de
  conocimiento en bases de datos.
- **CRISP-DM**: metodologia guiada por el negocio con 6 fases: comprension del negocio,
  comprension de los datos, preparacion, modelado, evaluacion y despliegue.
- **ETL vs ELT**: explica la diferencia y por que se uso ETL en este proyecto.
- **Data Warehouse**: muestra el esquema de estrella (tabla de hechos `entregas` rodeada
  de dimensiones: clientes, vehiculos, operadores, rutas).
- **Tabla de las 5 unidades del curso** y como se aplican en SIG-LOG.

### Pestana 1: ETL - Preparacion de datos (Unidad 2)

Muestra paso a paso como se preparan los datos antes de analizarlos:

1. **Extract**: datos crudos extraidos de la tabla `entregas`.
2. **Transform**: limpieza de nulos, calculo de columnas derivadas (`retraso_min`, `retrasado`).
3. **Load**: datos listos para modelar.

### Pestana 2: Reportes descriptivos (Unidad 3)

Esta pestana responde directamente las preguntas del caso de estudio:

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
| Es posible predecir si una entrega llegara tarde? | Pestana 4: Clasificacion logistica |
| Podemos identificar grupos de rutas similares? | Pestana 5: Clustering K-means |

**Caracteristicas:**
- **Filtro por periodo de fechas**: selecciona fecha de inicio y fin.
- **Grafica configurable**: elige variable (Ruta, Operador, Cliente, Vehiculo), tipo de
  grafica (barras verticales, horizontales o pastel) y cuantas categorias mostrar (top N).
- **Graficas interactivas**: pasa el cursor para ver valores exactos, usa la lupa para
  acercar, haz click en la leyenda para ocultar/mostrar categorias.
- **Reporte descargable**: genera un archivo HTML con todas las graficas interactivas,
  indicadores, periodo y fecha/hora de generacion.

### Pestana 3: Regresion - Aprendizaje supervisado (Unidad 4)

Predice los **minutos reales** que tardara una entrega.

**Regresion lineal simple:**
- Variable de entrada: distancia en km
- Variable a predecir: minutos reales
- Metricas: MAE (error absoluto promedio), RMSE (error cuadratico), R2 (que tan bien
  explica el modelo, 1.0 = perfecto)

**Regresion multiple:**
- Variables de entrada: distancia_km + minutos_estimados + hora de salida
- Incluye tabla de coeficientes que muestra cuanto influye cada variable
- Metricas: MAE, RMSE, R2

### Pestana 4: Clasificacion - Aprendizaje supervisado (Unidad 4)

Predice si una entrega **llegara tarde** (>15 min de retraso) o **a tiempo**.

- Variables de entrada: distancia_km, minutos_estimados, hora de salida
- Normalizacion: StandardScaler
- Metricas: Exactitud, Precision, Recall, F1-score
- **Matriz de confusion**: muestra aciertos y errores del modelo
- **Predictor interactivo**: ingresa distancia, minutos estimados y hora; presiona
  "Predecir" y el modelo te dice si llegara tarde o a tiempo.

### Pestana 5: Clustering - Aprendizaje no supervisado (Unidad 5)

Identifica **grupos de rutas similares** automaticamente.

- Variables: distancia_km y numero de entregas por ruta
- **Metodo del codo**: grafica que ayuda a elegir el numero optimo de grupos
- **Indice de silueta**: mide que tan bien separados estan los grupos
- **PCA**: reduccion a 2 dimensiones para visualizar los grupos en una grafica
- Slider para elegir el numero de clusters (2 a 5)

---

## 6. Las 5 unidades del curso en SIG-LOG

| Unidad | Tema | Donde se ve en SIG-LOG |
|---|---|---|
| 1 | Base de datos y SQL | 7 tablas con llaves foraneas, esquema de estrella, operaciones CRUD completas |
| 2 | ETL / Preparacion de datos | Pestana 1 de Reportes: limpieza de nulos, columnas derivadas |
| 3 | Reportes descriptivos | Pestana 2 de Reportes: 12+ graficas interactivas, filtros, KPIs |
| 4 | Aprendizaje supervisado | Pestana 3 (Regresion) y Pestana 4 (Clasificacion) de Reportes |
| 5 | Aprendizaje no supervisado | Pestana 5 de Reportes: Clustering con K-means, PCA, codo y silueta |

---

## 7. Preguntas frecuentes

- **Perdi mis datos?** Los datos se guardan en `data/sig_log.db`. Mientras no borres
  ese archivo, la informacion persiste entre sesiones.
- **Como reinicio los datos de ejemplo?** Borra el archivo `data/sig_log.db` y vuelve a
  ejecutar `streamlit run app.py`.
- **Cuanto tarda en cargar?** La primera vez puede tardar unos segundos al cargar los
  modelos de ML. Las demas veces es casi instantaneo.
- **Puedo usar el sistema en otro equipo?** Si. Copia la carpeta del proyecto, instala
  las dependencias con `pip install -r requirements.txt` y ejecuta `streamlit run app.py`.
