# Modulo plugin registry

The index [Modulo CMS](https://github.com/PhantomPixelDev/modulo-cms) installs plugins
from. The core reads:

```
https://raw.githubusercontent.com/PhantomPixelDev/modulo-registry/main/registry.json
```

Override with `MODULO_PLUGIN_REGISTRY` to run your own.

## Trust

Each entry records the SHA-256 of a release asset. The core downloads the asset from
an allowlisted host and refuses to unpack it unless the checksum matches. Installs
are **checksum-verified against this registry**, not signed: whoever controls this
repository controls what gets installed.

`registry.json` is generated, never hand-edited. The build downloads every package,
recomputes its checksum and fails if it disagrees with the one the plugin published.

## Adding a plugin

1. Publish releases with `<slug>-<version>.zip` (plugin.json at the zip root) and
   `<slug>-<version>.zip.sha256` — copy the release workflow from
   [modulo-plugin-hello-world](https://github.com/PhantomPixelDev/modulo-plugin-hello-world).
2. Open a pull request adding the repository to `sources.json`.

The index rebuilds hourly and on every change to `sources.json`.
