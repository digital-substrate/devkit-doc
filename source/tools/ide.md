# IDE Integration

Two IDE extensions support DSM development with syntax highlighting, validation, and code
completion.

| IDE           | Extension    | Strengths                                     |
|---------------|--------------|-----------------------------------------------|
| **VS Code**   | `ds-dsm`     | Lightweight, snippets, problem matcher        |
| **JetBrains** | DSM Language | Full IDE: completion, navigation, refactoring |

---

## VS Code Extension

```{figure} /_static/images/tools/vscode.png
:alt: VS Code editor showing DSM file with syntax highlighting for keywords, types, and UUIDs
:width: 100%

VS Code with DSM syntax highlighting and problem matcher.
```

### Installation

The VS Code extension is published on the [VS Code
Marketplace](https://marketplace.visualstudio.com/items?itemName=DigitalSubstrate.ds-dsm).

1. Open Visual Studio Code
2. Open the Extensions view: `Cmd+Shift+X` (macOS) or `Ctrl+Shift+X` (Windows/Linux)
3. Search for **DSM Syntax Highlighter** (publisher: *DigitalSubstrate*)
4. Click **Install**

Alternatively, install from the command line:

```bash
code --install-extension DigitalSubstrate.ds-dsm
```

Source repository:
[github.com/digital-substrate/dsm-vscode](https://github.com/digital-substrate/dsm-vscode).

### Syntax Highlighting

The extension highlights:

- Keywords (`namespace`, `concept`, `struct`, `attachment`)
- Types (`string`, `int64`, `vector<T>`)
- UUIDs, comments, docstrings

### Snippets

Type a prefix and press Tab to expand:

**Structures:**

| Prefix                     | Expansion                           |
|----------------------------|-------------------------------------|
| `namespace`                | Namespace with UUID placeholder     |
| `concept`                  | `concept Name;`                     |
| `struct`                   | Structure template                  |
| `enum`                     | Enumeration template                |
| `attachment`               | `attachment<Concept, Struct> name;` |
| `function_pool`            | Function pool with UUID             |
| `attachment_function_pool` | Attachment function pool            |

**Types:**

| Prefix     | Expansion      |
|------------|----------------|
| `key`      | `key<T>`       |
| `optional` | `optional<T>`  |
| `vec`      | `vec<T, size>` |
| `map`      | `map<K, V>`    |
| `set`      | `set<T>`       |

**Advanced:**

| Prefix    | Expansion                          |
|-----------|------------------------------------|
| `isa`     | `concept Derived is a Base;`       |
| `opt-key` | `optional<key<Concept>> fieldKey;` |
| `mutable` | Mutable function with docstring    |

## Build Task Configuration

Create `.vscode/tasks.json` to enable syntax checking on build:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check DSM Syntax",
      "type": "shell",
      "command": "python",
      "args": [
        "../tools/dsm_util.py",
        "check",
        "${file}"
      ],
      "presentation": {
        "reveal": "never",
        "revealProblems": "onProblem"
      },
      "problemMatcher": "$dsm",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

### Using the Build Task

- Press `Cmd+Shift+B` (macOS) or `Ctrl+Shift+B` (Windows/Linux)
- Errors appear in the Problems panel with click-to-navigate

## Optional: Theme Customization

### Dracula Theme (Recommended)

1. Open Command Palette
2. Run: `Browse Color Theme in MarketPlace`
3. Select: `Dracula`

### Token Customization

Add to your `settings.json`:

```json
{
  "editor.tokenColorCustomizations": {
    "textMateRules": [
      {
        "scope": "variable.key.dsm",
        "settings": {
          "fontStyle": "underline"
        }
      },
      {
        "scope": "constant.uuid.dsm",
        "settings": {
          "fontStyle": "underline"
        }
      },
      {
        "scope": "constant.enum.dsm",
        "settings": {
          "fontStyle": "italic"
        }
      }
    ]
  }
}
```

This customization:

- Underlines key types
- Underlines UUIDs
- Italicizes enum cases

---

## JetBrains Plugin

For IntelliJ IDEA, CLion, PyCharm, and other JetBrains IDEs.

```{figure} /_static/images/tools/jetbrains_overview.png
:alt: JetBrains IDE showing DSM file with syntax highlighting, code completion popup, Structure view panel, and DSM Validation panel
:width: 100%

JetBrains plugin showing syntax highlighting, code completion, Structure view, and DSM Validation panel.
```

### Installation

The JetBrains plugin is published on the [JetBrains
Marketplace](https://plugins.jetbrains.com/plugin/31186-dsm-language-support).

1. Open your JetBrains IDE (IntelliJ IDEA, PyCharm, CLion, etc.)
2. Go to: `Settings/Preferences > Plugins > Marketplace`
3. Search for **DSM** (publisher: *Digital Substrate*)
4. Click **Install**
5. Restart the IDE when prompted

Source repository:
[github.com/digital-substrate/dsm-jetbrains](https://github.com/digital-substrate/dsm-jetbrains).

### Key Features for DSM Development

**Context-Aware Completion:**

The plugin suggests different types based on cursor position:

- Inside `attachment<▸>` → suggests concepts and clubs only
- Inside `attachment<Graph, ▸>` → suggests all types (structs, primitives)
- Inside `key<▸>` → suggests concepts only (not structs)

**Navigation:**

| Action           | macOS       | Windows/Linux |
|------------------|-------------|---------------|
| Go to Definition | `Cmd+Click` | `Ctrl+Click`  |
| Find Usages      | `Alt+F7`    | `Alt+F7`      |
| Go to Symbol     | `Cmd+Alt+O` | `Ctrl+Alt+N`  |

**Validation:**

| Action         | Shortcut       |
|----------------|----------------|
| Validate DSM   | `Ctrl+Alt+V`   |
| Next Error     | `Alt+F2`       |
| Previous Error | `Alt+Shift+F2` |

**Refactoring:**

- **Rename** (`Shift+F6`): Renames across all files
- **Reformat** (`Cmd+Alt+L` / `Ctrl+Alt+L`): Consistent formatting

---

## Development Workflow

The typical DSM development cycle:

```text
Write DSM  →  Validate  →  Fix Errors  →  Generate Code
   │            │             │              │
   ▼            ▼             ▼              ▼
 IDE        Cmd+Shift+B    Click error    generate.py
 Snippets   or Ctrl+Alt+V  to navigate    or dsm_util.py
```

### Project Structure

```
my_project/
├── definitions/
│   ├── Model.dsm
│   └── Pools.dsm
├── src/generated/      # Kibo output (C++)
├── python/mymodel/     # Kibo output (Python)
└── generate.py         # Code generation script
```

## What's Next

- [Wheels](wheels.md) - Creating Python wheels
- [Templates](templates.md) - Understanding templated features
