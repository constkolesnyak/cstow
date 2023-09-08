# Cstow

![Demo](misc/demo.gif)

## About

There's lots of [dotfiles managers](https://wiki.archlinux.org/title/Dotfiles#Tools),
but my favorite is [GNU Stow](https://www.gnu.org/software/stow).

It has only two problems: boring UI and no config. Cstow solves them.

### Name

`C`on`st`antine's GNU St`ow` wrapper.

### Some [GNU Stow Terminology](https://www.gnu.org/software/stow/manual/stow.html#Terminology)

> A target directory is the root of a tree in which one or more packages wish to appear to be installed.

> A stow directory is the root of a tree containing separate packages in private subtrees.

## Installation

Use [pipx](https://pypa.github.io/pipx)

    pipx install cstow

Or pip

    pip install cstow

## Configuration

Set `CSTOW_CONFIG_PATH` to `path/to/your/cstow_config.toml`.
Use any file name you want.

### Examples

- My [cstow.toml](https://github.com/constkolesnyak/dotfiles/blob/main/cstow.toml).
- More [examples](tests/testing_data/configs).

### Config Contents

Cstow expands `~` and `$AN_ENVIRONMENT_VARIABLE`.

| Name                 | Type             | Description                             | Default               |
| -------------------- | ---------------- | --------------------------------------- | --------------------- |
| root_dir             | String           | The root of stow directories            | /                     |
| cmd_template         | String           | The [template][0] for GNU Stow commands | [See below](#default) |
| targets_dirs         | Table            | Targets (keys) and dirs (values)        |                       |
| targets_dirs (key)   | String           | A target directory                      |                       |
| targets_dirs (value) | Array of strings | Stow directories for the target         |                       |

[0]: https://peps.python.org/pep-0292/#a-simpler-proposal

### root_dir

You might set it to `~/dotfiles` or `$DOTFILES`.

If you don't set `root_dir`, use absolute paths in `targets_dirs`.

### cmd_template

You can set it to any shell command that contains every placeholder.

| Placeholder | Description                                       |
| ----------- | ------------------------------------------------- |
| action      | A GNU Stow action ([no, stow, restow, delete][1]) |
| target      | A target directory                                |
| dir         | A stow directory for the target                   |

[1]: https://www.gnu.org/software/stow/manual/stow.html#Invoking-Stow

#### Default

    stow --$action --no-folding --verbose --target=$target --dir=$dir . \
         2>&1 | grep --invert-match --regexp="^BUG" --regexp="^WARN"

## Usage

    # Get some help
    cstow -h
    cstow --help

    # Run an action
    cstow               # Default action is 'no'
    cstow delete        # Action is a positional argument
    cstow -a restow     # But flags also work
    cstow --action no

    # Print plain text
    cstow stow --plain
    cstow restow -p
    cstow -p -a delete
