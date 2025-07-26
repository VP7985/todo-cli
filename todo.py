import typer
from rich.console import Console
from rich.table import Table
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Configuration ---
TASKS_FILE = "tasks.json"
console = Console()
app = typer.Typer()

# --- Helper Functions ---
def load_tasks() -> List[Dict[str, Any]]:
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_tasks(tasks: List[Dict[str, Any]]):
    """Saves tasks to the JSON file."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def get_next_id() -> int:
    """Gets the next available ID for a new task."""
    tasks = load_tasks()
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

# --- CLI Commands ---

@app.command(short_help="Adds a new task to your list.")
def add(description: str = typer.Argument(..., help="The description of the task to add.")):
    """Adds a new task with the given DESCRIPTION to your to-do list."""
    tasks = load_tasks()
    new_task = {
        "id": get_next_id(),
        "description": description,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    tasks.append(new_task)
    save_tasks(tasks)
    console.print(f"[bold green]✅ Added task:[/bold green] '{description}'")

@app.command(short_help="Lists all tasks.")
def list(hide_done: bool = typer.Option(False, "--hide-done", "-h", help="Hide tasks that are already marked as done.")):
    """
    Lists all tasks.
    
    Shows a table with ID, Status, and Description.
    Use --hide-done to filter out completed tasks.
    """
    tasks = load_tasks()
    if not tasks:
        console.print("[bold yellow]No tasks found. Add one with 'add' command![/bold yellow]")
        return

    table = Table(title="My To-Do List", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Status", width=8)
    table.add_column("Description", style="bold", min_width=20)
    
    for task in sorted(tasks, key=lambda x: x['id']):
        if hide_done and task['status'] == 'done':
            continue
            
        status_color = "green" if task['status'] == 'done' else "yellow"
        status_icon = "✅" if task['status'] == 'done' else "⏳"
        status_text = f"[{status_color}]{status_icon} {task['status'].capitalize()}[/{status_color}]"
        
        table.add_row(
            str(task['id']),
            status_text,
            task['description']
        )
    console.print(table)


@app.command(short_help="Marks a task as complete.")
def done(task_id: int = typer.Argument(..., help="The ID of the task to mark as complete.")):
    """Marks a task as 'done' using its ID."""
    tasks = load_tasks()
    task_to_complete = next((task for task in tasks if task['id'] == task_id), None)

    if not task_to_complete:
        console.print(f"[bold red]Error:[/bold red] Task with ID {task_id} not found.")
        raise typer.Exit(code=1)

    if task_to_complete['status'] == 'done':
        console.print(f"[bold yellow]Warning:[/bold yellow] Task {task_id} is already marked as done.")
    else:
        task_to_complete['status'] = 'done'
        save_tasks(tasks)
        console.print(f"[bold green]🎉 Task {task_id} marked as complete![/bold green]")


@app.command(short_help="Deletes a task.")
def delete(task_id: int = typer.Argument(..., help="The ID of the task to delete.")):
    """Deletes a task from the list using its ID."""
    tasks = load_tasks()
    original_count = len(tasks)
    
    tasks = [task for task in tasks if task['id'] != task_id]

    if len(tasks) == original_count:
        console.print(f"[bold red]Error:[/bold red] Task with ID {task_id} not found.")
        raise typer.Exit(code=1)

    save_tasks(tasks)
    console.print(f"[bold green]🗑️ Task {task_id} deleted successfully.[/bold green]")


if __name__ == "__main__":
    app()