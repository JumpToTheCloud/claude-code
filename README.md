# cdk-x/claude-code — Plugin Marketplace

Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugins) for cdk-x. This repository acts as the catalog (`marketplace.json`) and hosts our own plugins under `plugins/`.

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
/plugin marketplace add cdk-x/claude-code
```

### Install a plugin

```shell
/plugin install <plugin-name>@cdk-x-plugins
```

### Update the catalog

```shell
/plugin marketplace update
```

## Adding a new plugin

1. Create a folder at `plugins/<plugin-name>/`.
2. Add `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `description`, `version`, and `author`.
3. Add its components (`skills/`, `agents/`, `hooks/`, `.mcp.json`, etc.) at the plugin root.
4. Register the plugin in `.claude-plugin/marketplace.json`, inside the `plugins` array, with at least `name` and `source` (the folder name is enough thanks to `metadata.pluginRoot`).
5. Validate the marketplace:

   ```bash
   claude plugin validate .
   ```

6. Test the install locally:

   ```shell
   /plugin marketplace add ./.
   /plugin install <plugin-name>@cdk-x-plugins
   ```

## Reference

- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
