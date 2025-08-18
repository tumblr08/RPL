import os
import logging
from flask import Flask, request, jsonify, send_file
from strawberry.flask.views import GraphQLView
from werkzeug.utils import secure_filename
# Import the new data_store functions
from data_store import (
    get_document_by_id,
    create_document, # Added for document upload
    delete_document_from_db, # Added for document deletion in schema
    get_all_users, get_all_projects, get_all_tasks, get_all_consultations, get_all_evaluations, get_all_documents,
    get_user_by_email, get_user_by_id, get_documents_by_project, get_documents_by_task,
    create_user, create_project, create_task, update_task, create_consultation, create_team_evaluation # Add new create/update functions
)
from schema import schema # Keep schema import
import datetime
from flask_cors import CORS
from models import Document, User, Project, Task, Consultation, TeamEvaluation, ChecklistItem # Import all models

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

CORS(app)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'zip', 'rar', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# GraphQL endpoint
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema, graphiql=True),
    methods=["GET", "POST"]
)

# Add debug route to check if Flask is working
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        'message': 'Flask server is running!',
        'endpoints': {
            'graphql': '/graphql',
            'upload': '/upload (POST)',
            'download': '/download/<id> (GET)',
            'health': '/health (GET)'
        }
    })

def upload_file_post():
    """Handle file uploads via REST endpoint"""
    try:
        print(f"Request method: {request.method}")
        print(f"Request files: {request.files}")
        print(f"Request form: {request.form}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        print(f"File received: {file.filename}")

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid filename conflicts
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
            unique_filename = f"{timestamp}{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save the file
            file.save(file_path)
            print(f"File saved to: {file_path}")

            # Get file info
            file_size = os.path.getsize(file_path)
            content_type = file.content_type or 'application/octet-stream'

            # Get additional parameters from form data
            project_id_str = request.form.get('project_id')
            task_id_str = request.form.get('task_id')
            uploaded_by_str = request.form.get('uploaded_by')

            project_id = int(project_id_str) if project_id_str else None
            task_id = int(task_id_str) if task_id_str else None
            uploaded_by = int(uploaded_by_str) if uploaded_by_str else None

            # Create document record using the data_store function
            # No need to manually calculate new ID; create_document will handle it
            document = Document(
                id=0, # ID will be assigned by DB
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                content_type=content_type,
                uploaded_at=datetime.datetime.now(),
                project_id=project_id,
                task_id=task_id,
                uploaded_by=uploaded_by
            )
            
            # Use the new create_document from data_store
            new_document = create_document(document)
            
            if new_document:
                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully',
                    'document': {
                        'id': new_document.id,
                        'filename': new_document.filename,
                        'file_size': new_document.file_size,
                        'content_type': new_document.content_type,
                        'uploaded_at': new_document.uploaded_at.isoformat()
                    }
                })
            else:
                # If database insertion fails, delete the uploaded file
                os.remove(file_path)
                return jsonify({'error': 'Failed to save document record to database'}), 500
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Handle both with and without trailing slash
@app.route("/upload/", methods=["GET", "POST", "OPTIONS"])
@app.route("/upload", methods=["GET", "POST", "OPTIONS"])
def upload_file_handler():
    """Handle file uploads and OPTIONS requests"""
    if request.method == "OPTIONS":
        # Handle preflight requests
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

    elif request.method == "GET":
        # Return upload form or info for testing
        return jsonify({
            'message': 'Upload endpoint is working',
            'method': 'POST',
            'content_type': 'multipart/form-data',
            'required_field': 'file',
            'optional_fields': ['project_id', 'task_id', 'uploaded_by'],
            'max_file_size': '16MB',
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        })

    # Handle POST request (actual upload)
    return upload_file_post()

# Add this new endpoint to your Flask app:

@app.route("/upload-form", methods=["GET"])
def upload_form():
    """Simple upload form for testing"""
    html_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Upload Test</title>
    </head>
    <body>
        <h2>File Upload Test</h2>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <div>
                <label for="file">Choose file:</label>
                <input type="file" id="file" name="file" required>
            </div>
            <br>
            <div>
                <label for="project_id">Project ID (optional):</label>
                <input type="number" id="project_id" name="project_id">
            </div>
            <br>
            <div>
                <label for="task_id">Task ID (optional):</label>
                <input type="number" id="task_id" name="task_id">
            </div>
            <br>
            <div>
                <label for="uploaded_by">Uploaded by (optional):</label>
                <input type="number" id="uploaded_by" name="uploaded_by">
            </div>
            <br>
            <button type="submit">Upload File</button>
        </form>
    </body>
    </html>
    '''
    return html_form

@app.route("/download/<int:document_id>", methods=["GET"])
def download_file(document_id):
    """Download a file by document ID"""
    try:
        document = get_document_by_id(document_id) # Uses updated data_store function
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        if not os.path.exists(document.file_path):
            return jsonify({'error': 'File not found on disk'}), 404

        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.filename,
            mimetype=document.content_type
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/files/<int:document_id>/info", methods=["GET"])
def get_file_info(document_id):
    """Get file information without downloading"""
    try:
        document = get_document_by_id(document_id) # Uses updated data_store function
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        return jsonify({
            'id': document.id,
            'filename': document.filename,
            'file_size': document.file_size,
            'content_type': document.content_type,
            'uploaded_at': document.uploaded_at.isoformat(),
            'project_id': document.project_id,
            'task_id': document.task_id,
            'uploaded_by': document.uploaded_by
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'graphql_endpoint': '/graphql',
        'upload_endpoint': '/upload',
        'max_file_size': '16MB',
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@app.before_request
def log_request_info():
    if request.path == '/graphql' and request.method == 'POST':
        print("\n--- Incoming GraphQL Request ---")
        print(f"Path: {request.path}, Method: {request.method}")
        print("Headers:")
        for header, value in request.headers.items():
            print(f"  {header}: {value}")
        try:
            # Mencoba mendapatkan JSON payload. Ini akan mengembalikan None jika bukan JSON valid.
            json_data = request.get_json(silent=True)
            print("JSON Payload:")
            print(json_data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print("Raw Request Data:")
            print(request.data) # Ini akan menunjukkan data mentah yang diterima
        print("--- End Request Info ---\n")

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'Check if you are using the correct HTTP method',
        'available_methods': ['GET', 'POST', 'OPTIONS']
    }), 405

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("=== ENVIRONMENT VARIABLES ===")
logger.info(f"PORT: {os.environ.get('PORT', 'NOT SET')}")
logger.info(f"DB_HOST: {os.environ.get('DB_HOST', 'NOT SET')}")
logger.info(f"DB_PORT: {os.environ.get('DB_PORT', 'NOT SET')}")
logger.info(f"MYSQL_HOST: {os.environ.get('MYSQL_HOST', 'NOT SET')}")
logger.info(f"MYSQL_PORT: {os.environ.get('MYSQL_PORT', 'NOT SET')}")

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Using port: {port}")
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")