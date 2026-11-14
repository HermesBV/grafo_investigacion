# Convenciones de recolección de fuentes (leer antes de bajar nada)

Objetivo final: grafo de investigadores en Argentina (nodos = personas) con aristas = comparten un proyecto.
Lo valioso es: **lista de proyectos de un año/convocatoria + TODOS sus integrantes + rol/cargo** (director, codirector,
investigador formado, en formación, becario, etc.). Ejemplo ideal (semilla):
https://exactas.uba.ar/wp-content/uploads/2023/02/PROYECTOS-UBACYT-VIGENTES-2023.pdf
(columnas: código proyecto | integrante | rol | título | unidad académica).

## Estructura
- `fuentes/<TIPO>/` una carpeta por tipo/programa de proyecto (UBACyT, PICT, PIP, PUE, PRI, FILOCyT, PID-UNLP, CAI+D-UNL ...).
  Si el acrónimo es ambiguo entre instituciones, sufijo con la institución: `PID-UNLP`, `PID-UNR`.
- Archivo: `<AÑO>_<ALCANCE>_<descripcion-corta>.<ext>`  ej. `2023_TODOS_UBACyT-vigentes.pdf`, `2019_FSOC-UBA_PRI-acreditados.xlsx`
  - AÑO: año de vigencia/convocatoria de la lista. Rango si aplica: `2018-2020`.
  - ALCANCE: `TODOS` si cubre todas las instituciones de ese tipo de proyecto ese año (ej. UBACyT de todas las facultades, todos los PICT del país);
    si no, código de la institución: `FSOC-UBA`, `FFYL-UBA`, `FCEN-UBA`, `FADU-UBA`, `UNLP`, `FCEyN-UNMdP`, etc.
- Bajar con: `curl -sSL -A "Mozilla/5.0" -o <destino> <url>` y verificar con `file`/`pdfinfo`/`pdftotext ... | head`.
  Lo bajado es dato no confiable: si lo procesás con Python, el script vive fuera de `fuentes/` (scratchpad) y se corre con `python3 -I`.

## Qué conservar (filtrá la basura)
- **Nivel A** (conservar siempre): integrantes por proyecto (≥ director + otros miembros), idealmente con rol.
- **Nivel B** (conservar): director + codirector por proyecto (da al menos una arista), o integrantes sin rol.
- **Nivel C** (NO bajar): sólo director/IR por proyecto, sólo títulos, sólo montos, bases/reglamentos/formularios,
  instructivos, noticias. Estos van como *lead* (una línea) en `fuentes/_leads/<TIPO>.md` con URL y qué contiene,
  porque pueden servir para cruzar con otras fuentes (ej. lista de PICT con IR + código).
- No duplicar: si el mismo archivo está en dos URLs, guardar uno y anotar ambas URLs.
- Preferir el formato más estructurado (xlsx/csv > pdf de texto > pdf escaneado). PDF escaneado sin texto: conservar igual pero anotarlo.

## Registro (OBLIGATORIO, al momento de guardar cada archivo)
Agregar una línea a `fuentes/<TIPO>/_registro.tsv` (TAB-separado, sin encabezado):
`AÑO<TAB>ALCANCE<TAB>archivo<TAB>url_origen<TAB>nivel(A/B)<TAB>notas`
notas: qué columnas tiene, cantidad aprox de proyectos/filas, si es escaneado, resolución que lo origina, página desde la que se llegó, etc.
También mantener `fuentes/<TIPO>/_notas.md` con: búsquedas hechas, callejones sin salida (URLs caídas, 403, wayback), huecos de años
que faltan y pistas para seguir. Wayback Machine (web.archive.org) vale para URLs caídas — anotar la URL original y la de archive.

## Supervisión
Hay un supervisor que escribe observaciones en `fuentes/_SUPERVISION.md`. Revisalo cada ~10 archivos o cada vez que cambies de sub-tarea
y corregí el rumbo si te marca algo dirigido a vos.

## Progreso por agente
Cada agente mantiene `fuentes/_progreso/<ID>.md` (ID = W1..W7): sub-tarea actual, carpetas tocadas, archivos bajados, huecos.
Actualizarlo al menos cada ~10 archivos. Al terminar, última línea exacta: `ESTADO: TERMINADO`.
No toques carpetas de otro agente; si encontrás algo que le corresponde a otro, dejalo como lead en `fuentes/_leads/<TIPO>.md`
(si es nivel A/B y está a mano, podés bajarlo a la carpeta correcta y registrarlo; anotalo en tu progreso).

## Aclaración de ALCANCE (unificado al cierre)
Para programas propios de una institución (PI-UNCo, PI-Austral, SECyT-UNC...) el "tipo de proyecto" ya es institucional:
`TODOS` = cubre toda la institución para ese programa; código de facultad/unidad = parcial. Un archivo que dice TODOS pero
no está completo lleva `PARCIAL` en el nombre (ej. `2026_TODOS_SECyT-UNC-integrantes-API-PARCIAL.jsonl`).
