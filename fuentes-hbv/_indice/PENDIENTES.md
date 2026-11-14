# Pendientes — grafo de investigadores

Estado al 2026-11-07. Recolección de fuentes terminada (flota de 8 agentes + supervisor): 302 archivos en 46 carpetas de `fuentes/`.
Leer primero: `fuentes/RESUMEN_COBERTURA.md`, `fuentes/FUENTES.md` (índice), `fuentes/_AUDITORIA.md`, `fuentes/_CONVENCIONES.md`.

## 1. Decisiones del usuario (bloquean tareas)

- [ ] **Integrantes SECyT-UNC (API pública).** Faltan ~7.350 proyectos de 2011–2026 (ya están 146 de 2026).
  - Trae nombre, CUIL, rol, dedicación y lugar de trabajo. Sería la mejor fuente nivel A fuera de UBA.
  - Se frenó por la política de permisos del entorno. Requiere autorización **explícita** del usuario, y aun así aparecerá el pedido de permiso.
  - Cómo retomar:
    `python3 -I scripts/recoleccion/W6/crawl_unc.py fuentes/SECyT-UNC/2011-2026_TODOS_SECyT-UNC-proyectos-aprobados-API.json fuentes/SECyT-UNC/2026_TODOS_SECyT-UNC-integrantes-API-PARCIAL.jsonl`
    - Retoma solo, salteando los códigos ya presentes en el jsonl. Pausa 0,25 s entre pedidos, ~1 h en total. Ya descarta la fecha de nacimiento.
    - Al terminar: renombrar el jsonl (sacar `PARCIAL`, poner rango de años) y actualizar `_registro.tsv`.
  - Estado viejo del crawl, por si hace falta: `scripts/recoleccion/W6/estado/`.
- [ ] **Becas** (`Becas-CONICET/` 170 MB, `EVC-CIN/` 61 MB, `PERHID-CIN/`, `INC-becas/`): dan pares director–becario, no proyectos. ¿Arista aparte o borrar?
- [ ] **`fuentes/SICyTAR-producciones/`** (coautorías 2011–2018, mismo `persona_id` que SICyTAR): ¿borrar o guardar para un tipo de arista futuro?
- [ ] **`_pendiente_decision/FONCyT-convocatorias-IR/`** (123 MB, ~650 PDFs de resultados de convocatorias FONCyT/Agencia; sólo código + investigador responsable). Rescatados del scratchpad. `clasif*.txt` = clasificación, `agdocs_log*.txt` = URL de origen, `leads_conv.md` = catálogo. ¿Conservar (mover a `fuentes/_leads/` o una carpeta de cruces) o borrar?

## 2. Conseguir lo que no es público (pedidos por mail / acceso a la información)

- [ ] **UBACyT con integrantes 2024–2026, todas las facultades:** pedir el export SIGEVA a la SECyT-UBA (subsi@rec.uba.ar). Es el sistema que generaba las listas 2021–2023.
- [ ] **PRI-FSOC (Sociales UBA):** sociales.uba.ar caído (timeout el 2026-11-07). Reintentar el sitio, o pedir las resoluciones a secinv@sociales.uba.ar. Faltan 2003–2011, 2015–2022, la Res CD 278/22 completa y 2024–2026.
- [ ] **PICT 2020+ (Agencia) y PIP/PUE/PIO 2020+ (CONICET):** sólo se publica el responsable. Pedido por Ley 27.275 de las nóminas de Grupo Responsable / GI.
- [ ] **UNLP:** los integrantes están sólo en SIGEVA (privado). Pedido a la Secretaría de CyT UNLP.

## 3. Descargas que quedaron a mano (fuentes concretas, sin bajar)

