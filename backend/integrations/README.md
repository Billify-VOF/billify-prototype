# integrations/README.md

# Integrations Layer

The integrations layer manages connections and communications with external services.

## Structure

### Providers
External service implementations:
- `ponto.py` - Banking service integration
- `yuki.py` - Accounting service integration

### Sync
Data synchronization management:
- `manager.py` - Sync orchestration
- `tasks.py` - Background tasks

### Transformers
Data transformation logic:
- `ponto_transformer.py` - Bank data transformation
- `yuki_transformer.py` - Accounting data transformation

## Guidelines

- Keep external system specifics isolated
- Handle data format conversions
- Manage authentication with external services
- Implement retry and error handling