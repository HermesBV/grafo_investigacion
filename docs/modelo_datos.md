# Contrato para integrar financiamientos

La base consolidada usa una fila por persona, proyecto y listado anual. La hoja
`Datos` conserva sus nueve columnas originales y agrega **`Tipo de proyecto`**.

| Columna | Criterio |
| --- | --- |
| Año del listado | Año entero del corte o fuente, no necesariamente año de aprobación. |
| Código proyecto | Texto completo; conservar ceros iniciales. |
| Convocatoria | Denominación original, si está informada. |
| Integrante | Nombre completo de la persona. |
| Rol integrante | Rol informado por la fuente; no inventar un rol faltante. |
| Título del proyecto | Título original. |
| Unidad académica | Denominación informada, con equivalencias revisadas para el visor. |
| Página PDF | Referencia a la fuente de la consolidación. |
| Fila en página | Referencia a la fila de origen. |
| Tipo de proyecto | Código explícito del financiamiento: `UBACYT`, `PIP`, `PICT`, `PRII`, etc. |

La clave de un proyecto es **`(tipo de proyecto, código)`**. El mismo código en
PIP y UBACyT corresponde a dos proyectos. La identidad de las personas se comparte
entre financiamientos, con el mismo criterio de nombres y alias revisados.

En intercambios procesados, la columna equivalente se denomina `tipo_proyecto`.
La auditoría de participaciones de la notebook ya utiliza ese nombre. Los otros
campos deben adaptarse al contrato de la hoja antes de integrarlos al consolidado.

## Incorporación de nuevos tipos

1. Informar el tipo en cada fila. No inferir PIP, PICT o PRII por la forma del código.
2. Incorporar los datos a la base local, conservando las fuentes y su procedencia.
3. Definir los multiplicadores de **nodos** y **conexiones** para ese tipo en
   `PESOS_TIPO_PROYECTO` y agregarlo a `TIPOS_INCLUIDOS` en la notebook.
4. Revisar los roles nuevos: deben tener puntaje explícito antes de procesar.
5. Registrar las fuentes en `fuentes-ubacyt.json`, con `project_type`, `year`,
   `url` y `level: integrantes`. El nombre histórico del catálogo no limita sus tipos.
6. Ejecutar la notebook, el generador web, el validador y las pruebas.

Por ahora solo UBACyT está incluido y sus multiplicadores son 1 para nodos y 1
para conexiones. **No se asignan ponderaciones automáticas a PIP, PICT o PRII.**
Un tipo incluido sin ponderación detiene el proceso. Los tipos que aún no se
incluyen permanecen en la base y en la auditoría de exclusiones.

## Migración de la base histórica

`python scripts/migrate_project_types.py` agrega la columna si falta. Reconoce
únicamente los tipos históricos UBACyT, PDE y PIUBAS. Conserva un respaldo y
comprueba que cada una de las nueve columnas originales mantenga sus valores y
su orden. Si la columna ya existe, no vuelve a escribir el archivo.

El consolidado histórico contiene 41.164 filas UBACyT, 1.818 PDE y 186 PIUBAS.
Las dos últimas categorías siguen excluidas del grafo publicado.

La base local actualizada se llama
`output/xlsx/UBACYT-consolidado-2021-2022-2023.xlsx`. El original de nueve columnas
se conserva en `output/xlsx/respaldos`. La notebook y el generador web usan la
versión con tipo; sus rutas pueden configurarse.

El Excel completo se mantiene local. El repositorio publica la notebook, los
criterios y los datos procesados que utiliza el visor.

## Esquema web 2

Cada registro de `projects` agrega al final su tipo explícito:
`[código, títulos, unidades, miembros, años, unidades originales, tipo]`.
`types` contiene los tipos presentes y `meta.projectTypeWeights` guarda sus
multiplicadores de nodos y conexiones. No se fusionan grupos por código solo.

Los filtros de tipo, unidad y rol admiten varias opciones: OR entre opciones del
mismo filtro y AND entre filtros distintos. Los mínimos de actividad conservan
su criterio global sobre toda la base del visor.

## Cobertura y esquema web 3

La base tiene once columnas: se agrega `fuente_completa` (completa / sólo dirección y codirección). En el JSON cada proyecto incorpora coberturas en project[7]; cada miembro agrega observaciones [año,cobertura,rol] en member[3]. El filtro usa esa observación para no trasladar integrantes o roles de una fuente completa a otra parcial. Ver [actualización local](actualizacion_local.md). Los recuentos y rangos actuales se calculan desde los datos al cargar el visor.
