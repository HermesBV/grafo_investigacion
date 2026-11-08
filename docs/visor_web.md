# Criterios del visor web UBACyT

## Datos y validación

El visor parte del Excel depurado y de los CSV generados por la notebook. No hay
muestreo, recorte de equipos ni exclusión de componentes pequeños. Se conservan
personas aisladas si un filtro deja un solo integrante de un grupo.

`scripts/build_web_data.py` reconstruye las participaciones del Excel, aplica la
misma identidad por nombre y los mismos puntajes del último procesamiento de la
notebook. Compara exactamente todos los nodos y prestigios y todas las aristas y
pesos contra los CSV. Comprueba duplicados exactos de origen, roles, IDs y fuentes.
Las diferencias detienen el proceso. No modifica las entradas.

## Unidades académicas

El PDF usa 50 variantes de escritura para las 14 unidades académicas: por ejemplo,
`FAC. DE CS. SOCIALES`, `FACULTAD DE CIENCIAS SOCIALES` y `CIENCIAS SOCIALES`.
El desplegable agrupa equivalencias explícitas en `canonical_unit` del generador.
Se equiparan prefijos, abreviaturas, tildes y tres erratas claras: `DISSEÑO`,
`NATURALESS` e `INGENIERÏA`. No se modifica el Excel. Las denominaciones originales
se conservan por proyecto en el JSON web (`project[5]`). Una unidad desconocida
produce un error para que se revise antes de incorporarla.

## Filtros

Los campos se combinan con AND. Unidad, código y título seleccionan **proyectos**.
Los códigos y títulos admiten coincidencias parciales. Un proyecto puede tener
versiones de título y unidad en distintos listados: cualquiera de sus versiones
observadas puede coincidir. Los roles se evalúan dentro del mismo proyecto que
pasó los demás filtros; no se trae un rol de un proyecto diferente.

El campo integrante busca nombres sin distinguir mayúsculas ni tildes. Esto solo
afecta la búsqueda, nunca la identidad de los nodos. Con “Ver sus colaboradores”
activado se muestran los integrantes de los proyectos donde coincide una persona
(si hay filtro de rol, solo los integrantes que lo cumplen en ese proyecto).
Al desactivarlo quedan exclusivamente las personas cuyo nombre coincide.

El prestigio mantiene su valor acumulado original al filtrar. El peso de cada
arista se vuelve a calcular por proyectos seleccionados: se cuentan únicamente
grupos visibles compartidos. Los nodos que permanecen solos también se muestran.
Las tarjetas de personas distinguen métricas globales y colaboradores de la vista.

Los campos **Mínimo de conexiones** y **Mínimo de proyectos** filtran personas por
sus totales acumulados en toda la base. Conexiones significa colaboradores
distintos (grado no ponderado), no suma de pesos. Proyectos significa proyectos
distintos por persona, sin multiplicar por años ni roles. Se aplican ambos mínimos
con AND y junto con los demás filtros, también al incluir colaboradores de una
búsqueda por nombre. El límite es inclusivo: un mínimo de 10 conserva valores de
10 o más. No se hace una poda iterativa según las aristas que quedan visibles.

Cada campo admite cualquier entero desde 0 hasta el máximo observado, calculado
automáticamente al cargar los datos. En la base actual los rangos son **0–75
conexiones** y **0–5 proyectos**. Cero o un campo vacío no restringen. No se aceptan
negativos, decimales ni valores superiores al máximo: el visor muestra un aviso y
conserva la última vista válida hasta corregir el número. “Limpiar” restablece ambos
mínimos a cero. Las aristas entre personas excluidas se ocultan; los pesos entre
personas que permanecen siguen contando proyectos seleccionados compartidos.

## Tamaños, colores y nombres

Cada persona tiene su nombre completo como etiqueta. Las etiquetas se distribuyen
por nivel de zoom para reducir superposiciones; la persona seleccionada o señalada
siempre muestra su nombre. El botón `Aa` aumenta la densidad de etiquetas. Todos
los nombres visibles se pueden consultar también en la lista lateral, de 30 en 30,
con selección por teclado y sin depender del dibujo WebGL.

