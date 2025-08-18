# GraphQL Query Examples

## Queries

### Get All Projects with Documents
```graphql
query GetProjectsWithDocuments {
  allProjects {
    id
    title
    description
    deadline
    ownerId
    documents {
      id
      filename
      fileSize
      contentType
      uploadedAt
      uploader {
        name
        email
      }
    }
  }
}
```

### Get All Tasks with Documents
```graphql
query GetTasksWithDocuments {
  allTasks {
    id
    title
    projectId
    checklist {
      item
      done
    }
    comments
    documents {
      id
      filename
      fileSize
      contentType
      uploadedAt
    }
  }
}
```

### Get All Documents
```graphql
query GetAllDocuments {
  allDocuments {
    id
    filename
    filePath
    fileSize
    contentType
    uploadedAt
    projectId
    taskId
    uploadedBy
    uploader {
      name
      email
    }
  }
}
```

### Get Specific Document
```graphql
query GetDocument($documentId: ID!) {
  getDocument(documentId: $documentId) {
    id
    filename
    fileSize
    contentType
    uploadedAt
    projectId
    taskId
    uploader {
      name
      email
    }
  }
}
```

## Mutations

### Register User
```graphql
mutation RegisterUser {
  register(input: {
    name: "John Doe"
    email: "john@example.com"
    password: "password123"
  }) {
    ok
    message
    user {
      id
      name
      email
    }
  }
}
```

### Login User
```graphql
mutation LoginUser {
  login(input: {
    email: "john@example.com"
    password: "password123"
  }) {
    ok
    message
    user {
      id
      name
      email
    }
  }
}
```

### Create Project
```graphql
mutation CreateProject {
  createProject(input: {
    title: "My New Project"
    description: "This is a test project"
    deadline: "2024-12-31"
    ownerId: "1"
  }) {
    id
    title
    description
    deadline
    ownerId
  }
}
```

### Upload Document (via GraphQL)
```graphql
mutation UploadDocument {
  uploadDocument(input: {
    filename: "document.pdf"
    fileSize: 1024000
    contentType: "application/pdf"
    projectId: "1"
    uploadedBy: "1"
  }) {
    success
    message
    document {
      id
      filename
      fileSize
      contentType
      uploadedAt
      projectId
      uploader {
        name
      }
    }
  }
}
```

### Delete Document
```graphql
mutation DeleteDocument($documentId: ID!) {
  deleteDocument(documentId: $documentId) {
    success
    message
  }
}
```

### Create Task
```graphql
mutation CreateTask {
  createTask(input: {
    projectId: "1"
    title: "New Task"
  }) {
    id
    title
    projectId
    checklist {
      item
      done
    }
    comments
  }
}
```

### Add Checklist Item
```graphql
mutation AddChecklistItem {
  addChecklistItem(input: {
    taskId: "1"
    item: "Complete documentation"
  }) {
    id
    title
    checklist {
      item
      done
    }
  }
}
```

### Add Comment to Task
```graphql
mutation AddComment {
  addCommentToTask(input: {
    taskId: "1"
    comment: "This task is in progress"
  }) {
    id
    title
    comments
  }
}
```

### Mark Checklist Item Done
```graphql
mutation MarkChecklistDone {
  markChecklistItemDone(input: {
    taskId: "1"
    item: "Complete documentation"
  }) {
    id
    title
    checklist {
      item
      done
    }
  }
}
```

### Create Consultation
```graphql
mutation CreateConsultation {
  createConsultation(input: {
    projectId: "1"
    dosenName: "Dr. Smith"
    datetime: "2024-01-15 10:00:00"
    topic: "Project Progress Review"
  }) {
    id
    projectId
    dosenName
    datetime
    topic
  }
}
```

### Create Team Evaluation
```graphql
mutation CreateEvaluation {
  createTeamEvaluation(input: {
    projectId: "1"
    evaluator: "Team Lead"
    score: 85
    comment: "Great progress on the project"
  }) {
    id
    projectId
    evaluator
    score
    comment
  }
}
```

## REST API Endpoints

### Upload File via REST
```bash
# Upload file with curl
curl -X POST http://localhost:5000/upload \
  -F "file=@/path/to/your/file.pdf" \
  -F "project_id=1" \
  -F "uploaded_by=1"
```

### Download File
```bash
# Download file by document ID
curl -X GET http://localhost:5000/download/1 \
  -o downloaded_file.pdf
```

### Get File Info
```bash
# Get file information
curl -X GET http://localhost:5000/files/1/info
```

### Health Check
```bash
# Check API health
curl -X GET http://localhost:5000/health
```

## Usage Examples

### Frontend JavaScript Example
```javascript
// Upload file using fetch API
async function uploadFile(file, projectId, userId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', projectId);
  formData.append('uploaded_by', userId);

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    if (result.success) {
      console.log('File uploaded successfully:', result.document);
      return result.document;
    } else {
      console.error('Upload failed:', result.error);
    }
  } catch (error) {
    console.error('Upload error:', error);
  }
}

// GraphQL query using fetch
async function getProjectDocuments(projectId) {
  const query = `
    query GetProjectDocuments($projectId: ID!) {
      allProjects {
        id
        title
        documents {
          id
          filename
          fileSize
          uploadedAt
        }
      }
    }
  `;

  try {
    const response = await fetch('/graphql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables: { projectId }
      })
    });

    const result = await response.json();
    return result.data;
  } catch (error) {
    console.error('GraphQL error:', error);
  }
}
```