# Project2-commerce

## Some tips and steps to make django realod the web page automatically every time you change anything in css or scss files

install these first:
```
pip install django-browser-reload
pip install django-sass-processor
pip install django-libsass
pip install django-livereload-server
```

Add these to your installed apps in django `settings.py`:
```
INSTALLED_APPS = [
    # other installed apps ...
    'sass_processor',
    'livereload',
    'django_browser_reload',
]

```

Add this to you middleware list in `settings.py`:
```
MIDDLEWARE = [
    # other middleware ...
    'livereload.middleware.LiveReloadScript',
]
```

Add this to `STATICFILES_FINDERS`:
```
STATICFILES_FINDERS = [
    # other static files ...
    'sass_processor.finders.CssFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

Add these lines to `settings.py` :
```
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

#Configuration to make my project start and refrash every time I make a change
LIVERELOAD_PORT = 35729

BROWSER_RELOAD_SCSS_DIRS = [
    SASS_PROCESSOR_ROOT,
]
```

finally add this to your `.html` file :
```
{% load sass_tags %}
    <link rel="stylesheet" type="text/css" href="{% sass_src 'app_folder_name/scss_file_name.scss' %}">
```