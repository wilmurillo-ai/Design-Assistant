# API Reference - {{ module_name }}

## Functions

{% for func in functions %}
### `{{ func.name }}({{ func.parameters|join(', ') }})`{% if func.return_type %} → `{{ func.return_type }}`{% endif %}

{{ func.docstring or '_No description_' }}

{% if func.parameters %}
**Parameters:**
{% for param in func.parameters %}
- `{{ param.name }}`{% if param.type %} (`{{ param.type }}`){% endif %}{% if param.default %} = `{{ param.default }}`{% endif %} - {{ param.description or '_' }}
{% endfor %}
{% endif %}

{% if func.raises %}
**Raises:**
{% for exc in func.raises %}
- `{{ exc.type }}`: {{ exc.description }}
{% endfor %}
{% endif %}

---
{% endfor %}

## Classes

{% for cls in classes %}
### `class {{ cls.name }}`{% if cls.base_classes %}({{ cls.base_classes|join(', ') }}){% endif %}

{{ cls.docstring or '_No description_' }}

{% if cls.attributes %}
**Attributes:**
{% for attr in cls.attributes %}
- `{{ attr.name }}`: {{ attr.value }}
{% endfor %}
{% endif %}

{% if cls.methods %}
**Methods:**
{% for method in cls.methods %}
- `{{ method.name }}({{ method.parameters|map(attribute='name')|join(', ') }})` → `{{ method.return_type or 'None' }}`
{% endfor %}
{% endif %}

---
{% endfor %}