- [ ] **UNSL 2021, 2024, 2025** (PROICO / PI, nivel A): digesto.unsl.edu.ar bloquea bots. Bajar con navegador; las URLs están en `fuentes/PROICO-UNSL/_notas.md`.
- [ ] **USAL:** completar el anuario, faltan 376 de 985 artículos. Script `scripts/recoleccion/W8/scripts/parse_usal.py`. Los PDF traen el rol "Director", lo que lo subiría a nivel A.
- [ ] **UNTREF 2021–2022:** el host tiene certificado TLS inválido. Decidir si se baja igual.
- [ ] **UNCa PIDI 2024:** mismo problema de TLS.
- [ ] **UNLaM:** repositoriocyt detrás de Cloudflare; bajar con navegador.
- [ ] **UNVM 1998–2018:** resoluciones enlazadas en investigacion.unvm.edu.ar/proyectos/proyectos-internos.
- [ ] **UNLPam:** faltan años (2013, 2016, 2020, 2023–2025) y otras facultades, en actosresolutivos.unlpam.edu.ar.
- [ ] **UTN:** faltan el resto de las regionales (FRC, FRSF → sidn.frsf.utn.edu.ar/resoluciones, FRM, FRRo, FRLP).
- [ ] **UNR:** probar el digesto (digesto.unr.edu.ar) y los sitios de facultades para las resoluciones de acreditación de PID.
- [ ] **UNLP 2004–2018:** índice Wayback de secyt.presi.unlp.edu.ar (disposiciones de acreditación).
- [ ] **CONICET:** recorrer las ~150 unidades ejecutoras con web fuera de conicet.gov.ar (método en `fuentes/PIP/_notas.md`, scripts en `scripts/recoleccion/W3/`).
- [ ] **UCA:** repositorio CRIS con ~500 proyectos y coordinador; cruzando las páginas de cada investigador podría llegar a nivel B.
- [ ] **Tipos sin cubrir que podrían valer:** grupos de trabajo de CLACSO, Becas Salud Investiga (anexos en el Boletín Oficial), Banco PDTS, equipos por nodo de PISAC-COVID. Ver `fuentes/_CATALOGO_TIPOS.csv` (filtrar `cubierto_por = NADIE`).
- [ ] **Truco general:** en sitios WordPress, `/wp-json/wp/v2/media?search=` lista adjuntos no enlazados. Así salieron UBACyT 2021/2024, UCASAL y UNSTA. Probar en otras universidades (uap.edu.ar, ub.edu.ar, facultades UBA).

## 4. Procesamiento (siguiente etapa: armar el grafo)

- [ ] **OCR** de ~40 PDF escaneados. Instalar tesseract (`tesseract-ocr` + `tesseract-ocr-spa`) y usar ocrmypdf. Listado en `fuentes/_AUDITORIA.md`.
- [ ] **Parsear cada fuente a un formato común:** `proyecto_id, programa, año_inicio, año_fin, institución, persona_nombre, rol`.
  - Empezar por SICyTAR, que ya viene tabular, y por la semilla UBACyT 2023.
- [ ] **Identidad de personas:**
  - Usar el `persona_id` de SICyTAR como canónico.
  - Normalizar nombres (mayúsculas, acentos, "APELLIDO, Nombre").
  - Desambiguar homónimos (~3.500 en SICyTAR); DNI/CUIL sirven para matchear donde existan.
- [ ] **Deduplicar proyectos entre fuentes:**
  - Por código: PICT-AAAA-NNNN, código SIGEVA de PIP, código UBACyT 2002XXXXXXXXXXBA.
  - UBACyT: la semilla de febrero 2023 es anterior a la acreditación. Depurar con los anexos RESCS-2023-1384 y los "no acreditados".
  - PI-UNVM: varias resoluciones 2021–2022 repiten la convocatoria 2020.
- [ ] **Filtrar no aprobados:** UNMdP OCS 416/22 (columna resultado), EVC 2017/2018.
- [ ] **Proyectos gigantes** (INTA PE, PUE con 150–200 integrantes): ponderar las aristas (p. ej. 1/(n−1)) o excluir, para no generar cliques enormes.
- [ ] **Datos personales:** DNI, CUIL y emails (HTML crudo de CYTED) no van a los derivados ni a nada publicado.

## 5. Prolijidad menor

- [ ] Los `_progreso/W*.md` y `_SUPERVISION.md` son históricos de la recolección; se pueden archivar.
- [ ] El scratchpad de la sesión se pierde. Ya se rescataron los scripts (`scripts/recoleccion/`), el estado del crawl de la UNC y los PDF FONCyT. El resto (descargas intermedias) es descartable.
- [ ] Regenerar el índice tras cualquier cambio: `python3 -I scripts/generar_indice.py`.
