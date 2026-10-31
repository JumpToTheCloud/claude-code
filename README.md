# JumpToTheCloud/claude-code — Plugin Marketplace

![Claude Code Plugin Marketplace](https://img.shields.io/badge/Claude%20Code-Plugin%20Marketplace-6E56CF)
[![release-please](https://github.com/JumpToTheCloud/claude-code/actions/workflows/release-please.yml/badge.svg)](https://github.com/JumpToTheCloud/claude-code/actions/workflows/release-please.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugins) for jumptothecloud. This repository acts as the catalog (`marketplace.json`) and hosts our own plugins under `plugins/`.

## Structure

```
.
├── .claude-plugin/
│   └── marketplace.json        # Marketplace catalog
└── plugins/                    # Our own plugins (one folder each)
```

## Usage

### Add this marketplace

```shell
/plugin marketplace add JumpToTheCloud/claude-code
```

### Install a plugin

```shell
/plugin install <plugin-name>@jumptothecloud-code-marketplace
```

### Update the catalog

```shell
/plugin marketplace update
```

## Adding a new plugin

1. Create a folder at `plugins/<plugin-name>/`.
2. Add `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `description`, `version`, and `author`.
3. Add its components (`skills/`, `agents/`, `hooks/`, `.mcp.json`, etc.) at the plugin root.
4. Register the plugin in `.claude-plugin/marketplace.json`, inside the `plugins` array, with at least `name` and `source` (the relative path, e.g. `./plugins/<plugin-name>`).
5. Validate the marketplace:

   ```bash
   claude plugin validate .
   ```

6. Test the install locally:

   ```shell
   /plugin marketplace add ./.
   /plugin install <plugin-name>@jumptothecloud-code-marketplace
   ```

## Reference

- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
