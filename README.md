
# pr-why

Understand what a pull request changes, with a clear explanation grounded in its diff. `pr-why` is a small Python CLI that can summarize changed files offline or ask an OpenAI-compatible model to explain the change.

## Install

Requires Python 3.10 or newer. From a clone of this repository:

```bash
python3 -m pip install .
```

## Use without an API key

```bash
pr-why --pr psf/requests#7579
```

This mode fetches the public GitHub pull request diff and reports changed paths and addition/deletion counts. You can also provide a diff file or pipe one in:

```bash
pr-why --diff change.patch
git diff origin/main...HEAD | pr-why
```

## Use an OpenAI-compatible model API

The key remains on your machine. Set it in your shell, then choose the model and API base URL for your provider:

```bash
export OPENAI_API_KEY="your-key"
export PR_WHY_BASE_URL="https://api.openai.com/v1"
export PR_WHY_MODEL="gpt-4o-mini"
pr-why --pr psf/requests#7579
```

Or pass `--api-key`, `--base-url`, and `--model`. `--base-url` expects an OpenAI-compatible Chat Completions endpoint. Provider compatibility, model names, usage limits, and pricing depend on your provider. Never commit API keys.

Save a report with `--output report.md`.

## Current limits

This is an early project. Model explanations depend on the provider and may be wrong; always review the original diff. The initial release accepts public GitHub PRs and unified diffs. Private repositories and other API formats are not supported yet.

## Development

Tests run directly from a checkout with Python 3.10 or newer:

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT
