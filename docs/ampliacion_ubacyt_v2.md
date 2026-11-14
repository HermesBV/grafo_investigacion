# Ampliación UBACyT v2 (fork HermesBV)

`output/xlsx/UBACYT-consolidado-v2.2.xlsx` (v2.2 = v2.1 sin datos personales; ver «Versiones») — hoja **`Datos`** con las **11 columnas del contrato**
([modelo_datos.md](modelo_datos.md)), lista para la notebook:

```sh
GRAFO_EXCEL=output/xlsx/UBACYT-consolidado-v2.2.xlsx GRAFO_ALIASES=output/xlsx/ampliacion_v2/alias_aplicados-v2.1.json  # y ejecutar notebooks/ubacyt_grafo.ipynb
```

| | base del repo (graph.json) | v2 |
|---|---|---|
| filas | 44.664 | **72.187** |
| proyectos UBACyT | 3.225 | **7.258** |
| personas (nombres distintos, tras 729 alias de tildes/puntuación) | ~16.700 | **24.596** |
| conexiones | — | **185.827** |
| años | 2021, 2022, 2023, 2024, 2026 | **2010–2014, 2016–2018, 2020–2026** |

## Cómo se armó

1. **Base reconstruida.** El Excel consolidado original no está en el repositorio, así que la base
   del repo se reconstruyó desde `web/public/data/graph.json` (cada observación año/cobertura/rol de
   cada miembro → una fila). Quedan vacíos `Convocatoria`, `Página PDF` y `Fila en página`
   (el JSON no los guarda), y el título/unidad es uno por proyecto.
   El dueño del Excel original puede, en cambio, **anexar sólo** `ampliacion_v2/UBACYT-ampliacion-v2.csv`
   (27.521 filas nuevas) a su Excel, que es equivalente y conserva sus referencias de página.
2. **Fusión sin pisar.** Si un (año, código) ya está en la base **con la misma cobertura**, manda la
   base y la fila nueva se descarta (4.450 filas descartadas así; las diferencias de dirección/codirección
   quedaron en `ampliacion_v2/UBACYT-diferencias-v2.csv`, 29 casos, para revisar). Sólo se agregan:
   años nuevos, proyectos que no estaban en ese año, y coberturas distintas (p. ej. integrantes completos
   de FFyL 2026 donde la base sólo tenía dirección/codirección). Duplicados exactos eliminados.
3. **Identidad.** Igual que la notebook: NFC + mayúsculas + espacios; **no** se unen nombres que difieren
   en tildes. Los 404 casos donde un nombre nuevo sólo difiere en tildes/puntuación de uno existente están
   en `ampliacion_v2/alias_sugeridos-v2.json` (formato `--aliases` / `ALIAS_PERSONAS`), para revisión manual.

## Fuentes agregadas (crudos en `fuentes-hbv/UBACyT/`, origen en su `_registro.tsv`)

| Año del listado | Cobertura | Fuente |
|---|---|---|
| 2010, 2011, 2012, 2013 | completa | Listas SIGEVA de integrantes de **todas las facultades** publicadas por sociales.uba.ar (PC 2010-12, 2011-14 con rol; 2012-15, 2013-16 sin rol → `SIN ROL`) |
| 2011, 2013, 2014, 2016, 2017, 2018, 2020, 2023, 2026 | sólo dirección y codirección | Resoluciones CS de acreditación (año = inicio de la programación). Se excluyen los anexos de **no acreditados / no admitidos** |
| 2024, 2025 | sólo dirección y codirección | Resoluciones de otorgamiento de cuotas 2024 y **2025** (RESCS-2023-1965/1966, RESCS-2025-288/289). Cubre el hueco 2025 |
| 2010–2026 | completa | Facultad de Derecho: páginas por proyecto (año = inicio de programación) |
| 2023, 2026 | completa | Filosofía y Letras: catálogo Omeka (PC2023, PC2026) con rol |
| 2020–2023 | completa | FADU, Instituto de la Espacialidad Humana: fichas con rol |

## Limitaciones conocidas

- **Rol nuevo `INVESTIGADOR COLABORADOR`** (FFyL Omeka, listas 2011-14). Se agregó a `PUNTOS_ROL` en la
  notebook con **2 puntos provisorios** y su etiqueta en `web/src/main.js`; revisar el puntaje.
- "Becario", "Colaborador externo" sin más detalle y las listas sin rol → `SIN ROL`.
- Resoluciones escaneadas con OCR (2011-14 Res 2657, 2016 Res 4756/4912): nombres con errores de OCR;
  se descartaron directores sin código legible. Las escaneadas sin capa de texto (Res 1004/10, 4895/12, 921/14) no se usaron.
- Lista SIGEVA 2011-14: ~1.900 filas no se pudieron alinear por columnas y se descartaron (~20%).
- Derecho y FADU dan nombres en orden "Nombre Apellido": se convirtieron a "APELLIDO, NOMBRE" buscando
  coincidencias con nombres conocidos; si no hay, se toma el último apellido (heurística, ~1.150 casos).
- El año de las fuentes por programación es el de inicio; no se replican equipos a los años siguientes.
- **El visor (`graph.json`, CSV de nodos/aristas) se regeneró con v2.2**: notebook con `GRAFO_EXCEL` y `GRAFO_ALIASES`,
  `build_web_data.py --excel ... --aliases ...`, `pnpm layout`, validación (`complete`), `pnpm test` y `pnpm build`.

Scripts: `scripts/ampliacion_v2/` (`parsear_resoluciones.py`, `parsear_listas_sociales.py`, `fusionar_v2.py`).

## Versiones y correcciones (2026-11)

- **v2.1**: 729 alias de tildes/puntuación aplicados (`ampliacion_v2/alias_aplicados-v2.1.json`; 25.326 → 24.600 nombres),
  +3 codirectores, y 29 diferencias de dirección/codirección resueltas (17 misma persona, 3 codirectores sumados,
  9 descartadas por orden de nombre invertido o conflicto de director). Las celdas vacías de `Página PDF` y `Fila en página`
  valen 0 («sin referencia»).
- **v2.2**: igual que v2.1 pero sin datos personales que el OCR dejó pegados a cuatro nombres de integrantes de las listas
  SIGEVA 2011 (un número de documento y marcas «DNI» leídas con errores). Se quitó el número de tres nombres y se descartó una
  fila que era solo ruido de OCR (72.188 → 72.187 filas; 24.600 → 24.596 personas). La v2.1 se conserva sin tocar solo por
  trazabilidad y **no** debe publicarse; el historial de git anterior sigue conteniendo esos cuatro valores.
