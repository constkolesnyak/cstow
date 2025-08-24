# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Package Management & Dependencies
- `poetry install` - Install dependencies
- `poetry shell` - Activate the virtual environment
- `poetry add <package>` - Add new dependency
- `poetry add --group dev <package>` - Add development dependency

### Testing
- `pytest` - Run all tests with verbose output (configured in pyproject.toml)
- `pytest -m smoke` - Run smoke tests only (integration tests with actual stow operations)
- `pytest tests/command_test.py` - Run specific test file
- `pytest tests/config_test.py::test_good_configs` - Run specific test

### Coverage
- `coverage run -m pytest` - Run tests with coverage
- `coverage report` - Show coverage report
- `coverage html` - Generate HTML coverage report

### Running the Application
- `poetry run cstow` - Run with default 'no' action (dry run)
- `poetry run cstow stow` - Execute stow action
- `poetry run cstow delete --plain` - Run delete action with plain text output
- Set `CSTOW_CONFIG_PATH` environment variable to point to your config file

### Building & Publishing
- `poetry build` - Build the package
- `poetry publish --build` - Build and publish to PyPI (used in CI)

## Code Architecture

### High-Level Structure
Cstow is a GNU Stow wrapper that provides a rich UI and configuration support. It follows a clean separation of concerns with distinct layers:

### Core Components

**Entry Point (`main.py`)**
- Uses Python Fire for CLI parsing
- Handles error presentation and program flow
- Coordinates between config, command parsing, and execution

**Command Layer (`command.py`)**
- `CmdAction`: Enum defining GNU Stow actions (no, stow, restow, delete)  
- `CmdPlaceholders`: Template system for constructing GNU Stow commands
- Handles command validation and shell-safe quoting

**Configuration System (`config.py`)**
- Pydantic-based validation for TOML configuration files
- Environment variable expansion (`~` and `$VAR`)
- Complex validation for target/directory relationships
- Default template: `stow --${action} --no-folding --verbose --target=${target} --dir=${dir} . 2>&1 | grep --invert-match --regexp="^BUG" --regexp="^WARN"`

**Execution Engine (`stow.py`)**
- Orchestrates the actual stow operations
- Subprocess execution with proper error handling
- Dependency injection pattern for testing (Run callable)

**View Layer (`view.py`)**
- Abstract base class with PlainView and RichView implementations
- RichView provides colored output with custom GNU Stow syntax highlighting
- Separates stdout and stderr presentation

### Key Patterns

**Configuration-Driven Execution**
The application is built around a TOML configuration that maps target directories to arrays of stow directories. Each target-directory pair generates a separate GNU Stow command execution.

**Template-Based Command Generation** 
GNU Stow commands are generated from a customizable template with placeholders for action, target, and directory. This allows users to modify the underlying stow behavior while maintaining type safety.

**Testable Architecture**
The codebase uses dependency injection (particularly for the Run function in stow.py) to enable testing without actual filesystem operations.

### Testing Strategy

**Integration Tests (`smoke` marker)**
Tests that perform actual stow/unstow operations using test data in `tests/testing_data/`. These verify the complete workflow including config parsing, command generation, and filesystem operations.

**Unit Tests**
Focused tests for individual components like configuration validation and command parsing.

**Test Data Structure**
- `tests/testing_data/configs/good_*` - Valid configuration files
- `tests/testing_data/configs/bad_*` - Invalid configurations for error testing
- `tests/testing_data/dir/` and `tests/testing_data/target/` - Test filesystem structure

### Error Handling Philosophy
The application provides user-friendly error messages by catching low-level exceptions (Pydantic validation, file I/O) and re-raising as domain-specific exceptions with contextual information.
