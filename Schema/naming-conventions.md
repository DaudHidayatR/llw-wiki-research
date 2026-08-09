# Naming And Stable IDs
Generated filenames use lowercase ASCII kebab-case: NFKD normalize, remove combining marks, ASCII-drop unsupported characters, lowercase, replace non-alphanumeric runs by `-`, collapse and trim hyphens. Supply an explicit ASCII slug if empty or misleading. Notes normally use `<slug>.md`; logs may prefix an ISO date.

Creation IDs are `<type>-<slug>` and never change automatically after title/alias/path changes. On collision append the first six lowercase hex characters of `SHA256(type + "\n" + initial_relative_path)`. IDs are unique lowercase `[a-z0-9-]`, normally begin with exact type plus `-`; relationships target stable IDs, while evidence targets canonical Raw paths.
