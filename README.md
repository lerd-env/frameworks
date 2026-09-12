# Lerd Framework Store

> The community-driven store of framework definitions that powers
> [Lerd](https://lerd.sh) — teach Lerd a new PHP framework by
> editing YAML, no binary release required.

[![Part of Lerd](https://img.shields.io/badge/part%20of-lerd-ff2d20)](https://lerd.sh)
[![Docs](https://img.shields.io/badge/docs-lerd.sh-blue)](https://lerd.sh/usage/frameworks)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

When you run `lerd link` on a project, Lerd detects which framework it is and pulls the matching definition from this store — then it knows how to serve it, which workers to run, how to set up its `.env`, how to scaffold it, and how to health-check it. Everything is a versioned YAML file. Add a framework here and every Lerd install can use it within 24 hours, with no new Lerd release and no Go code.

That's the whole point: **Lerd is framework-agnostic, and this repo is where that agnosticism lives.** Laravel, Symfony, WordPress, Drupal, CakePHP, CodeIgniter, Statamic, Winter CMS, Magento, and Tempest are all defined here — not hardcoded in the binary — and so is whatever framework you add next.

## What a definition powers

A single `frameworks/<name>/<version>.yaml` teaches Lerd to:

- 🔎 **Auto-detect** the framework and its major version on `lerd link`, from lockfiles, marker files, or `composer.json` entries
- 🐘 **Pin PHP** to the versions the framework supports, so the right runtime is selected automatically
- 🌱 **Set up `.env`** — wire database, cache, and service hosts, generate app keys, and apply framework-specific defaults
- ⚒️ **Run the right workers** — queue, schedule, Horizon, Reverb, a host-side Vite dev server, and more, each self-healing and idle-suspendable
- 🚀 **Scaffold new projects** with the framework's own `create-project` command
- 🩺 **Health-check** the site through Lerd's framework-agnostic doctor, with checks declared right in the definition
- 🧪 **Drive the Tinker REPL**, custom commands, log tails, and post-link setup steps (migrations, `storage:link`, and friends)

All of it is data. None of it ships in the binary.

## Available frameworks

| Framework | Versions | Detection |
|-----------|----------|-----------|
| Laravel | 13, 12, 11, 10, 9, 8, 7, 6 | `artisan` file or `laravel/framework` in composer.json |
| Lumen | 11, 10, 9, 8, 7, 6 | `laravel/lumen-framework` in composer.json |
| Symfony | 8, 7, 6, 5, 4 | `symfony.lock` file or `symfony/framework-bundle` in composer.json |
| WordPress | 7, 6, 5 | `wp-login.php` file or `wp-config.php` file |
| Bedrock | 1 | `web/wp-config.php` file or `web/wp/wp-login.php` file |
| Drupal | 11, 10, 9, 8 | `drupal/core-recommended` or `drupal/core` in composer.json |
| TYPO3 | 14, 13, 12, 11, 10 | `typo3/cms-core` in composer.json or `public/typo3` directory |
| CakePHP | 5, 4, 3 | `bin/cake` file or `cakephp/cakephp` in composer.json |
| CodeIgniter | 4, 3 | `spark` file or `codeigniter4/framework` in composer.json |
| Statamic | 6, 5, 4, 3 | `statamic/cms` in composer.json |
| Winter CMS | 1 | `winter/wn-system-module` in composer.json |
| Magento | 2 | `bin/magento` file or `magento/product-community-edition` in composer.json |
| Tempest | 3 | `tempest` file or `tempest/framework` in composer.json |

Don't see yours? [Add it](#contributing) — that's what this repo is for.

## Available packages

Some of what a project needs is not the framework's at all: a Horizon worker
belongs to `laravel/horizon`, not to Laravel 12. Those declarations live in
`packages/`, one file per composer package, and Lerd merges them into whatever
definition your project resolved when its `composer.json` requires the package.

| Package | What it adds | Applies to |
|---------|--------------|------------|
| `cakephp/migrations` | `migrate` command | CakePHP 3+ |
| `cakephp/queue` | `queue` worker | CakePHP 5+ |
| `codeigniter4/queue` | `queue` worker, `queue:retry`, `queue:failed`, `queue:flush` commands | CodeIgniter 4+ |
| `doctrine/doctrine-fixtures-bundle` | `doctrine:fixtures:load` command, 1 setup step | Symfony 4+ |
| `doctrine/doctrine-migrations-bundle` | `doctrine:migrations:migrate` command, 1 setup step | Symfony 4+ |
| `drush/drush` | `cron` worker, `site:install`, `cr`, `uli`, `updb`, `cex`, `cim` commands, 3 setup steps | Drupal 8+ |
| `helhum/typo3-console` | `setup` command | TYPO3 10-11 |
| `laravel/cloud-cli` | `cloud` runs on the host PHP | any framework |
| `laravel/horizon` | `horizon` worker | Laravel 6+ |
| `laravel/reverb` | `reverb` worker | Laravel 11+ |
| `nativephp/electron` | `native` worker, `native:install`, `native:build` commands, 1 doctor check | Laravel 11+ |
| `nativephp/mobile` | `native:install-mobile`, `native:jump`, `native:run`, `native:open` commands, 3 doctor checks | Laravel 11+ |
| `symfony/messenger` | `messenger` worker | Symfony 4+ |
| `symfony/scheduler` | `scheduler` worker | Symfony 8+ |
| `tempest/command-bus` | `command_bus` worker | Tempest 3+ |
| `tempest/database` | 1 setup step | Tempest 3+ |
| `typo3/cms-scheduler` | `scheduler` worker, `scheduler` command | TYPO3 10+ |

Missing one you use? [Add it](#package-definitions) — a package file is a dozen
lines, and it reaches every install within 24 hours like anything else here.

## Usage

You rarely touch the store directly: link a project and Lerd offers to install the matching definition for you. When you want to manage it by hand:

```bash
lerd framework search                # list everything available
lerd framework search symfony        # search by name
lerd framework install symfony       # auto-detects the version from composer.lock
lerd framework install laravel@12    # install a specific major version
lerd framework list --check          # compare your local definitions against the store
lerd framework update                # refresh all installed definitions
```

Installed definitions auto-refresh every 24 hours, so improvements landed here reach existing installs without an update.

## Contributing

New frameworks and version bumps are welcome — this store is only as good as the community around it.

1. Fork this repo
2. Add or update `frameworks/<name>/<version>.yaml`, or `packages/<vendor>-<name>.yaml` for something a composer package owns (see below)
3. Optionally add the framework's own mark as `frameworks/<name>.svg` (see below)
4. Add or update the entry in `frameworks/index.json` (name, label, versions, latest, detect rules), and list a new package under `packages`
5. Open a pull request

### Definition schema

Every definition declares a `version` matching the major release it targets, plus detection rules and whichever capabilities apply:

```yaml
name: myframework
version: "7"
label: My Framework
color: "#4a90d9"
public_dir: public
create: composer create-project myvendor/myapp:^7.0
detect:
  - composer: myvendor/myframework
php:
  min: "8.2"
env:
  # database/cache/service wiring, app key generation
workers:
  # queue, schedule, and other long-running processes
setup:
  # post-link commands (migrations, symlinks)
doctor:
  # declarative health checks
```

The `create` command is what `lerd new` hands to composer, and it has to name the
major the file is for. `lerd new` asks which major to scaffold and resolves this
definition from the answer, so a command that leaves the package unconstrained
installs the newest release whatever was picked, and the project on disk ends up
a major the definition was never written for.

### Package definitions

Most workers and commands are not really the framework's. A Horizon worker belongs
to `laravel/horizon`, a fixtures command to `doctrine/doctrine-fixtures-bundle`,
and written into the version files each one has to be repeated in every major of
every framework that can carry the package, then corrected in all of them at once.

A package declares them once, as `packages/<vendor>-<name>.yaml`, a sibling of the
`frameworks/` directory since a package is not a version of a framework, with the
composer name written as one file name:

```yaml
package: laravel/horizon
frameworks:                 # optional: which frameworks, and which of their majors
  - name: laravel
    min: "6"                # inclusive, as is max:, and either may be omitted
workers:                    # same shape as a definition's own
commands:
setup:
doctor:
```

Workers, commands, setup steps and doctor checks are the whole schema; env
wiring, detection and services stay with the framework. Lerd merges the package
onto the resolved definition when the project requires it in its `composer.json`
and the framework falls inside the range, an empty `frameworks:` list meaning
every framework. The package wins a name collision with the version file, which
is what lets an entry move here without being shadowed by the copy it left
behind. List the package under `packages` in `frameworks/index.json` as
`{"name": "vendor/package"}`, which is where lerd reads the set from; a file
nothing lists is never fetched.

When a major of the package itself changes what lerd runs, give that major its
own file, `<vendor>-<name>@<major>.yaml`, and list the majors in the index entry
(`{"name": "drush/drush", "versions": ["13", "11"], "latest": "13"}`). A
versioned file serves its own major and every later one until the next versioned
file, and the unversioned file serves everything below the first of them, so
adding a major is adding one file and no project is moved onto a definition
written for a version it does not have. Keep the unversioned file: it is what
older projects are served.

Each file is the whole answer for the versions it serves, not a patch on the one
before it. What a major *removes* has to be said out loud, since the copy the
declaration was lifted out of is still in the framework's version files and
silence there means keep it:

```yaml
removes:
  commands: [horizon:snapshot]
  workers: [horizon-metrics]
  setup: ["Publish Horizon assets"]   # a setup step by its label
  doctor: [horizon_supervisor]
```

The copies a package was lifted out of stay in the version files that already
shipped them: an install whose binary predates the package layer still reads
those, and deleting them would take the worker away from it. The package file is
the one that is maintained from here, since it is the one lerd prefers.

### The framework's own mark

A framework used to be a text label everywhere lerd showed it. It can now carry
its logo: add `frameworks/<name>.svg` beside the versioned directory, and declare
a `color:` in the YAML for the tint lerd paints it in.

The mark is per family, not per version, so one file serves every release and it
sits next to `<name>/` rather than inside it. The colour lives in the YAML, which
only exists per version, so repeat the same `color:` in each version file.

It is **monochrome**: one silhouette of filled paths with no `fill`, `stroke`,
`style` or `class` of its own, in a bare `<svg viewBox="...">`. lerd strips
everything but the geometry on the way in, along with script, `foreignObject`,
event handlers and external references, then paints it in the declared colour.
Not a full colour logo, and not a wordmark, which is unreadable at the size this
renders. Take the mark, not the lockup.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="…"/></svg>
```

`color:` must be a plain hex literal, `#ff2d20` or `#abc`; anything else is
dropped and the framework renders as its label alone. A framework with a colour
but no mark still gets the tint. The marks currently in this repo come from
[Simple Icons](https://simpleicons.org), which is CC0, except Magento's, which
comes from the project's own repo.

See the [frameworks documentation](https://lerd.sh/usage/frameworks) for the full schema reference and every available field.

## License

MIT
