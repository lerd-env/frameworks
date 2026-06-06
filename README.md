# lerd-frameworks

Community framework definitions for [lerd](https://github.com/geodro/lerd).

## Usage

```bash
lerd framework search symfony        # search the store
lerd framework install symfony       # auto-detects version from composer.lock
lerd framework install laravel@12    # install a specific version
lerd framework update                # update all installed definitions
```

When you link a project and no local definition exists, lerd offers to install one from this store automatically.

## Available frameworks

| Framework | Versions | Detection |
|-----------|----------|-----------|
| Laravel | 13, 12 | `artisan` file, `laravel/framework` in composer.json |
| Symfony | 8, 7 | `symfony.lock` file, `symfony/framework-bundle` in composer.json |
| WordPress | 6, 5 | `wp-login.php` or `wp-config.php` file |
| Drupal | 11, 10 | `drupal/core-recommended` or `drupal/core` in composer.json |
| CakePHP | 5, 4 | `bin/cake` file, `cakephp/cakephp` in composer.json |
| CodeIgniter | 4 | `spark` file, `codeigniter4/framework` in composer.json |
| Statamic | 6, 5 | `statamic/cms` in composer.json |

## Contributing

1. Fork this repo
2. Add or update a YAML file under `frameworks/<name>/<version>.yaml`
3. Update `frameworks/index.json` with the new entry
4. Submit a pull request

### YAML schema

See the [lerd frameworks documentation](https://github.com/geodro/lerd/blob/main/docs/usage/frameworks.md#yaml-schema) for the full schema reference.

Each definition must include a `version` field matching the major version it targets:

```yaml
name: myframework
version: "7"
label: My Framework
public_dir: public
detect:
  - composer: myvendor/myframework
# ... rest of definition
```

## License

MIT
