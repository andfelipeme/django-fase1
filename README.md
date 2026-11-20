# Fase 1 — Django básico: proyecto, vistas, URLs y templates

> Verificado con **Django 6.1.3**, **Python 3.15.2** y **uv 0.13.9** (noviembre 2026), siguiendo el tutorial oficial de Django 6.1. Todas las salidas y errores son reales.

---

## Clase 1 — Crear el proyecto

| Concepto | Qué es |
|---|---|
| **Django** | Framework web "baterías incluidas": base de datos, admin, usuarios, formularios y seguridad |
| **Proyecto** | La configuración del sitio completo (uno solo) |
| **App** | Módulo con una función concreta (`inventario`, `pedidos`); un proyecto tiene varias |

### Comandos

```bash
uv init --no-package --python 3.15 taller3d
cd taller3d
uv add django                              # instala Django en el .venv y lo anota en pyproject.toml
uv run django-admin --version              # 6.1.3
rm main.py                                 # en Django el punto de entrada es manage.py
uv run django-admin startproject config .  # el punto = "créalo aquí mismo"
uv run manage.py runserver                 # http://127.0.0.1:8000/  (Control + C para detener)
uv run manage.py runserver 8080            # en otro puerto
uv run manage.py check                     # revisa la configuración
```

- `uv add django` también instala `asgiref` y `sqlparse` (dependencias de Django).
- Con uv se escribe `uv run manage.py …` donde la documentación dice `python manage.py …`.
- Evitar nombres de proyecto como `django` o `test` (chocan con paquetes existentes).

### Estructura

```
taller3d/
├── manage.py           ← órdenes al proyecto (como php artisan)
├── config/
│   ├── __init__.py
│   ├── settings.py     ← configuración
│   ├── urls.py         ← tabla de rutas
│   ├── asgi.py         ← entrada para servidores de producción
│   └── wsgi.py         ← entrada para servidores de producción
├── pyproject.toml
├── uv.lock
└── .gitignore          ← agregar: db.sqlite3
```

```bash
echo "db.sqlite3" >> .gitignore     # >> agrega al final; > borraría todo el archivo
```

### `settings.py`

| Ajuste | Qué es |
|---|---|
| `SECRET_KEY` | Clave secreta; "django-insecure-" = solo desarrollo |
| `DEBUG = True` | Errores detallados; solo desarrollo |
| `ALLOWED_HOSTS` | Dominios que pueden servir el sitio |
| `DATABASES` | SQLite en `BASE_DIR / "db.sqlite3"` por defecto |
| `LANGUAGE_CODE = "es-co"` | Idioma (formato idioma-país, con guion) |
| `TIME_ZONE = "America/Bogota"` | Zona horaria (formato Continente/Ciudad) |

### Laravel → Django

| Laravel | Django |
|---|---|
| `php artisan serve` | `uv run manage.py runserver` |
| `php artisan …` | `uv run manage.py …` |
| `.env` + `config/` | `settings.py` |
| `routes/web.php` | `urls.py` |

### Errores típicos

| Error | Mensaje |
|---|---|
| `manage.py` desde otra carpeta | `error: Failed to spawn: manage.py` |
| Puerto ocupado | `Error: That port is already in use.` |
| Sin el punto en `startproject` | Carpeta `config/config/` de más |
| Zona horaria mal escrita | `ValueError: Incorrect timezone setting: America/Bogata` |
| Idioma con guion bajo | `(translation.E001) ... invalid value for the LANGUAGE_CODE setting: 'es_co'` |

---

## Clase 2 — App, vista y URL

| Concepto | Qué es |
|---|---|
| **Vista** | Función que recibe `request` y devuelve (`return`) un `HttpResponse` |
| **URLconf** | Lista `urlpatterns` que conecta rutas con vistas |
| **`path(ruta, vista, name=...)`** | Una ruta; la vista va **sin paréntesis** |
| **`include("app.urls")`** | Conecta las URLs de una app; corta el prefijo y pasa el resto |

### Recorrido de una petición

```
/inventario/ → config/urls.py ("inventario/" + include)
             → inventario/urls.py (path(""))
             → views.inicio(request) → HttpResponse → navegador
```

### Código

```bash
uv run manage.py startapp inventario    # urls.py NO viene: se crea a mano
```

```python
# inventario/views.py
from django.http import HttpResponse


def inicio(request):
    return HttpResponse("Inventario del taller")
```

