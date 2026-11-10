# Criterios del grafo de proyectos UBACyT

## Base y duplicados

La entrada es la hoja `Datos` del Excel consolidado. Se conserva un respaldo
íntegro antes de modificarlo. Se eliminan solo copias que coincidan exactamente
en año del listado, código de proyecto, convocatoria, integrante, rol, título,
unidad académica, `Tipo de proyecto` y `fuente_completa`. Se ignoran únicamente `Página PDF` y `Fila en página` para
detectar esas copias, según el criterio confirmado por el usuario.

Se conserva la primera aparición y sus referencias al PDF. No se normalizan
espacios, mayúsculas o saltos de línea para decidir si una fila es duplicada.
Las filas eliminadas se guardan en la auditoría de cada ejecución. El mismo
registro en otro año se conserva en la base. La notebook modifica el Excel
original solo cuando hay duplicados; un respaldo existente nunca se reemplaza.

`Control` conserva los recuentos de la extracción de los PDF originales y agrega
las filas conservadas después de la limpieza. La base puede incluir PDE y
PIUBAS; sus filas se conservan en el Excel, pero no integran estos grafos.

## Personas y proyectos

- Cada nodo representa un nombre completo normalizado: Unicode NFC, mayúsculas
  y espacios consecutivos o saltos de línea reducidos a un espacio.
- Se conservan tildes y puntuación. No se aplican coincidencias aproximadas.
  Por ejemplo, un nombre con y sin tilde puede seguir representado por dos nodos.
- Los nombres no contienen un identificador personal oficial. Los homónimos
  y las variantes de escritura requieren revisión. `ALIAS_PERSONAS` permite
  registrar equivalencias revisadas manualmente.
- `Id` se deriva del nombre normalizado mediante SHA-256. Es estable entre
  ejecuciones y se comprueba que no haya colisiones.
- Un grupo es un proyecto identificado por `(tipo de proyecto, código)`.
  Su aparición en varios años no crea grupos nuevos.
- El grafo es acumulado: reúne a todas las personas observadas en un proyecto
  en los años seleccionados. No exige que dos integrantes estén registrados
  en el mismo corte anual. No representa una prueba de colaboración simultánea.
- `ANIOS_INCLUIDOS = None` utiliza todos los años disponibles. Puede indicarse
  una lista explícita de años para restringir el grafo, sin borrar otros años
  de la base.

## Prestigio de los nodos

Puntajes definidos por el usuario:

| Rol | Puntos |
| --- | ---: |
| Estudiante de grado | 1 |
| Estudiante | 1 |
| Investigador en formación | 2 |
| Investigador tesista | 2 |
| Investigador de apoyo | 2 |
| Investigador asesor | 3 |
| Investigador formado | 3 |
| Codirector | 5 |
| Director | 6 |
| Sin rol informado | 1 |

Se equiparan las variantes de género y escritura de los roles, como
`INVESTIGADOR/A FORMADO/A`, `CO-DIRECTOR` y `CODIRECTOR`. La variante tipográfica
de origen `DIRECTOR/A/A` se interpreta como director. Las tildes se omiten solo
para comparar los nombres de los roles, no los de las personas.

Cada persona-proyecto aporta una sola vez. Si el mismo vínculo tiene varios
roles o cambia de rol entre años, se utiliza el **mayor puntaje observado**.
Todos los roles y años observados quedan en la tabla de participaciones de la
auditoría. No se suman varios roles del mismo proyecto ni se multiplica por
la cantidad de años. Las celdas vacías de la base siguen vacías; su participación
aporta 1 punto cuando no hay un rol de mayor puntaje para esa persona-proyecto.

`prestigio(persona) = suma por proyecto distinto de
máximo puntaje de rol observado × multiplicador de nodos del tipo de proyecto`.

La notebook se detiene y muestra los roles que no tengan un puntaje definido.
Un rol nuevo no recibe cero ni se interpreta automáticamente como otro rol.

## Conexiones y peso

El grafo es **no dirigido**, sin autoenlaces. Cada par de personas aparece una
sola vez en el CSV. Hay una conexión cuando comparten al menos un proyecto.

`peso(persona A, persona B) = suma de los multiplicadores de conexiones de los
proyectos distintos que comparten`.

