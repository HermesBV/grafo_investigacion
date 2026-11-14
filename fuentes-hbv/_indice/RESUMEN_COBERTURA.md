# Resumen de cobertura (cierre 2026-11-07)

Índice completo por archivo: `FUENTES.md` (regenerar con `python3 -I scripts/generar_indice.py`).
Auditoría del supervisor: `_AUDITORIA.md`. Catálogo de tipos de proyecto/financiamiento (102): `_CATALOGO_TIPOS.csv`.
Pistas no descargadas (listas sólo-director, URLs, pedidos pendientes): `_leads/`.

## Lo más valioso (nivel A = integrantes por proyecto)
| Fuente | Años | Alcance | Nota |
|---|---|---|---|
| SICyTAR (MinCyT datos abiertos) | 2008-2019 (inicio) | Nacional: PICT, PIP, PUE, PIO, PICTO, PID, INTA | ~19k proyectos, 130k participaciones, nombres + rol + persona_id estable. Ver `SICyTAR/_ANALISIS.md` |
| UBACyT | 2021, 2022, 2023 | TODOS | Mismo formato que la semilla |
| UBACyT / FILOCyT / DeCyT | 2010-2026 | FFYL-UBA, FDER-UBA | Única cobertura A de UBA post-2023 |
| SIIP-UNCuyo | 2016-2024 | TODOS | 1008 proyectos, 7561 integrantes con rol |
| PI-UNCo, PROICO-UNSL, PI-UNVM, PI-UNRN, UNAJ, PI-UNLPam | 2012-2027 | varios | ver FUENTES.md |
| CYTED | varios | Internacional | 5.349 filas de argentinos en 444 redes |
| Privadas: Austral, UCC, UCASAL, UNSTA, UAI | 2005-2026 | TODOS | |

## Nivel B (director + codirector)
UBACyT 2010-2026 TODOS (incl. 2024, 2025, 2026), SECyT-UNC 2011-2026 (7.494 proyectos), PID-UNLP 2022-2025, CAI+D-UNL 2020/2024,
PI-UNICEN, PI-UNMdP 2022, PPI-UNRC, UNQ, PDE-UBA 2016-2024, PUE 2020/2022.

## Huecos principales
1. UBACyT con integrantes, todas las facultades, 2024-2026: no público → pedir export SIGEVA a SECyT-UBA (subsi@rec.uba.ar).
2. PICT 2020+ y PIP/PUE 2020+ nacionales: sólo se publica el responsable (SICyTAR termina 2019) → acceso a la información (Ley 27.275).
3. PRI-FSOC: sociales.uba.ar caído; sólo 2013-2015 (A parcial) y 2022-2024 (B, Sociología) → secinv@sociales.uba.ar.
4. UNR, UNLP (integrantes en SIGEVA privado), NOA/NEA, UNSAM, UNGS, UNLaM: nada A/B.
5. Agencias provinciales: sólo director.

## Pendiente de decisión del usuario
- Completar crawl API SECyT-UNC (integrantes de ~7.300 proyectos; frenado por permisos).
- Becas (Becas-CONICET, EVC-CIN, PERHID-CIN, INC-becas): son director–becario, no proyectos. ¿Arista aparte o borrar?
- `SICyTAR-producciones/` (coautorías, fuera de alcance).
- ~650 PDFs de convocatorias FONCyT (código + IR) en scratchpad temporal: ¿conservar?

## Advertencias para el procesamiento
- Muchas fuentes traen DNI/CUIL (y el HTML crudo de CYTED, emails): no propagar a derivados.
- ~40 PDFs escaneados necesitan OCR (tesseract no instalado).
- Algunas listas incluyen no aprobados (UNMdP OCS 416/22, EVC 2017/2018): filtrar por resultado.
- Homónimos: ~3.500 pares nombre+apellido repetidos en SICyTAR.
- Proyectos gigantes (INTA PE, PUE con 150-200 integrantes): ponderar o excluir para no generar cliques enormes.
