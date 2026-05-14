# envault

> Secure local `.env` file manager with per-project encryption and shell integration for seamless switching.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a vault for your project:**
```bash
envault init
```

**Store and encrypt your `.env` file:**
```bash
envault lock .env
```

**Load variables into your current shell session:**
```bash
eval "$(envault unlock)"
```

**Switch between project environments:**
```bash
envault use my-project
eval "$(envault unlock)"
```

**List all managed vaults:**
```bash
envault list
```

Each vault is encrypted with a unique key derived from your system and project path, ensuring secrets never sit in plaintext on disk.

---

## Shell Integration

Add the following to your `.bashrc` or `.zshrc` for automatic environment switching when entering a project directory:

```bash
source <(envault shell-hook)
```

---

## License

[MIT](LICENSE) © 2024 envault contributors