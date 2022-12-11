# Note to Code Shelter maintainers

This project is considered stable and requires little to no
maintenance. I'm still around maintaining it but I won't be
working on it unless someone submits a PR or files an issue
as I'm not actively using it myself.

I was asked to [reduce the bus factor](https://github.com/bikeshedder/django-composite-field/issues/1#issuecomment-1344934071).
This sounds like a sensible request. So here we are. 👍

As of today (2022-12-11) there are no known bugs and it should be compatible
with all Django versions. It used to break every time Django added a new
field to the `django.db.models.fields.Field` class but that last happened
in 2019.

I don't use Django and this project as much as I used to. It would be
great if someone has a sharp eye on it and checks if upcoming
Django versions require another release of this library.

I have already added Code Shelter to the project's PyPI page, so feel free to
make any releases necessary.

Thank you!
