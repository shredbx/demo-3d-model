# FastAPI Standards

## Route Handlers

- Use dependency injection
- Pydantic models for validation
- Explicit response models
- HTTP status codes as constants
- OpenAPI tags for grouping

## Dependencies

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    ...
```

## Error Handling

- HTTPException for API errors
- Custom exception handlers
- Structured error responses
