# UBACyT — notas (W1)

## Cobertura por año (qué hay en la carpeta)
| Años | Nivel A (integrantes) | Nivel B (dir+codir) |
|---|---|---|
| 2010-2012 (PC2010-12, cód. 2002009...) | FDER-UBA (web) | TODOS: Res CS 1004/10 (escaneado) |
| 2011-2014 (cód. 2002010...) | FDER-UBA | TODOS: Res 2657 (OCR malo) |
| 2012-2015 (cód. 2002011...) | FDER-UBA | TODOS: Res 4895/12 (escaneado) |
| 2013-2016 (cód. 2002012...) | FDER-UBA | TODOS: Res 6932/13 (texto) |
| 2014-2017 (cód. 2002013...) | FDER-UBA | TODOS: Res 921/14 (escaneado) + Res 1271/14 anexos II-VI texto + 1268/14 interdisc. + 777/14 Historia y Memoria |
| 2016-2019 (PC2016, cód. 2002015...) | FDER-UBA | TODOS: Res 4756/16 (OCR) + 4912/16 clínicos + 5015/16 anexos I-V (texto) |
| 2017-2019 (PC2017, cód. 2002016...) | FDER-UBA | TODOS: Res 6903/17 anexos I-III + 7053/17 + 7245/17 |
| 2018-2022 (PC2018, cód. 2002017...) | FDER-UBA; TODOS vía 2021 (W5) y 2022 vigentes | TODOS: Res 1041/18 PDF completo + 1359/18 clínicos + 1244/18 pendientes |
| 2020-2025 (PC2020, cód. 2002019...; Mod I prorrogada a 31/12/2025) | FDER-UBA; TODOS vía 2022 y 2023 vigentes | TODOS: RESCS-2020-345 anexos I-VIII |
| 2021 | **TODOS (PROYECTOS-UBACYT-Y-PDE-VIGENTES-2021.pdf, bajado por W5)** | TODOS: xlsx vigentes a junio 2021 |
| 2022 | **TODOS (exactas, PROYECTO-VIGENTES-2022.pdf)** | |
| 2023 | **TODOS (semilla)** | |
| 2023-2027 (PC2023, cód. 2002022...; Mod I prorrogada a 31/12/2027) | FDER-UBA; **FFYL-UBA (Omeka, con rol)** | TODOS: RESCS-2023-1384 anexos I-VIII |
| 2024 | (PC2023 = semilla 2023; FFYL/FDER) | **TODOS: xlsx vigentes al 26/2/2024** + otorg. 2024 PC2023 (RESCS-2023-1965) y PC2020 (RESCS-2023-1966) |
| 2025 | (idem) | TODOS: otorg. 2025 PC2023 (RESCS-2025-288) y PC2020 (RESCS-2025-289) |
| 2026 / 2026-2028 (PC2026, cód. 2002025...) | FDER-UBA (10 proy); **FFYL-UBA (153 proy, con rol)** | **TODOS: xlsx vigentes al 31/8/26 (cyt.rec.uba.ar)** |

