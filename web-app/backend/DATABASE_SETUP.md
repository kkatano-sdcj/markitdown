# Database Setup Guide

This guide explains how to set up Firebase and Vector Database for the Markitdown Web Application.

## Features

- **Firebase Firestore**: Store converted markdown files persistently
- **ChromaDB Vector Database**: Enable semantic search across your documents
- **Automatic Embeddings**: Generate and store embeddings for intelligent search

## Prerequisites

1. Python 3.11 or higher
2. Firebase project with Firestore enabled
3. Service account credentials for Firebase

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Firebase Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Follow the setup wizard

### Step 2: Enable Firestore

1. In your Firebase project, go to "Firestore Database"
2. Click "Create database"
3. Choose production or test mode
4. Select your region

### Step 3: Generate Service Account Credentials

1. Go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Save the JSON file securely

### Step 4: Configure the Application

Option 1: Using environment variables
```bash
export FIREBASE_CREDENTIALS_PATH=/path/to/your/service-account.json
```

Option 2: Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
# Edit .env file with your credentials
```

## Vector Database Setup

ChromaDB is used for vector storage and is automatically initialized when the application starts.

### Configuration

The vector database is stored locally by default in `./chroma_db`. You can change this location by setting:

```bash
export VECTOR_DB_PATH=/your/custom/path
```

## Enabling Database Features

To enable database features, set the following in your configuration:

```python
# In your startup code or configuration
conversion_service.initialize_databases(
    firebase_config=your_firebase_credentials,  # Optional: pass credentials directly
    vector_db_path="./chroma_db"  # Optional: custom path
)
```

Or use environment variables:
```bash
export ENABLE_DATABASE=true
export FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
```

## API Endpoints

Once configured, the following endpoints become available:

### Storage Management

- `GET /api/storage/files` - List all stored markdown files
- `GET /api/storage/files/{file_id}` - Get a specific markdown file
- `DELETE /api/storage/files/{file_id}` - Delete a stored file
- `POST /api/storage/search` - Search for similar content
- `GET /api/storage/stats` - Get storage statistics

### Search Request Example

```json
POST /api/storage/search
{
    "query": "machine learning algorithms",
    "n_results": 5
}
```

## Security Considerations

1. **Never commit credentials**: Keep your Firebase service account JSON file secure
2. **Use environment variables**: Store sensitive configuration in environment variables
3. **Restrict Firestore rules**: Configure appropriate security rules in Firebase Console
4. **API Rate Limiting**: Consider implementing rate limiting for production use

## Troubleshooting

### Firebase Connection Issues

If you see "Failed to initialize Firebase":
1. Check your service account JSON file path
2. Verify the file has correct permissions
3. Ensure Firestore is enabled in Firebase Console

### Vector Database Issues

If you see "Failed to initialize vector database":
1. Check write permissions for the vector DB path
2. Ensure sufficient disk space
3. Try deleting the `chroma_db` folder and restarting

### Memory Issues

For large document collections:
1. Consider chunking large documents
2. Implement pagination for listing operations
3. Use batch operations for bulk imports

## Performance Tips

1. **Batch Operations**: Use batch conversion with database saving for multiple files
2. **Indexing**: ChromaDB automatically indexes embeddings for fast retrieval
3. **Caching**: Frequently accessed documents are cached in memory
4. **Cleanup**: Regularly clean up old conversions to manage storage

## Support

For issues or questions:
1. Check the logs in the application
2. Review Firebase Console for quota or permission issues
3. Ensure all dependencies are correctly installed