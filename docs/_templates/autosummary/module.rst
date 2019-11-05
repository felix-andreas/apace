API Reference
=============

.. rubric:: Description

.. automodule:: {{ fullname }}

.. currentmodule:: {{ fullname }}

{% if classes %}
Classes
-------

.. autosummary::
    :toctree: .
    {% for class in classes %}
    {{ class }}
    {% endfor %}

{% endif %}

{% if functions %}
Functions
---------

.. autosummary::
    :toctree: .
    {% for function in functions %}
    {{ function }}
    {% endfor %}

Exceptions
----------

.. autosummary::
   :toctree .
   {% for exception in exceptions %}
   {{ exception }}
   {% endfor %}

{% endif %}