# CLI

CLI written in rust to provide user experience in runners.

## Abilities

### Auto detect examples

When run, it will auto detect all examples in image and provide to user `multiselect`  choice to run examples.
To make this work each example shall deploy configuration file `name.score.json` which below layout.

```json
{
    "name": "Name of example",
    "description": "Extensive description",
    "path": "exec_path",
    "args": [
        // args to be used when running
    ],
    "env": {
        // env to be used when running
    }
}

```

You can customize where to look for examples using env `SCORE_CLI_INIT_DIR`.