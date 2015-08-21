SECRET_KEY = 'dummy_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

MIDDLEWARE_CLASSES = []

INSTALLED_APPS = [
    'composite_field',
    'composite_field_test',
]
