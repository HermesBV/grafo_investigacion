# Tramas de investigación · UBACyT

Visor de personas y colaboraciones construido a partir de los listados de proyectos
vigentes de la Universidad de Buenos Aires de **2021, 2022, 2023, 2024 y 2026**.

Destino de publicación: **https://bustosthl.github.io/grafo_investigacion/**.

La base actual contiene **16.959 personas, 119.769 conexiones y 3.225 proyectos**.
Las conexiones son no dirigidas. Cada proyecto distinto compartido aporta un punto
al peso de la conexión. El prestigio suma los puntajes de los roles por proyecto
distinto; los criterios y las limitaciones están en
[docs/criterios_grafo_ubacyt.md](docs/criterios_grafo_ubacyt.md).

## Fork HermesBV: base UBACyT ampliada (v2)

`output/xlsx/UBACYT-consolidado-v2.2.xlsx` amplía la base a **2010–2026** (72.187 filas, 7.258 proyectos,
24.596 personas, 185.827 conexiones), en el mismo formato de 11 columnas, sin pisar los datos existentes. Detalle, criterios
y limitaciones en [docs/ampliacion_ubacyt_v2.md](docs/ampliacion_ubacyt_v2.md). Fuentes crudas en
[fuentes-hbv/](fuentes-hbv/README.md).

## Visor

- Tamaño y color de cada nodo según su prestigio acumulado. Nombre completo como etiqueta.
- Grosor de las aristas según su peso; color para pesos 1, 2 y 3 o más.
- Distribuciones por colaboraciones (comunidades Louvain y ForceAtlas2 ponderado) y por centralidad de grado global.
- Filtros de selección múltiple por tipo de proyecto, unidad académica y rol;
  campos de integrante, código y título. OR dentro de cada desplegable, AND entre campos.
- Mínimos de conexiones y proyectos por persona, con cualquier entero del rango
  completo de la base (actualmente 0–75 colaboradores y 0–6 proyectos). Se aplican
  ambos mínimos sobre los totales acumulados; cero no restringe.
- Detalle de las personas, sus roles y proyectos; detalle de las conexiones al tocarlas.
- Diseño adaptable al celular. Los filtros se abren con el botón “Filtros”.

JavaScript, [Sigma.js](https://www.sigmajs.org/) y
[Graphology](https://graphology.github.io/) dibujan la red con WebGL 2.
Python prepara y verifica los datos. [Vite](https://vite.dev/) compila un sitio
estático: no requiere servidor de Python ni base de datos en producción.
Las posiciones se calculan antes de publicar y los filtros se procesan en un Web Worker.

## Ejecutar localmente

Requisitos: Python 3.12, Node 24 y pnpm 11.25.0.

```sh
python -m pip install openpyxl==3.1.5
npm install --global pnpm@11.25.0
cd web
pnpm install --frozen-lockfile --ignore-scripts
pnpm dev
```

Abrir la URL que imprime Vite, que termina en `/grafo_investigacion/`.
El JSON con los datos y las posiciones ya está incluido para explorar localmente.
La publicación utiliza los CSV y ese JSON. El Excel consolidado se mantiene como
entrada local y no forma parte del repositorio público.

## Actualizar las bases

1. Ubicar el Excel de trabajo local en
   `output/xlsx/UBACYT-consolidado-2021-2022-2023.xlsx` e incorporar los años nuevos,
   manteniendo las once columnas de la hoja `Datos`, incluidas **Tipo de proyecto** y **fuente_completa**.
   La base histórica de nueve columnas se migra una sola vez con
   `python scripts/migrate_project_types.py`; crea respaldo y verifica todas las celdas originales.
2. Actualizar `fuentes-ubacyt.json` con las fuentes de los nuevos listados.
3. Instalar `requirements-grafos.txt` y ejecutar toda la notebook
   [notebooks/ubacyt_grafo.ipynb](notebooks/ubacyt_grafo.ipynb).
4. Reconstruir los datos y posiciones del visor:

```sh
python scripts/build_web_data.py
python scripts/validate_web_data.py
cd web
pnpm layout
pnpm test
pnpm build
pnpm preview
```

`build_web_data.py --excel ruta/al/consolidado.xlsx` admite otro nombre de archivo.
La notebook permite cambiar `RUTA_EXCEL` o definir la variable `GRAFO_EXCEL` con esa ruta.
Si se usan equivalencias de personas en `ALIAS_PERSONAS`, pasarlas también mediante
`--aliases ruta/aliases.json`. Las unidades académicas nuevas requieren revisar sus
equivalencias. Para otros financiamientos, completar `Tipo de proyecto` en cada
fila, definir los multiplicadores de nodos y conexiones y agregarlos a los tipos
incluidos en la notebook. Actualmente solo se incluye UBACYT (1 y 1); no se han
asignado pesos a PIP, PICT o PRII. La clave de proyecto es `(tipo, código)`.
El contrato para integrar otras bases está en [docs/modelo_datos.md](docs/modelo_datos.md).

El generador compara **cada nodo, su prestigio y cada arista con su peso** con los
CSV de la notebook. Ante una diferencia detiene la construcción. No descarta datos
para hacer coincidir los resultados.

## GitHub Pages y Actions

El workflow [.github/workflows/pages.yml](.github/workflows/pages.yml) coteja todos
los nodos, prestigios y conexiones del JSON con los CSV y las participaciones
procesadas, calcula el layout, ejecuta las pruebas y compila el sitio. En `main`
publica mediante GitHub Pages. En los pull requests solo valida y construye.

El repositorio debe llamarse `grafo_investigacion` dentro de la cuenta `bustosthl`.
En **Settings → Pages → Build and deployment → Source**, seleccionar **GitHub Actions**.
No se necesita un token personal ni secretos para el despliegue: el workflow usa
los permisos temporales de `GITHUB_TOKEN`. Si el repositorio es público, el sitio y
los datos versionados también lo son.

Para la primera publicación desde una sesión de GitHub CLI de **bustosthl**:

```sh
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
python scripts/publish_github.py
```

El publicador comprueba la cuenta, la rama y el destino remoto; crea el repositorio
público si no existe, sube `main` sin forzar historial y activa Pages con Actions.
No cambia las credenciales globales de Git. Después de publicar hay que comprobar
que la ejecución del workflow haya terminado correctamente.

## Datos y documentación

- Excel consolidado: entrada de trabajo local, fuera del repositorio público.
- [Nodos](output/grafos/ubacyt/nodos_ubacyt.csv) y [conexiones](output/grafos/ubacyt/conexiones_ubacyt.csv).
- [Criterios del grafo](docs/criterios_grafo_ubacyt.md) y [criterios del visor](docs/visor_web.md).
- [Catálogo de fuentes oficiales](fuentes-ubacyt.json).

Los PDF originales se enlazan en el catálogo y en el visor; los respaldos,
auditorías y dependencias locales quedan fuera del repositorio.

## Actualización con doble clic

Ver [accesos locales, ejecución de la notebook y cobertura](docs/actualizacion_local.md). El consolidado mantiene su nombre histórico 2021–2023 y ahora integra también los cortes 2024 y 2026. No se incorporó un listado 2025 sin fuente verificable.
