{%- extends 'index.rst.j2' -%}

{% block in_prompt %}
{% if cell.execution_count is defined %}
**In [{{ cell.execution_count|replace(None, " ") }}]:**
{% else %}
**In [ ]:**
{% endif %}
{% endblock in_prompt %}

{% block output_prompt %}
{% if cell.execution_count is defined %}
**Out [{{ cell.execution_count|replace(None, " ") }}]:**
{%- else -%}
{% endif %}
{% endblock output_prompt %}

{% block stream %}
{% set text_len = output.text.strip() | length %}
{% if text_len > 1 %}
.. parsed-literal::

{{ output.text | replace('*', '\*') | replace('|', '\|') | indent }}
{% endif %}
{% endblock stream %}

{% block data_html scoped %}
.. raw:: html

    <div class="data_html">
    {{ output.data['text/html'] | indent }}
    </div>
{% endblock data_html %}

{%- block jsapp -%}
.. raw:: html

{{ output.data['application/javascript'] | indent }}
{%- endblock jsapp -%}

{%- block data_javascript scoped %}
.. raw:: html

    {% set div_id = uuid4() %}

    <div id="{{ div_id }}"></div>
    <div class="output_subarea output_javascript {{ extra_class }}">
    <script type="text/javascript">
    var element = $('#{{ div_id }}');
    {{ output.data['application/javascript'] | indent}}
    </script>
    </div>
{%- endblock -%}
