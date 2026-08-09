# Relationship Model
Explicit relationships are flat strings `<lowercase-kebab-relation>|<stable-target-id>`. Semantic edges come only from these declarations. Graph generation may derive `links-to` from wikilinks and `supported-by` from source paths; it must never infer hidden semantic relations. Targets resolve repository-wide.
