{%- if obj.display %}
.. {{ obj.type }}:: {{ obj.name }}

   {% if obj.docstring %}
   {{ obj.docstring|prepare_docstring|indent(3) }}
   {% endif %}
{% endif %}