## Búsquedas hechas / callejones
- **Clave:** la WP REST API de los sitios WordPress lista TODOS los adjuntos, incluso los no enlazados: https://cyt.rec.uba.ar/wp-json/wp/v2/media?per_page=100&page=N&_fields=source_url,date (enumeré los 3943 de cyt) y https://exactas.uba.ar/wp-json/wp/v2/media?search=... . Así aparecieron: Proyectos-vigentes-al-26_2_2024.xlsx, Proyectos-UBACYT-vigentes-a-junio-de-2021(.xlsx y -1.xlsx), Proyectos-vigentes-al-15-5-26.xlsx (601 proy, subconjunto de la de 31/8/26 → no bajada), PROYECTOS-CYT-VIGENTES-2022(.pdf y -1.pdf: misma lista que exactas 2022 con otra paginación → no duplicada), PROYECTOS-UBACYT-VIGENTES-2023.pdf (= semilla, mismo md5; URL alternativa https://cyt.rec.uba.ar/wp-content/uploads/PROYECTOS-UBACYT-VIGENTES-2023.pdf), 2021/08/1041-18-Acreditacion-de-la-Programacion-cientifica-2018.pdf (PDF completo con anexos). No hay listas de integrantes 2024-2026 en ninguno de los dos sitios.
- Probé también https://cyt.rec.uba.ar/wp-content/uploads/[2021/08/]{PROYECTOS-UBACYT-Y-PDE-VIGENTES,PROYECTOS-UBACYT-VIGENTES,PROYECTOS-VIGENTES,...}-{2017..2026}.{pdf,xlsx}: sólo existen 2021 y 2023.
- CDX Wayback de exactas.uba.ar/wp-content/uploads/ (7302 URLs): sólo hay listas de integrantes "PROYECTO(S)-VIGENTES" para 2022 y 2023. Nada 2024-2026 ni anterior a 2022.
- Probé por fuerza bruta https://exactas.uba.ar/wp-content/uploads/{2024,2025,2026}/{01..12}/{PROYECTOS-UBACYT-VIGENTES-AAAA, PROYECTOS-VIGENTES-AAAA, PROYECTO-VIGENTES-AAAA, ...-1, Proyectos-UBACyT-vigentes-AAAA}.pdf → todo 404.
- exactas.uba.ar/subsidios/subsidios-uba/ espeja los anexos de cyt.rec.uba.ar (mismos ACS) — no los dupliqué; URL alternativa anotada en el registro.
- cyt.rec.uba.ar/investigacion/subsidios/convocatorias-programaciones-cientificas/programacion-cientifica-{2013-2016,2014-2017,2016,2017,2018,2020,2023,2026}/ : resoluciones de acreditación y otorgamiento con anexos (por proyecto: código, título, monto, director/a, codirector/a con DNI, UA). NO traen integrantes.
- Res 1271/14 Anexo I: la URL de cyt (y su captura Wayback 2022) sirve el Anexo I de Res 1268/14 (PIUBACC). El Anexo I real de 1271/14 no apareció (también en uba.ar/archivos_secyt sólo hay la versión PDTS). Cubierto igual por Res 921/14 escaneada.
- Res 1041/18 (acreditación PC2018): en la página está como .docx SIN anexos, pero la API de medios tiene el PDF completo (bajado). Los anexos de Res 1671/18 (cuota extra 2018) los bajé primero y los reemplacé por éste.
- No bajé los anexos de otorgamiento de cada cuota 2014-2023 (repiten dir+codir de la acreditación; indicación SUP).
- PC2026: no bajé los anexos de acreditación RESCS-2026-1048 (ACS-2026-193..198) ni interdisciplinarios RESCS-2026-1471 (ACS-2026-267..269) porque la xlsx vigentes al 31/8/26 trae la misma info estructurada. URLs: https://cyt.rec.uba.ar/wp-content/uploads/ACS-2026-198-UBA-SGREC-Anexo-I.pdf (y -197..-193), ACS-2026-269/268/267-UBA-SG-REC-Anexo-I/II/III.pdf.
- Anexos "no acreditados / no admitidos" (sólo códigos; útiles para FILTRAR la semilla 2023, que es de feb-2023 y previa a la acreditación): PC2023 https://cyt.rec.uba.ar/wp-content/uploads/ACS-2023-367-UBA-SG-REC_Anexo-IX.pdf (no acreditados) y ACS-2023-366-UBA-SG-REC_Anexo-X.pdf (no admitidos); PC2020 Anexo-IX-aceditacion-PC2020.pdf y Anexo-X-acreditacion-PC2020.pdf; PC2017 2017-Anexo-IV/V-R6903-17.pdf; PC2014-17 Resol-1268-14-Anexo-III.pdf.
- Fac. Derecho (derecho.uba.ar/investigacion/): páginas por proyecto con integrantes (sin rol en las recientes; con categoría en 2011-2014). Scrapeado (201 páginas) → TSV por programación. Scripts: scratchpad W1/scripts/der_scrape.py.
- Fac. Filosofía y Letras: plataforma Omeka https://proyectos.investigacion.filo.uba.ar (API REST deshabilitada, pero /items/browse?output=omeka-xml&page=N devuelve todo con metadatos). 575 items: UBACyT 2023 (110) y 2026 (153) con integrantes + ROL; también FiloCyT 2022/2025, PIP 2025-27, PIDAE 2025/26 (derivados a FILOCyT/, PIP/ y lead PIDAE). Scripts: scratchpad W1/scripts/filo_omeka.py, filo_tsv.py.
- Filo "Proyectos Vigentes 2023_0.pdf" (investigacion.filo.uba.ar): sólo director/codirector de FFyL, subconjunto de la semilla → no bajado. Filo "PROYECTO VIGENTES 2022.pdf" (files/u6/) = mismo md5 que el de exactas 2022.
- Fac. Psicología (psi.uba.ar/ubacyt/vigentes/{2023,2020}/, finalizados/{2010-2012..2018}/): PDFs por programación con director+codirector de Psicología (B, redundante con anexos UBA-wide) → no bajados. vigentes/2026/programacion_ubacyt_2026_.pdf da 404 (link roto). Pre-2010 (2001-2003, 2004-2007, 2006-2009, 2008-2010): páginas HTML sólo director (C).
- Fac. Derecho inv_prog_ubacyt_proyectos_2006.php / _2008.php: listados sin páginas por proyecto (sólo director/título, C).
- sociales.uba.ar: timeout en todas las descargas (blogs.dir/219/files/... "Listado de proyectos" — según buscador son proyectos de "Inicio a la Investigación", no UBACyT).
- Informes de Incentivos SIGEVA-UBA (cyt.rec.uba.ar/wp-content/uploads/Informe-de-Incentivos-2018-SIGEVA-UBA.pdf, 2017, 2014, WINSIP 2013/2015/2016): sólo director por proyecto (UBACyT/PICT/PIP/PDE) → C, lead.
- SIGEVA-UBA (integrantes de todos los proyectos) no es público.

