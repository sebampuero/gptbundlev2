import typer
from gptbundle.user.service import (
    create_user as service_create_user, 
    delete_user_by_email as service_delete_user,
    get_users as service_get_users
)
from gptbundle.user.models import UserCreate
from gptbundle.common.db import get_pg_db
from gptbundle.messaging.models import Chat as ChatModel
from gptbundle.messaging.repository import ChatRepository
from rich.console import Console
from rich.table import Table
from datetime import datetime

app = typer.Typer(help="Admin CLI for user and chat management")
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

@app.command()
def list_chats():
    try:
        chats = list(ChatModel.scan())
        if not chats:
            console.print("[yellow]No chats found in DynamoDB.[/yellow]")
            return

        table = Table(title="GPTBundle Chats")
        table.add_column("Chat ID", style="cyan", no_wrap=True)
        table.add_column("User Email", style="green")
        table.add_column("Timestamp", style="magenta")
        table.add_column("Messages", style="bold yellow")

        for chat in chats:
            dt_object = datetime.fromtimestamp(chat.timestamp)
            formatted_ts = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            
            table.add_row(
                chat.chat_id,
                chat.user_email,
                formatted_ts,
                str(len(chat.messages))
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing chats:[/red] {e}")

@app.command()
def delete_chat(
    chat_id: str = typer.Argument(..., help="The ID of the chat to delete"),
    timestamp: float = typer.Argument(..., help="The timestamp of the chat to delete"),
):
    repo = ChatRepository()
    try:
        success = repo.delete_chat(chat_id, timestamp)
        if success:
            console.print(f"[green]Successfully deleted chat:[/green] {chat_id} at {timestamp}")
        else:
            console.print(f"[yellow]Chat with ID {chat_id} and timestamp {timestamp} not found.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error deleting chat:[/red] {e}")

@app.command()
def delete_chats_by_email(
    email: str = typer.Argument(..., help="The email of the user whose chats should be deleted"),
):
    try:
        chats = list(ChatModel.user_email_index.query(email))
        if not chats:
            console.print(f"[yellow]No chats found for email:[/yellow] {email}")
            return
        
        count = 0
        repo = ChatRepository()
        for chat in chats:
            if repo.delete_chat(chat.chat_id, chat.timestamp):
                count += 1
        
        console.print(f"[green]Successfully deleted {count} chats for email:[/green] {email}")
    except Exception as e:
        console.print(f"[red]Error deleting chats by email:[/red] {e}")

@app.command(help="Deletes all chats. WARNING: use only in development environment!")
def delete_all_chats():
    try:
        chats = list(ChatModel.scan())
        if not chats:
            console.print("[yellow]No chats found in DynamoDB.[/yellow]")
            return
        
        count = 0
        repo = ChatRepository()
        for chat in chats:
            if repo.delete_chat(chat.chat_id, chat.timestamp):
                count += 1
        
        console.print(f"[green]Successfully deleted {count} chats.[/green]")
    except Exception as e:
        console.print(f"[red]Error deleting all chats:[/red] {e}")

if __name__ == "__main__":
    app()
