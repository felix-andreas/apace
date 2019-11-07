{% if obj.display %}
.. py:{{ obj.type }}:: {{ obj.short_name }}{% if obj.args %}({{ obj.args }}){% endif %}


   {% if obj.bases %}
   Inherits: {% for base in obj.bases %}:class:`{{ base }}`{% if not loop.last %}, {% endif %}{% endfor %}

   {% endif %}

   {% if obj.docstring %}
   {{ obj.docstring|prepare_docstring|indent(3) }}
   {% endif %}
   {% set visible_classes = obj.classes|selectattr("display")|list %}
   {% for klass in visible_classes %}
   {{ klass.rendered|indent(3) }}
   {% endfor %}

   {% set visible_attributes = obj.attributes|selectattr("display")|rejectattr("annotation", "equalto", "Signal")|list %}
   {% set visible_signals = obj.attributes|selectattr("display")|selectattr("annotation", "equalto", "Signal")|list %}
   {% set visible_methods = [] %}
   {% for method in obj.methods|selectattr("display")|list %}
   {% if "property" in method.properties %}
   {% set _ = visible_attributes.append(method) %}
   {% else %}
   {% set _ = visible_methods.append(method) %}
   {% endif %}
   {% endfor %}

   {% if visible_attributes %}
   **Attributes**
   {% endif %}

   {% for attribute in visible_attributes %}
   {{ attribute.rendered|indent(3) }}
   {% endfor %}

   {% if visible_methods %}
   **Methods**
   {% endif %}

   {% for method in visible_methods %}
   {{ method.rendered|indent(3) }}
   {% endfor %}

   {% if visible_signals %}
   **Signals**
   {% endif %}

   {% for signal in visible_signals %}
   {{ signal.rendered|indent(3) }}
   {% endfor %}

{% endif %}
