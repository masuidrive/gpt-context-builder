from flask import Flask, jsonify, Response, request, send_from_directory
import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import tiktoken
import pkg_resources
from werkzeug.serving import WSGIRequestHandler

def create_app():
    # 開発サーバーの警告を抑制
    WSGIRequestHandler.log_request = lambda *args, **kwargs: None
    
    app = Flask(__name__)
    # プロダクションモードを設定
    app.env = 'production'
    app.debug = False

    def count_tokens(text):
        """Count tokens using GPT-4's tokenizer to track context window usage"""
        try:
            enc = tiktoken.encoding_for_model("gpt-4")
            return len(enc.encode(text))
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0

    def load_gitignore():
        """Load and parse .gitignore file to exclude ignored files from the tree view"""
        try:
            with open('.gitignore', 'r') as f:
                spec = PathSpec.from_lines(GitWildMatchPattern, f.readlines())
            return spec
        except FileNotFoundError:
            return PathSpec.from_lines(GitWildMatchPattern, [])

    def get_directory_structure(path, gitignore_spec):
        """Recursively build a tree structure of the directory while respecting gitignore rules"""
        result = []
        base_path = os.getcwd()
        
        try:
            for entry in os.scandir(path):
                # Convert path to relative path for gitignore checking
                rel_path = os.path.relpath(entry.path, base_path)
                
                # Skip if matches gitignore patterns
                if gitignore_spec.match_file(rel_path):
                    continue
                    
                if entry.name.startswith('.'):
                    continue
                    
                if entry.is_file():
                    result.append({
                        'type': 'file',
                        'path': rel_path,
                        'name': entry.name
                    })
                elif entry.is_dir():
                    children = get_directory_structure(entry.path, gitignore_spec)
                    if children:  # Only add directories that have visible children
                        result.append({
                            'type': 'directory',
                            'path': rel_path,
                            'name': entry.name,
                            'children': children
                        })
        except Exception as e:
            print(f"Error scanning directory {path}: {e}")
            
        return sorted(result, key=lambda x: (x['type'] != 'directory', x['name'].lower()))

    @app.route('/')
    def index():
        """Serve the main application page"""
        template_dir = pkg_resources.resource_filename('gpt_context_builder', 'templates')
        return send_from_directory(template_dir, 'index.html')

    @app.route('/files')
    def list_files():
        """Return the directory structure as JSON, excluding gitignored files"""
        try:
            gitignore_spec = load_gitignore()
            structure = get_directory_structure(os.getcwd(), gitignore_spec)
            return jsonify(structure)
        except Exception as e:
            print(f"Error in list_files: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/file/<path:filepath>')
    def get_file_content(filepath):
        """Read and return the content of a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 出力フォーマットに応じて処理を変える
            output_format = request.args.get('format', 'xml')  # デフォルトはxml
            
            if output_format == 'code':
                # コードブロックの場合は何もエスケープしない
                return jsonify({'content': content})
            else:
                # XMLフォーマットの場合は < > のみをエスケープ
                content = content.replace('<', '&lt;').replace('>', '&gt;')
                return jsonify({'content': content})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/count_tokens', methods=['POST'])
    def count_tokens_endpoint():
        """Calculate the number of GPT-4 tokens in the given text"""
        try:
            text = request.json.get('text', '')
            count = count_tokens(text)
            return jsonify({'count': count})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