Con la configuración actual, cada proyecto UBACyT compartido suma **1**.
Compartir el mismo proyecto en dos o tres años sigue sumando 1. La cantidad de
roles o de filas de una persona dentro del proyecto tampoco aumenta ese peso.
El atributo `peso` pertenece a la conexión. Se conservan también los nodos
aislados, aunque no aparezcan en el archivo de conexiones.

## Otros tipos de proyecto

Por ahora solo se incluye `UBACYT`. En `PESOS_TIPO_PROYECTO` sus multiplicadores
son `nodos = 1` y `conexiones = 1`.

Para incorporar otros tipos:

1. Informar `Tipo de proyecto` explícitamente en cada fila (`PIP`, `PICT`, `PRII`, etc.).
2. Definir explícitamente sus multiplicadores de nodos y conexiones.
3. Agregar el tipo a `TIPOS_INCLUIDOS`.
4. Asignar puntaje a los roles nuevos que la notebook señale.

El tipo se lee de la columna, no se infiere del código. La identidad compuesta
impide mezclar dos financiamientos que usen el mismo código. PDE y PIUBAS se
conservan en la base, excluidos de estos primeros grafos. Un tipo incluido sin
multiplicadores genera un error visible. Si cambia la estructura del Excel, hay que actualizar la
lista de columnas y la clave de duplicados; no se descartan columnas nuevas
silenciosamente.

La migración de la base histórica de nueve columnas se reproduce con
`python scripts/migrate_project_types.py`. Agrega la décima columna, respalda el
libro y comprueba que todas las celdas originales permanezcan iguales. Solo esa
migración infiere UBACYT, PDE y PIUBAS de los códigos históricos. Si la columna
ya existe, valida su contenido sin reescribir el libro. Las nuevas bases deben
informarla desde su construcción. Ver [modelo de datos](modelo_datos.md).

## Archivos y reproducción

- `notebooks/ubacyt_grafo.ipynb`: proceso completo, con parámetros y resultados
  de la ejecución. Abrir desde el proyecto o su carpeta `notebooks`.
- `output/grafos/ubacyt/nodos_ubacyt.csv`: `Id`, `Label`, `prestigio`.
- `output/grafos/ubacyt/conexiones_ubacyt.csv`: `Source`, `Target`, `Type`, `peso`.
  `Type` vale `Undirected`.
- `output/grafos/ubacyt/auditoria/<ejecución>/`: filas eliminadas, participaciones
  persona-proyecto con su contribución, roles detectados, registros excluidos,
  hashes y resumen de validación.
- `output/xlsx/respaldos/`: respaldo del Excel anterior a cada limpieza que
  elimine registros.

Los CSV usan coma como separador y UTF-8 con BOM. Las comas incluidas en los
nombres se conservan entre comillas de CSV. Para que una aplicación utilice
el peso de las conexiones, seleccionar la columna `peso` como atributo de peso.

Instalar `requirements-grafos.txt` en el entorno Python elegido y seleccionar
ese entorno en Jupyter o en el editor de notebooks. Si el archivo de entrada
cambia de nombre, actualizar `RUTA_EXCEL`. El resto del proceso toma todos los
años disponibles sin necesitar cambios por año.

Antes de ejecutar con `BORRAR_DUPLICADOS_EN_EXCEL = True`, cerrar el consolidado
en Microsoft Excel: Windows impide reemplazar un libro que permanezca abierto.
La generación de grafos utiliza los datos depurados en memoria; la opción de
escritura controla si se actualiza también el archivo de entrada.

Antes de exportar se comprueban la deduplicación idempotente, la unicidad de
las participaciones y los nodos, la ausencia de autoenlaces, la coherencia de
los identificadores y el peso de **cada conexión** mediante la intersección
de los proyectos de sus extremos. Se verifica que duplicar un corte anual no
infle el grafo y se ejecutan casos pequeños con resultados conocidos. Después
de exportar se releen los dos CSV y el Excel limpio y se comparan sus datos.

## Cobertura e importación de Excel

Ver [actualización local y cobertura](actualizacion_local.md). La columna `fuente_completa` distingue nóminas completas y fuentes con dirección/codirección. El grafo acumula solamente personas observadas, sin imputar equipos de años anteriores.
