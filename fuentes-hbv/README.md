# fuentes-hbv — fuentes crudas recolectadas (HermesBV)

Todo lo scrapeado/descargado para el grafo de investigadores de Argentina.

## Contenido

- `UBACyT/` — derivados y listados sin datos personales: TSV por facultad (Derecho, FFyL, FADU),
  listados de proyectos vigentes (xlsx director/codirector), `_registro.tsv` (origen de cada
  archivo: año, alcance, URL, nivel A=integrantes / B=dir+codir) y `_notas.md`.
- `_indice/` — índices y convenciones de la recolección.

## Qué NO está en este repositorio (y por qué)

Este repositorio es **público**. Se retiraron (también del historial) los archivos que traen
datos personales identificatorios:

- Las **resoluciones UBA en PDF** (acreditación/otorgamiento 2010–2026): publican el **DNI** de
  directores/as. Se pueden volver a bajar de la URL que figura en `UBACyT/_registro.tsv`.
- El **comprimido con el resto de las fuentes** (SICyTAR, SECyT-UNC, becas, PICT, PIP, etc.):
  trae DNI, CUIL y emails de terceros. Las bases derivadas viven en una copia local.
- **CUIL** de SECyT-UNC, **HTML de CYTED** (emails) y los PDF de fichas FADU.
- Las bases derivadas publicadas (`output/xlsx/UBACYT-consolidado-v2.2.xlsx`) **no incluyen DNI,
  CUIL, emails ni datos de contacto**.
