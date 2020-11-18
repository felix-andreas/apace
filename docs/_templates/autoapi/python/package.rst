{% if not obj.display %}
:orphan:

{% endif %}

.. _api-reference:

API Reference
=============

This is the API reference. To learn how to use and work with apace, see :ref:`user-guide`.

{% if obj.all is not none %}
{% set visible_children = obj.children|selectattr("short_name", "in", obj.all)|list %}
{% elif obj.type is equalto("package") %}
{% set visible_children = obj.children|selectattr("display")|list %}
{% else %}
{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}
{% set visible_classes = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}
{% set visible_exceptions = visible_children|selectattr("type", "equalto", "exception")|list %}
{% set constants = obj.children|selectattr("type", "equalto", "data")|list %}
{% set constants_dict = {} %}
{% for constant in constants %}
{%- set _ = constants_dict.update({constant.name: constant}) -%}
{% endfor %}

* :const:`__version__` **=** :code:`{{ constants_dict["__version__"].value }}`
* :const:`__license__` **=** :code:`{{ constants_dict["__license__"].value }}`

Classes
-------
{% for klass in obj.classes %}
* :class:`{{ klass.name }}` - {{ klass.summary }}
{% endfor %}

Functions
---------
{% for function in obj.functions %}
* :func:`{{ function.name }}` - {{ function.summary }}
{% endfor %}

Exceptions
----------
{% for exception in visible_exceptions %}
* :exc:`{{ exception.name }}` - {{ exception.summary }}
{% endfor %}

Detailed Overview
-----------------
{% for obj in visible_classes %}
{{ obj.rendered|indent(0) }}
{% endfor %}

{% for obj in visible_functions %}
{{ obj.rendered|indent(0) }}
{% endfor %}

{% for obj in visible_exceptions %}
{{ obj.rendered|indent(0) }}
{% endfor %}

Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1
   
   plot/index