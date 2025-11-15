"""Typer CLI for the OCRO project."""
from __future__ import annotations

import json
import logging

import typer

from ..scoring import ScoringEngine

logging.basicConfig(level=logging.INFO)

app = typer.Typer(help="On-Chain Reputation Oracle CLI")
engine = ScoringEngine()


@app.command()
def score(address: str, json_output: bool = typer.Option(False, "--json", "-j")) -> None:
    """Calculate and display the reputation score for an address."""

    details = engine.calculate(address)
    if json_output:
        typer.echo(
            json.dumps(
                {"address": address, "score": details.score, "details": details.to_dict()},
                indent=2,
            )
        )
    else:
        typer.echo(f"Address: {address}")
        typer.echo(f"Score  : {details.score}/1000")
        for name, value in details.to_dict().items():
            typer.echo(f" - {name}: {value}")


if __name__ == "__main__":  # pragma: no cover
    app()
