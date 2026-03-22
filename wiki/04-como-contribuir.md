# Cómo contribuir

## Estructura de una contribución

1. **Nueva tool** → crea `agent/tools/mi_tool.py`, regístrala en `__init__.py` y `tools_manifest.yml`, documenta en `wiki/02-tools.md`
2. **Config de seguridad** → edita los YAMLs en `config/`, nunca hardcodees paths o dominios en el código
3. **Cambio al grafo** → modifica `agent/graph.py`, asegúrate de que `auditor` siga corriendo después de cada tool

## Reglas básicas

- Toda tool debe llamar a `log_action` antes de retornar
- No lanzar excepciones al LLM — captura y retorna string con `"ERROR: ..."`
- Los tests van en `tests/` (directorio a crear cuando haya cobertura inicial)
- Ningún secret en el código — usar variables de entorno o config YAML

## Correr localmente

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m agent.main
```
