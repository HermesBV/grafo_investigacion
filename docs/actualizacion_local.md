# Actualización local y cobertura de las fuentes

## Doble clic

En la raíz del proyecto hay dos accesos propios de esta computadora, ignorados
por Git junto con la carpeta `local/`:

- `ACTUALIZAR_BASES.local.cmd`: importa los Excel verificados del catálogo,
  ejecuta toda la notebook existente, reconstruye los datos web y las posiciones,
  coteja cada nodo y arista, ejecuta las pruebas y compila la página. No publica.
- `PUBLICAR_GITHUB.local.cmd`: comprueba cuenta bustosthl, rama main y remoto,
  valida los datos, prueba y compila, confirma los cambios de archivos ya
  versionados y hace push sin forzar. GitHub Actions despliega la página.
  Los archivos nuevos deben revisarse y agregarse a Git explícitamente.

La primera vez, ejecutar `local/CONFIGURAR_GITHUB.cmd` e iniciar sesión como
**bustosthl**. La autorización queda en GitHub CLI, no en el repositorio.
Si el remoto avanzó o una verificación falla, la publicación se detiene con
un mensaje; no mezcla historiales automáticamente ni sube los Excel.

Cerrar el consolidado antes de actualizar. Cada ventana muestra errores y queda
abierta al terminar. Los procesos se ejecutan en orden y se detienen si fallan.
Los accesos utilizan el Python disponible en esta computadora; para portarlos,
adaptar su intérprete y preparar Python 3.12 con `requirements-grafos.txt`,
Node 24 y las dependencias de `web`. El proceso portable también se ejecuta con
`python scripts/actualizar_bases.py`.

## Qué significa fuente_completa

La hoja Datos añade `fuente_completa`:

- `completa`: listados PDF de 2021, 2022 y 2023 con integrantes y roles.
- `sólo dirección y codirección`: Excel oficiales con cortes 26/02/2024 y 31/08/2026.

“Completa” describe el alcance publicado por la fuente, no garantiza que los
equipos no tengan errores u omisiones. No se inventan integrantes de 2024 o 2026 a
partir de la composición de 2023. La columna se agrega a la clave de duplicados;
se siguen ignorando únicamente Página PDF y Fila en página.

El importador conserva intactos los archivos originales y todas sus filas. Separa
codirectores únicamente por punto y coma y conserva las comas apellido/nombre.
En las filas provenientes de Excel, Página PDF vale 0 (no corresponde) y Fila en
página referencia la fila real del Excel original, incluida su cabecera.
La importación es idempotente y respalda la base antes de cambiarla.

El filtro de cobertura selecciona observaciones persona/proyecto/rol de esa
fuente. Si una persona sólo figura como integrante en una fuente completa,
no aparece por ese motivo al seleccionar sólo dirección y codirección. La red
filtrada recalcula conexiones; el prestigio y los mínimos siguen siendo globales.
Las fuentes parciales producen equipos y colaboraciones incompletos: la ausencia
de una persona no demuestra que haya abandonado un proyecto.

El JSON web versión 3 conserva tipo y coberturas por proyecto, y añade a cada
miembro observaciones `[año, cobertura, índice de rol]`. Esto permite combinar
cobertura y rol sobre la misma observación, sin cruzar roles de distintas fuentes.

## Año 2025 pendiente

Revisión del 10/11/2026: el catálogo oficial de adjuntos con búsquedas `vigentes`
y `proyectos` no ofrece un listado anual 2025 verificable. Hay cortes 2024 y 2026.
No se atribuyen datos de estos años a 2025. Si se consigue el archivo, registrar
su URL, SHA-256, hoja y recuento de filas en `fuentes-ubacyt.json`; el importador
admite entradas de nivel proyectos para 2024 y 2026 con la estructura revisada.

Fuentes: https://cyt.rec.uba.ar/wp-json/wp/v2/media?search=vigentes&per_page=100
y https://cyt.rec.uba.ar/wp-json/wp/v2/media?search=proyectos&per_page=100.

El usuario confirmó que los cortes solicitados son 2024 y 2026. Se incorporan ambos; no se espera una fuente 2025 para completar esta actualización. La publicación quedó pendiente por indicación del usuario.
