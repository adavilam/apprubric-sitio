# AppRubric — sitio comercial

Página de presentación de **AppRubric**, sistema de gestión evaluativa alineado al Instructivo de Evaluación del MINED (Nicaragua).

- Sitio publicado: https://apprubric.net
- Página de Facebook: https://www.facebook.com/AppRubric
- Contacto: WhatsApp +505 5819 6269 · apprubricnic@gmail.com

Es un sitio estático de un solo archivo (`index.html`), sin dependencias ni paso de compilación. No contiene datos de estudiantes ni de ningún centro educativo: los ejemplos son ilustrativos.

## Marca

En `marca/`: isotipo (`isotipo.svg`, PNG de 512 y 1024), logotipo horizontal para fondo claro (`logo-horizontal.svg`) y oscuro (`logo-horizontal-blanco.svg`). En la raíz: `favicon.ico` (16, 32 y 48 px), `favicon.svg` y `apple-touch-icon.png`. Todo sale de `marca/generar_marca.py`.

Concepto: una rúbrica de 3 criterios × 4 niveles (AI, AF, AS, AA). Las cuatro celdas marcadas dibujan un visto bueno (✓) que es también una línea de progreso hasta el dorado del Aprendizaje Avanzado: la evaluación del MINED, resuelta y trazable.

## Publicación

Se sirve desde `public_html` de la cuenta cPanel de AppRubric (dominio principal `apprubric.net`). Para actualizarlo, subir `index.html`, `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, la carpeta `marca/` (sin `generar_marca.py`) y `.htaccess` a `public_html` con el Administrador de archivos. El subdominio `demo.apprubric.net` vive en otra carpeta y no se toca.

La versión anterior en Vercel (`prospecto-apprubric.vercel.app`) quedó retirada.

## Licencia

Todos los derechos reservados. El código y los textos se publican para consulta; no se autoriza su reutilización sin permiso del autor.