## Huecos
- Integrantes (A) a nivel TODOS: sólo 2021 (W5), 2022 y 2023. Para 2024-2026 sólo hay A para FFyL (PC2023, PC2026) y FDER; el resto de facultades sólo dir+codir (xlsx 2026 y anexos 2024/2025).
- PC2016 / PC2017 / 2014-2017 / anteriores: sólo dir+codir a nivel TODOS (A sólo FDER).
- Pre-2010 (programaciones 2001-2003, 2004-2007, 2006-2009, 2008-2010): nada A/B encontrado.

## Pistas para seguir
- Exactas departamentos / institutos (DF, DQB, IFIBA, etc.) a veces listan integrantes UBACyT por grupo — disperso.
- Otras facultades con posibles listados propios por proyecto: FADU (SI + UBACyT por instituto, ej. ieh.fadu.uba.ar/wp-content/uploads/2024/04/sanguinetti-marco-ubacyt-20020220400352ba.pdf), Económicas (ciece.economicas.uba.ar/actividades/proyectos-de-investigacion/), Agronomía (páginas de laboratorios), FFyB, Medicina.
- Pedir a la SCyT-UBA (subsi@rec.uba.ar) el export de SIGEVA con integrantes (lo que generaba los "PROYECTOS-VIGENTES" de 2022/2023).
- WP REST API media de facultades: fadu, ffyb responden (ffyb espeja los xlsx de cyt 2021 y 2024: https://www.ffyb.uba.ar/wp-content/uploads/2024/09/Proyectos-vigentes-al-26_2_2024.xlsx); agro, economicas, fvet, fmed, odon, sociales, fi, cbc, uba.ar sin resultados/sin API.

## Búsqueda 2026-11-11
**Hallazgo principal:** sociales.uba.ar (WP media API `?search=ubacyt`, cuando responde) tiene listas SIGEVA de integrantes de TODAS las UA:
- `https://www.sociales.uba.ar/wp-content/uploads/UBACYT-2010-2012.pdf` (A, con rol, ~631 proy), `UBACyT-2011-2014.pdf` (A, con rol, ~1063 proy), `UBACyT-2012-2015.pdf` (= `-20151.pdf`; integrantes sin rol, ~328 proy), `UBACyT-2013-2016.pdf` (sin rol, ~375 proy). Ojo: la API devuelve `/uploads/sites/1/...` → 404; sin `/sites/1/` funciona. `UBACYT-2011-2014.pdf` (mayúsculas) = sólo FSOC, subconjunto → no guardado. `Resultados-UBACyT-2014.pdf` = sólo director (C).
- Wayback CDX de sociales.uba.ar/wp-content/uploads (27.8k URLs) y blogs.dir: NO hay equivalentes para 2014-2017, 2016, 2017, 2018+. Probé nombres UBACyT-{2014-2017,2016,2016-2019,2017,2018,2008-2010}.pdf → 500 (sitio inestable, "Error de la base de datos"); reintentar más adelante.
- blogs.dir/219/files/2009/08/Proyectos-vigentes-01-10-151.pdf: FSOC vigentes oct-2015, dir+codir (168 proy) → redundante, no guardado.
- Becas UBACyT FSOC (Resultados-Becas-UBACYT-20xx, BecasUBACYT2023-FSOC, Becarios-UBACyT-2019): pares becario-director, no proyectos → no bajados (posible lead).

**Bajado además:**
- PC2026 RESCS-2026-1048 Anexos I (Mod I, 453 proy) y II (Mod II, 299), V (no acreditados) y VI (no admitidos); interdisciplinarios RESCS-2026-1471 Anexos I y II. Anexos III/IV (1048) y III (1471) = sólo director + monto → no guardados (C).
- Filtros no acreditados/no admitidos: PC2023 (Anexo IX/X), PC2020 (IX/X; URLs duplicadas mismo md5), PC2017 (Res 6903/17 Anexo IV/V).
- Psicología: PDFs dir+codir 2014-2017, PC2016, PC2017, PC2018, PC2023. Los de 2010-2012, 2011-2014, 2012-2015, 2013-2016 y PDTS tienen fuentes rotas (texto ilegible) → no guardados; vigentes/2020/Programacion_UBACyT_2020.pdf y vigentes/2026/... → 404.
- FADU IEH (ieh.fadu.uba.ar, WP media enumerada completa, 424 adjuntos): 13 fichas UBACyT/PDE con integrantes+rol → TSV + crudo. El resto de fichas son proyectos SI-FADU (PIA/PII/PIT), PICT, PIP (no UBACyT; posible lead para otras carpetas).

**Callejones:** fadu.uba.ar media API sin resultados; ciece.economicas (sólo director, C); economicas/fvet/fi/derecho/psi sin API o vacías; fmed (SSL), odon (no conecta); ffyb sólo espejo xlsx 2021/2024 + instructivos; exactas media 2024-2026 sólo becas/instructivos; cyt media "integrantes"/"equipo"/"programacion" sin listas nuevas (Montos-ano-2018/2019_Programacion-Cientifica-2016.xls = montos, C). Búsqueda web general sin listas de integrantes 2024-2026. CDX Wayback por dominio para agro/fvet/fmed/odon/fi/economicas/ffyb/fadu/cbc quedó sin correr (cortado por tiempo).

**Huecos que siguen:** integrantes TODOS 2014-2017, PC2016, PC2017, PC2018 (salvo 2021/2022), 2024-2026.