```python
# inventario/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
]
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("inventario/", include("inventario.urls")),
    path("admin/", admin.site.urls),
]
```

- Las rutas terminan en `/`; `/inventario` redirige solo (301) a `/inventario/`.
- En la app, las rutas van **sin** el prefijo (si no: `/inventario/inventario/materiales/`).
- Con rutas propias, la raíz `/` da 404 (desaparece la página del cohete). Es normal.
- Siempre se usa `include()`, salvo `admin.site.urls`.

### Laravel → Django

| Laravel | Django |
|---|---|
| Método de controlador | Función de vista |
| `return response('texto')` | `return HttpResponse("texto")` |
| `Route::prefix('inventario')->group(...)` | `include()` |

### Errores típicos

| Error | Mensaje |
|---|---|
| No importar `include` | `NameError: name 'include' is not defined` |
| `include("inventario.url")` | `ModuleNotFoundError: No module named 'inventario.url'. Did you mean: 'inventario.urls'?` |
| Falta `urls.py` de la app | `ModuleNotFoundError: No module named 'inventario.urls'` |
| `views.inicio()` con paréntesis | `TypeError: inicio() missing 1 required positional argument: 'request'` |
| Vista sin `request` | `inicio() takes 0 positional arguments but 1 was given` |
| Vista devuelve texto | `'str' object has no attribute 'get'` |
| Vista sin `return` | `The view inventario.views.inicio didn't return an HttpResponse object. It returned None instead.` |

---

## Clase 3 — Templates

| Concepto | Qué es |
|---|---|
| **Template** | HTML con "huecos" que Django llena con datos |
| **Contexto** | Diccionario que la vista pasa al template; sus claves son las variables |
| **`render(request, "app/plantilla.html", contexto)`** | Carga el template, lo llena y devuelve el `HttpResponse` |
| **`{{ variable }}`** | Muestra un valor; el punto lee claves de diccionario y atributos |
| **`{% etiqueta %}`** | Lógica: `for`, `if`… |

### Requisitos

1. La app en `INSTALLED_APPS`: `"inventario.apps.InventarioConfig"` (la clase está en `apps.py`).
2. La carpeta `inventario/templates/inventario/` (el nombre de la app repetido evita choques entre apps con plantillas del mismo nombre).

```bash
mkdir -p inventario/templates/inventario
```

### Código

```python
from django.http import HttpResponse
from django.shortcuts import render


def materiales(request):
    lista = [
        {"nombre": "PLA", "color": "Negro", "cantidad": 1000},
        {"nombre": "PETG", "color": "Blanco", "cantidad": 650},
    ]
    contexto = {"titulo": "Materiales del taller", "materiales": lista}
    return render(request, "inventario/materiales.html", contexto)
```

```html
<ul>
    {% for material in materiales %}
        <li>{{ material.nombre }} {{ material.color }} - {{ material.cantidad }} g</li>
    {% empty %}
        <li>No hay materiales registrados.</li>
    {% endfor %}
</ul>
```

- Django **escapa el HTML** de los datos automáticamente (`<b>` sale como texto).
- Si se crea una carpeta `templates` **con el servidor encendido**, Django no la ve hasta reiniciarlo. Los archivos nuevos dentro de una carpeta existente sí los detecta solo.

### Laravel → Django

| Blade | Django |
|---|---|
| `resources/views/inventario/materiales.blade.php` | `inventario/templates/inventario/materiales.html` |
| `return view('inventario.materiales', [...])` | `render(request, "inventario/materiales.html", contexto)` |
| `{{ $titulo }}` | `{{ titulo }}` |
| `$material['nombre']` / `$material->nombre` | `material.nombre` |
| `@forelse ... @empty ... @endforelse` | `{% for %} ... {% empty %} ... {% endfor %}` |

### Errores típicos

| Error | Qué pasa |
|---|---|
| App no registrada | `TemplateDoesNotExist: inventario/materiales.html` |
| Carpeta `templates` creada con el servidor encendido | Mismo error hasta reiniciar |
| Template sin la subcarpeta de la app | `TemplateDoesNotExist` |
| Nombre mal escrito en `render` | `TemplateDoesNotExist: inventario/material.html` |
| Olvidar `request` en `render` | `TemplateDoesNotExist` con el diccionario en el mensaje |
| Falta `{% endfor %}` | `TemplateSyntaxError: Unclosed tag on line 10: 'for'. Looking for one of: endfor.` |
| Variable mal escrita | **Sin error**: sale vacío |

---

