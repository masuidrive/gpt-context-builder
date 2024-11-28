# GPT Context Builder

A web-based tool for creating context blocks for ChatGPT from local files.

![screenshot](screenshot.png)

## Features

- Browse and select local files through a tree view interface
- Generate formatted content blocks (XML or Markdown code blocks)
- Track token count for GPT-4 context window
- Copy formatted content to clipboard for easy pasting into ChatGPT
- Automatic handling of special characters and code blocks
- Support for .gitignore patterns

## Installation

```bash
pip install gpt-context-builder
```

## Usage

Basic usage:
```bash
gpt-context-builder
```

With options:
```bash
gpt-context-builder --port 8000 --root /path/to/project
```

Options:
- `--port`: Specify the port number (default: 5432)
- `--root`: Specify the root directory to serve (default: current directory)
- `--help`: Show help message

## Output Formats

1. XML Format:
```xml
<content filename="path/to/file.py">
file content here
</content>
```

2. Code Block Format:
````markdown
```path/to/file.py
file content here
```
````

## Author

- [Yuichiro Masui](https://github.com/masuidrive)

## Repository

- https://github.com/masuidrive/gpt-context-builder

## License

Apache License 2.0
