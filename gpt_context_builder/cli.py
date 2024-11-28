import click
import os
from .server import create_app

@click.command()
@click.option('--port', default=5432, help='Port to run the server on')
@click.option('--root', default='.', help='Root directory to serve files from')
@click.option('--debug', default=False, help='Debug mode')
def main(port, root, debug):
    """Start the GPT Context Builder server"""
    # Convert relative path to absolute path
    root = os.path.abspath(root)
    
    if not os.path.exists(root):
        click.echo(f"Error: Directory '{root}' does not exist")
        return
    
    # Change to the specified root directory
    os.chdir(root)
    
    click.echo(f"Starting server at http://localhost:{port}")
    click.echo(f"Serving files from: {root}")
    
    app = create_app()
    app.run(debug=debug, port=port)

if __name__ == '__main__':
    main()