## Clase 4 — Plantilla base y enlaces

### Parte A: plantilla base (herencia)

- `{% block nombre %}{% endblock %}` en la base: un hueco que la hija puede llenar (lo que tenga dentro es el valor por defecto).
- `{% extends "base.html" %}` en la hija: **primera etiqueta** del archivo. La hija solo llena bloques.
- `base.html` va en `templates/` del proyecto (al lado de `manage.py`), con:

```python
"DIRS": [BASE_DIR / "templates"],
```

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block titulo %}Taller VHAJ{% endblock %}</title>
</head>
<body>
    <nav>
        <a href="{% url 'inventario:inicio' %}">Inventario</a> |
        <a href="{% url 'inventario:materiales' %}">Materiales</a> |
        <a href="{% url 'pedidos:inicio' %}">Pedidos</a>
    </nav>
    <main>
        {% block contenido %}{% endblock %}
    </main>
</body>
</html>
```

```html
<!-- inventario/templates/inventario/materiales.html -->
{% extends "base.html" %}

{% block titulo %}{{ titulo }}{% endblock %}

{% block contenido %}
    <h1>{{ titulo }}</h1>
    ...
{% endblock %}
```

### Parte B: enlaces con nombres de URL

- `{% url 'app:nombre' %}` arma la dirección desde el `name` de la ruta. Si cambia la ruta, los enlaces se actualizan solos.
- Con dos rutas del mismo `name` y sin espacios de nombres, Django usa **la última registrada** sin avisar.
- `app_name = "inventario"` en el `urls.py` de la app crea el espacio de nombres:

```python
app_name = "inventario"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("materiales/", views.materiales, name="materiales"),
]
```

### Laravel → Django

| Blade | Django |
|---|---|
| `@yield('contenido')` | `{% block contenido %}{% endblock %}` |
| `@extends('layouts.app')` | `{% extends "base.html" %}` |
| `@section('contenido') ... @endsection` | `{% block contenido %} ... {% endblock %}` |
| `Route::name('inventario.')->group(...)` | `app_name = "inventario"` |
| `route('inventario.materiales')` | `{% url 'inventario:materiales' %}` |

### Errores típicos

| Error | Qué pasa |
|---|---|
| Sin `DIRS` o sin reiniciar tras crear `templates/` | `TemplateDoesNotExist: base.html` |
| Etiqueta o variable antes de `{% extends %}` | `TemplateSyntaxError: {% extends "base.html" %} must be the first tag in '...'` |
| Contenido de la hija fuera de un bloque | **Sin error**: no aparece |
| Bloque con otro nombre en la hija | **Sin error**: no aparece |
| `'inventario:inicio'` sin `app_name` | `NoReverseMatch: 'inventario' is not a registered namespace` |
| `'inicio'` a secas con `app_name` puesto | `NoReverseMatch: Reverse for 'inicio' not found. ...` |
| Nombre mal escrito | `NoReverseMatch: Reverse for 'inico' not found. ...` |
| Sin comillas: `{% url inventario:inicio %}` | `TemplateSyntaxError: Could not parse the remainder: ':inicio' from 'inventario:inicio'` |

---

## Prácticas realizadas

| Práctica | Qué se construyó |
|---|---|
| 1 | Proyecto `taller3d` en español de Colombia y hora de Bogotá; `db.sqlite3` en `.gitignore` |
| 2 | Vista `materiales` y segunda app `pedidos` |
| 3 | Templates con contexto, `for` y `empty` en las dos apps |
| 4 | `base.html` con menú, herencia en las 3 páginas y espacios de nombres |

## Lecciones de las revisiones

- **La etiqueta debe decir lo mismo que el dato**: si la clave es `cantidad` en unidades, no se muestra como "Peso".
- **Nombres consistentes**: la vista principal de cada app se llama `inicio` (`inventario:inicio`, `pedidos:inicio`).
- **Imports**: primero librerías en orden alfabético, línea en blanco, luego los del proyecto (`from . import views`); sin comentarios ni código comentado en medio.
- **Importa solo lo que usas** (`F401`); revisar con `uvx ruff check .`. Los `F401` de `admin.py`, `models.py` y `tests.py` los genera Django y se usan en la Fase 2.
- **Unidades con espacio**: `1000 g`, no `1000g`.
- **Reiniciar el servidor** al crear carpetas `templates` nuevas.
- **Leer la última línea del error**: Django y Python 3.15 suelen decir qué está mal y sugerir el nombre correcto.