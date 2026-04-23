# {{ project_name }}

{{ description or 'A Python project.' }}

## Installation

```bash
pip install {{ project_name }}
```

## Usage

```python
{{ usage_example or 'TODO: Add usage example' }}
```

## API Reference

See [API Reference](docs/API.md) for detailed documentation.

{% if has_tests %}
## Running Tests

```bash
pytest tests/
```
{% endif %}

## License

MIT License - Copyright (c) 2026 思捷娅科技 (SJYKJ)
