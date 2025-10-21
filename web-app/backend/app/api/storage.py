from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.conversion_service import ConversionService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/storage", tags=["storage"])

conversion_service = ConversionService()


class SearchQuery(BaseModel):
    query: str
    n_results: int = 5


class DeleteRequest(BaseModel):
    file_id: str


@router.get("/files")
async def list_stored_files(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    保存されたMarkdownファイルのリストを取得
    """
    try:
        files = await conversion_service.list_stored_files(limit=limit, offset=offset)
        return files
    except Exception as e:
        logger.error(f"Failed to list stored files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}")
async def get_stored_file(file_id: str) -> Dict[str, Any]:
    """
    特定のMarkdownファイルを取得
    """
    try:
        file_data = await conversion_service.get_stored_markdown(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        return file_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stored file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_similar_content(search_query: SearchQuery) -> List[Dict[str, Any]]:
    """
    類似コンテンツを検索
    """
    try:
        results = await conversion_service.search_similar_content(
            query=search_query.query,
            n_results=search_query.n_results
        )
        return results
    except Exception as e:
        logger.error(f"Failed to search similar content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}")
async def delete_stored_file(file_id: str) -> Dict[str, str]:
    """
    保存されたMarkdownファイルを削除
    """
    try:
        success = await conversion_service.delete_stored_file(file_id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found or deletion failed")
        return {"message": f"File {file_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete stored file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_storage_stats() -> Dict[str, Any]:
    """
    ストレージの統計情報を取得
    """
    try:
        if not conversion_service.enable_database:
            return {
                "database_enabled": False,
                "message": "Database services not initialized"
            }
        
        vector_stats = conversion_service.vector_db_service.get_collection_stats()
        
        return {
            "database_enabled": True,
            "vector_db_stats": vector_stats
        }
    except Exception as e:
        logger.error(f"Failed to get storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))