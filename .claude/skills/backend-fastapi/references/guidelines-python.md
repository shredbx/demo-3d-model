# Python Standards

## Style
- Follow PEP 8
- Use Black formatter (line length: 100)
- Type hints for all function signatures
- Docstrings: Google style

## Naming
- snake_case for functions, variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants
- _private for internal use
- __double_underscore only for name mangling

## Pythonic Idioms
- List comprehensions over map/filter
- Context managers (with) for resources
- Generators for large sequences
- enumerate() instead of range(len())
- f-strings for formatting
- Pathlib over os.path

## Type Hints
```python
def process_user(user_id: int, options: dict[str, Any]) -> User | None:
    ...
```

## Error Handling
- Prefer exceptions over return codes
- Use specific exceptions (ValueError, TypeError)
- Context managers for cleanup
- EAFP over LBYL (ask forgiveness, not permission)

## Testing
- pytest framework
- test_* naming
- Fixtures for setup
- Parametrize for multiple cases