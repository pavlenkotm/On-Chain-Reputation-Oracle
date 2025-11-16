# On-Chain Reputation Oracle (OCRO)

On-Chain Reputation Oracle (OCRO) is a small yet realistic Web3 tool that
estimates a reputation score for any EVM wallet. It exposes the scoring engine
through a FastAPI service and a Typer-based CLI, making it easy to integrate
with other applications or experiments.

## Features

- Deterministic reputation scoring in the range of 0–1000
- Modular metric abstraction with support for new chains or signals
- Activity consistency signal that rewards steady, organic usage
- Ethereum data provider with mock mode for local development
- FastAPI REST endpoints and Typer CLI entry point
- Comprehensive unit tests covering scoring logic and provider fallbacks

## Quickstart

### 1. Setup a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Configure environment

Set a real Ethereum RPC endpoint or enable mock mode:

```bash
export OCRO_ETH_RPC_URL="https://mainnet.infura.io/v3/<token>"
# or
export OCRO_MOCK_MODE=true
```

### 4. Run the API

```bash
uvicorn ocro.api.main:app --reload
```

### 5. Run the CLI

```bash
ocro score 0x000000000000000000000000000000000000dEaD
```

Add `-j` to receive JSON output.

### 6. Run tests

```bash
pytest
```

## Notes

This project is purely experimental and educational. It does **not** constitute
financial advice and should not be relied upon for on-chain security decisions.
