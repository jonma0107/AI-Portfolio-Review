# AI Portfolio Review

Este proyecto es una aplicación web que permite a los usuarios ingresar el dominio de su portafolio y recibir una revisión detallada generada por la API de OpenAI. 

## Estructura del Proyecto

- **index.html**: Archivo de plantilla HTML que define la estructura de la interfaz de usuario.
- **views.py**: Contiene las vistas de Django que manejan las solicitudes HTTP y la lógica del backend.
- **models.py**: Define el modelo de datos `Review` utilizado para almacenar las revisiones en la base de datos.
- **urls.py**: Define las rutas URL para las vistas de la aplicación.
- **main.js**: Archivo JavaScript que maneja la lógica del frontend, incluyendo la captura de eventos.

## Flujo del Backend

1. **Solicitud de Revisión**:
   - El usuario ingresa el dominio de su portafolio en el formulario de la página principal (`index.html`).
   - Al enviar el formulario, se realiza una solicitud POST a la vista `submit_url` en `views.py`.

2. **Procesamiento de la Solicitud**:
   - En `views.py`, la función `submit_url` recibe la solicitud y extrae el dominio del portafolio.
   - Se toma una captura de pantalla del sitio web utilizando `Playwright` y se sube a un bucket de `S3 de AWS`.
   - La URL de la imagen subida se utiliza para solicitar una revisión detallada a la API de OpenAI.

3. **Generación de la Revisión**:
   - La función `get_openai_review` en `views.py` envía una solicitud a la API de OpenAI con la URL de la imagen.
   - La respuesta de la API, que contiene la revisión en formato Markdown, se convierte a HTML utilizando la librería `markdown`.

4. **Almacenamiento y Respuesta**:
   - La revisión generada y la URL de la imagen se almacenan en la base de datos utilizando el modelo `Review`.
   - Se envía una respuesta JSON al frontend con la revisión en HTML y la URL de la imagen.

5. **Visualización**:
   - En `main.js`, el frontend recibe la respuesta y actualiza el DOM para mostrar la revisión y la imagen.  

## Herramientas Implementadas

- **Django**: Framework web utilizado para manejar el backend y la lógica de la aplicación.
- **Playwright**: Herramienta para automatizar navegadores, utilizada para tomar capturas de pantalla de los sitios web.
- **AWS S3**: Servicio de almacenamiento en la nube utilizado para almacenar las capturas de pantalla.
- **OpenAI API**: API utilizada para generar revisiones detalladas de los portafolios.
- **Markdown**: Librería de Python utilizada para convertir texto Markdown a HTML.
- **Tailwind CSS**: Framework CSS utilizado para el diseño y estilo de la interfaz de usuario.

## Seguridad

### Sanitización del HTML

Para evitar vulnerabilidades de seguridad como XSS (Cross-Site Scripting), es importante sanitizar el HTML generado a partir del texto Markdown. Esto se puede lograr utilizando la librería `bleach` en Python, que permite limpiar el HTML y eliminar cualquier contenido potencialmente peligroso. 

### Protección CSRF

CSRF (Cross-Site Request Forgery) es un tipo de ataque que permite a un atacante realizar acciones no autorizadas en nombre de un usuario autenticado. Django proporciona mecanismos integrados para proteger las aplicaciones contra este tipo de ataques.

#### Opciones para Desarrollo

- **Uso de `@csrf_exempt`:** Durante el desarrollo, puedes usar el decorador `@csrf_exempt` en vistas específicas para desactivar temporalmente la protección CSRF. Esto puede ser útil para pruebas rápidas, pero no es seguro para producción.

#### Opciones para Producción

- **Uso de Tokens CSRF:** En producción, es crucial utilizar tokens CSRF para proteger las solicitudes POST. Django genera automáticamente un token CSRF para cada sesión de usuario, que debe incluirse en los formularios HTML. Asegúrate de incluir `{% csrf_token %}` dentro de cada formulario en tus plantillas HTML.
  
- **Middleware de CSRF:** Asegúrate de que `'django.middleware.csrf.CsrfViewMiddleware'` esté habilitado en la lista de `MIDDLEWARE` en `settings.py`. Este middleware verifica automáticamente los tokens CSRF en las solicitudes POST.

## Configuración Previa

1. **Configuración de AWS**:
   - Configura tus credenciales de AWS para permitir la subida de imágenes a S3.

# Configuración de Variables de Entorno en Django

Este proyecto utiliza variables de entorno definidas en un archivo `.env` para mantener segura la configuración sensible como la `SECRET_KEY` y la variable `DEBUG`.


Este README proporciona una visión general del flujo del backend, las herramientas utilizadas y las consideraciones de seguridad en el proyecto.