Radio del nodo: `0,4 + 3,4 × raíz(prestigio / prestigio máximo global)`.
Para facilitar la lectura de redes filtradas, ese radio se multiplica por 3 cuando
hay menos de 150 personas visibles y por 1,5 entre 150 y 1.499. Se conserva la
relación entre tamaños de personas con distinto prestigio dentro de la vista.
El color usa una interpolación continua verde → ocre → terracota, con escala
logarítmica del prestigio. La escala de color conserva los mismos límites entre filtros.

Grosor de arista: `0,45 + 1,15 × log2(peso)`, con el mismo factor de lectura que
los nodos para redes pequeñas. El color usa tres clases: 1 (gris
verdoso), 2 (verde) y 3 o más (terracota). El grosor distingue pesos superiores a 3.
La selección atenúa las demás personas y conexiones sin cambiar sus valores.
Los tamaños cambian con el zoom del visor. Las leyendas indican las variables.

## Posiciones y centralidad

La posición no es una coordenada geográfica. `web/scripts/layout.mjs` calcula una
distribución ForceAtlas2 multiescala ponderada por peso, con semilla 202123.
Louvain (resolución 1, semilla fija) identifica comunidades. Se calculan 300
iteraciones de ForceAtlas2 sobre el grafo agregado de comunidades; discos de radio
proporcional a la raíz de su población se separan sin superponerse, conservando
esa disposición inicial. Dentro de cada disco se ejecutan 200 iteraciones de
ForceAtlas2 (modo LinLog y Barnes–Hut para más de 100 nodos). Los vínculos entre
comunidades se conservan todos. Esto ayuda a separar grupos en la vista general
sin recortar personas o aristas. Las personas se atraen según sus vínculos. El cálculo
ocurre al construir el sitio; el navegador recibe posiciones guardadas.

La alternativa por centralidad usa **centralidad de grado no ponderada global**:
`vecinos distintos / (personas de la base − 1)`. Conserva el ángulo de ForceAtlas2
y asigna el radio `0,09 + 0,91 × (1 − log(1 + grado) / log(1 + grado máximo))`.
Quienes tienen más colaboradores quedan más cerca del centro. Es una distribución
radial, no un algoritmo de comunidades ni otra medida del prestigio.

Ambas posiciones se mantienen al filtrar para evitar que cambie la referencia de
cada persona. El encuadre se ajusta a los nodos que quedan. La centralidad global
no se vuelve a calcular al aplicar filtros. Grado y prestigio miden cosas distintas.

## Estructura y reproducción

Sitio estático con Vite, Sigma.js 3.0.2, Graphology y JavaScript. WebGL dibuja nodos
y aristas; Canvas 2D dibuja las etiquetas para mayor compatibilidad. Los filtros se ejecutan
en un Web Worker para no bloquear la interacción. La publicación mediante GitHub
Actions verifica todos los datos procesados y recalcula las posiciones. El
workflow utiliza el lockfile y versiones exactas de las dependencias principales.

El Excel de trabajo permanece local y no se publica. `scripts/validate_web_data.py`
usa únicamente los CSV, el JSON y la configuración procesada: reconstruye todos
los pares compartidos por proyecto y los prestigios por rol y comprueba personas,
conexiones, pesos, grados, participaciones y hashes. Así la publicación no requiere
acceso al consolidado completo. La regeneración desde el Excel se ejecuta localmente
con la notebook y `scripts/build_web_data.py` antes de subir nuevos datos procesados.

`web/public/data/graph.json` usa arrays compactos para reducir la transferencia:

- `nodes`: `[Id, nombre, prestigio, grado, grado ponderado, cantidad de proyectos,
  xForce, yForce, xCentralidad, yCentralidad]`.
- `projects`: `[código, títulos originales normalizados en espacios, índices de
  unidades canónicas, miembros, años, denominaciones originales de unidad]`.
- Cada miembro: `[índice de persona, índices de roles observados, años observados]`.
- `edges`: `[índice persona A, índice persona B, peso acumulado]`.
- `meta`: recuentos, sumas de control, años, escala de roles, fuentes y SHA-256 de
  los archivos de entrada. `roles` y `units` son los catálogos de índices.

Para años o grupos nuevos, ejecutar primero la notebook, luego el generador de
datos y el layout. El README contiene los comandos. Se deben agregar las fuentes
anuales al catálogo. Si se introduce otro tipo de proyecto, adaptar las reglas y
el esquema antes de publicar: el generador se detiene ante tipos nuevos.
