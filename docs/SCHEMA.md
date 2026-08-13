# CelLAB Documentation Schema

## Purpose
This schema defines the hierarchical documentation format used by CellIntella and developers.
The LLM reads Level 0 first, matches keywords, then drills into Level 1/2 as needed.

## Levels

### Level 0: INDEX.md (root)
- One file for the entire platform
- Each package: name, keywords, one-line description, path to OVERVIEW.md
- ~500 tokens — always loaded first

### Level 1: OVERVIEW.md (per package)
- What it does, key concepts, when to use it
- API summary: method signatures (no details)
- Links to Level 2 detail files
- ~800-1200 tokens

### Level 2: Detail files (per topic)
- API.md — full parameter docs, return values, types
- Topic files — batch_processing.md, plotters.md, troubleshooting.md
- Each has Keywords block at top
- ~500-1500 tokens each

### Level 3: TUTORIAL.md (optional)
- Step-by-step walkthroughs with full code examples
- Only loaded when user explicitly asks for help

## File Format Rules

1. Every file starts with:
```markdown
# Title
Keywords: comma, separated, keywords
```

2. Parameters use structured blocks:
```markdown
### parameter_name
- Type: float
- Default: 0.58
- Unit: μm/pixel
- Description: What it does
- Affects: What outputs change
```

3. Methods use:
```markdown
### method_name()
Signature: `method_name(param1, param2=default)`
Returns: dict with keys [key1, key2, ...]
Example:
```python
result = obj.method_name(param1)
```
```

4. Cross-references use relative paths:
```markdown
See: cornealia/API.md#collective_order
```

5. Headers ARE the search index:
- H1 = package/file title
- H2 = category
- H3 = specific item (method, parameter, concept)
