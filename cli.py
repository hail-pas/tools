import typer

cli = typer.Typer(help="Tranlate CLI")

@cli.command()
def hello(name: str = None):
    if name:
        typer.echo(f"Hello {name}")
    else:
        typer.echo("Hello World!")


if __name__ == "__main__":
    cli()
