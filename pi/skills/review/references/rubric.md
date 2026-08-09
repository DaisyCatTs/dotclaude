# Review Rubric (Embedded in Prompt)

The review prompt given to pi must cover these dimensions. Embed them as part of the task description, not as `--append-system-prompt`:

### 1. Correctness & Logic
- Does the code do what it intends? Any off-by-one, race conditions, null pointer, or type errors?
- Are error paths handled (not just the happy path)?
- Are async operations properly awaited or chained?

### 2. Code Quality & Maintainability
- Naming: do names reveal intent? (Mysterious Name)
- Duplication: is the same logic repeated? (Duplicated Code)
- Coupling: does a module reach into another's internals? (Feature Envy)
- Abstraction: is there speculative generality or missing domain types? (Speculative Generality, Primitive Obsession)
- Size: are functions/classes too large? Do they do one thing?

### 3. Security
- Are user inputs validated/sanitized?
- Any hardcoded secrets, tokens, or credentials?
- Any injection vectors (SQL, command, path traversal)?

### 4. Architecture & Design
- Does the change follow the project's established patterns?
- Does it introduce unnecessary dependencies?
- Is the change scoped appropriately (not shotgun surgery)?

### 5. Testing
- Are there tests for the changed code?
- Do tests cover edge cases and error paths?
