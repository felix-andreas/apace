{%- if obj.display %}
{% if sphinx_version >= (2, 1) %}
{% if "property" in obj.properties %}
.. attribute:: {{ obj.short_name }}
   {%+ if obj.return_annotation %}:annotation: :{{ obj.return_annotation }}{% endif %}
{% else %}
.. method:: {{ obj.short_name }}({{ obj.args.split(',', 1)[1:]|join(',') }}) {% if obj.return_annotation %} -> {{ obj.return_annotation }}{% endif %}
{% for property in obj.properties %}
:{{ property }}:
{% endfor %}
{% endif %}

{% else %}
.. {{ obj.method_type }}:: {{ obj.short_name }}({{ obj.args.split(',', 1)[1:]|join(',') }})
{% endif %}

   {% if obj.docstring %}
   {{ obj.docstring|prepare_docstring|indent(3) }}
   {% endif %}
{% endif %}