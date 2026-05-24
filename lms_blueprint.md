# Blueprint funcional de plataforma LMS SINTRAC

Este documento traduce el contenido entregado para que se implemente en una plataforma similar a la referencia visual, con foco en control administrativo y gestión de contenidos.

## 1) Roles y permisos

### Admin (único rol con control total)
- Crear usuarios (único permitido).
- Editar/activar/desactivar usuarios.
- Crear cursos, módulos y clases.
- Cargar URL de videos de YouTube por clase.
- Crear y administrar sección de descargas (links de PDF, documentos, videos, etc.).
- Publicar/ocultar contenidos.

### Estudiante
- Iniciar sesión.
- Ver cursos asignados/publicados.
- Reproducir clases con video embebido desde YouTube.
- Acceder a descargas publicadas.
- Ver progreso propio.

## 2) Estructura de contenido inicial

### Curso principal
- **Nombre del curso:** Escuela Sindical Aprendamos Luchando
- **Objetivo:** Generar conocimiento de estrategias de lucha y organización, funcionamiento del Estado, conceptos generales de clase, género y gestión práctica del trabajo sindical.
- **Público objetivo:** Dirigentes sindicales y trabajadores del ámbito privado y estatal, especialmente trabajadores a honorarios.
- **Duración estimada:** 8 clases.
- **Horario referencial:** 16:30 a 18:30, una vez por semana.

### Módulo 0: Inauguración
- Presentación de la escuela.
- Discurso de apertura.
- Artista invitado.
- Video de exposición de luchas de la organización.
- Cierre/finalización.

### Clases
1. La productividad y formas de medirla — Gonzalo Durán (Fundación SOL).
2. Normas laborales generales y procedimientos para la acción sindical — María Estrella Zúñiga.
3. Qué es el Estado, su funcionamiento y repercusión en trabajadores — Cristian Cepeda.
4. Estrategias de organización y lucha — Sergio Alegría.
5. Formación del líder sindical: coherencia y consecuencia — Isolina Acosta.
6. Rol y funciones de la Dirección del Trabajo — Hernán Larraín.
7. Trabajo a honorarios y tipos de contrato — Diego López.
8. Reformas laborales y movimientos sindicales.

## 3) Modelo de datos mínimo recomendado

### users
- id
- full_name
- email (único)
- password_hash
- role (`admin` | `student`)
- status (`active` | `inactive`)
- created_by (FK users.id, nullable en primer admin)
- created_at

### courses
- id
- title
- description
- objective
- audience
- schedule_text
- published
- created_by
- created_at

### lessons
- id
- course_id
- order_index
- title
- speaker_name
- summary
- youtube_url
- youtube_embed_url
- duration_minutes
- published

### download_links
- id
- course_id (nullable si descarga global)
- lesson_id (nullable)
- title
- resource_type (`pdf` | `doc` | `video` | `link` | `ppt` | `zip`)
- url
- published
- created_by
- created_at

## 4) Endpoints clave (API)

### Auth
- `POST /auth/login`
- `POST /auth/logout`

### Usuarios (solo Admin)
- `POST /admin/users`
- `GET /admin/users`
- `PATCH /admin/users/:id`

### Cursos/Clases (solo Admin para escritura)
- `POST /admin/courses`
- `POST /admin/courses/:courseId/lessons`
- `PATCH /admin/lessons/:id`
- `GET /courses` (estudiantes)
- `GET /courses/:id` (estudiantes)

### Descargas (solo Admin para escritura)
- `POST /admin/downloads`
- `PATCH /admin/downloads/:id`
- `DELETE /admin/downloads/:id`
- `GET /downloads` (estudiantes)

## 5) Reglas de negocio obligatorias
- El registro público de usuarios debe estar deshabilitado.
- Solo `admin` puede crear cuentas.
- Toda clase con video debe validarse como URL de YouTube.
- Toda descarga debe ser un link seguro (`https://`).
- Contenidos no publicados no se muestran a estudiantes.

## 6) JSON semilla sugerido para carga inicial

```json
{
  "course": {
    "title": "Escuela Sindical Aprendamos Luchando",
    "objective": "Generar conocimiento de estrategias de lucha y organización, funcionamiento del Estado. Conceptos generales de clase, género y gestión práctica del trabajo sindical.",
    "audience": "Dirigentes sindicales y trabajadores del ámbito privado y del Estado, principalmente trabajadores a honorarios.",
    "schedule_text": "16:30 a 18:30 horas, una vez por semana"
  },
  "inauguration": [
    "Presentación de la escuela",
    "Discurso de apertura",
    "Artista",
    "Video de exposición de las luchas de nuestra organización",
    "Finalización"
  ],
  "lessons": [
    {"order": 1, "title": "La productividad y formas de medirla", "speaker": "Gonzalo Durán", "organization": "Fundación SOL"},
    {"order": 2, "title": "Normas laborales generales y procedimientos para el ejercicio de la acción sindical", "speaker": "María Estrella Zúñiga"},
    {"order": 3, "title": "Qué es el Estado y su funcionamiento y su repercusión en los trabajadores", "speaker": "Cristian Cepeda"},
    {"order": 4, "title": "Estrategias de organización y lucha", "speaker": "Sergio Alegría"},
    {"order": 5, "title": "Formación del líder sindical, coherencia y consecuencia", "speaker": "Isolina Acosta"},
    {"order": 6, "title": "Rol y funciones de la Dirección del Trabajo", "speaker": "Hernán Larraín"},
    {"order": 7, "title": "Trabajo a honorarios, tipos de contrato", "speaker": "Diego López"},
    {"order": 8, "title": "Reformas laborales y movimientos sindicales", "speaker": "Por confirmar"}
  ]
}
```
