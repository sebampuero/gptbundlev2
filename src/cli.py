import typer
from src.user.service import (
    create_user as service_create_user, 
    delete_user_by_email as service_delete_user,
    get_users as service_get_users
)
from src.user.models import UserCreate
from src.common.db import get_pg_db
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Admin CLI for user management")
console = Console()

@app.command()
def create_user(
    email: str = typer.Argument(..., help="The email of the user to create"),
    username: str = typer.Argument(..., help="The username of the user to create"),
    password: str = typer.Argument(..., help="The password for the new user"),
):
    user_in = UserCreate(email=email, username=username, password=password)
    
    db_gen = get_pg_db()
    session = next(db_gen)
    
    try:
        user = service_create_user(user_create=user_in, session=session)
        console.print(f"[green]Successfully created user:[/green] {user.username} ({user.email})")
    except Exception as e:
        console.print(f"[red]Error creating user:[/red] {e}")
    finally:
        # Since it's a generator that yields a session managed by a context manager, 
        # we don't strictly need to close it here if the generator logic handles it, 
        # but the current get_pg_db uses 'with Session(engine) as session:'
        pass

@app.command()
def delete_user(
    email: str = typer.Argument(..., help="The email of the user to delete"),
):
    db_gen = get_pg_db()
    session = next(db_gen)
    
    try:
        success = service_delete_user(email=email, session=session)
        if success:
            console.print(f"[green]Successfully deleted user with email:[/green] {email}")
        else:
            console.print(f"[yellow]User with email {email} not found.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error deleting user:[/red] {e}")

@app.command()
def list_users():
    db_gen = get_pg_db()
    session = next(db_gen)
    
    try:
        users = service_get_users(session=session)
        if not users:
            console.print("[yellow]No users found in the database.[/yellow]")
            return

        table = Table(title="GPTBundle Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Username", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Active", style="bold yellow")

        for user in users:
            table.add_row(
                str(user.id),
                user.username,
                user.email,
                "Yes" if user.is_active else "No"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing users:[/red] {e}")

if __name__ == "__main__":
    app()
