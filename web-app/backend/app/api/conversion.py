"""
ファイル変換APIエンドポイント
ファイルのアップロードと変換処理を管理
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from models.data_models import (
    ConversionResult, BatchConversionResult, ConversionStatus
)
from pydantic import BaseModel
from services.conversion_service import ConversionService
from services.api_service import APIService
from services.enhanced_conversion_service import EnhancedConversionService
from api.websocket import manager
from services.cancel_manager import cancel_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# サービスのインスタンス化
conversion_service = ConversionService()
api_service = APIService()
enhanced_service = EnhancedConversionService()

class URLConversionRequest(BaseModel):
    """URL変換リクエストモデル"""
    url: str
    use_api_enhancement: bool = False

class EnhancedConversionRequest(BaseModel):
    """Enhanced conversion request with AI mode"""
    use_ai_mode: bool = False

@router.post("/upload", response_model=ConversionResult)
async def upload_and_convert(
    file: UploadFile = File(...),
    use_api_enhancement: bool = False,
    use_ai_mode: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    ファイルをアップロードして変換
    
    Args:
        file: アップロードするファイル
        use_api_enhancement: OpenAI APIによる強化を使用するか
    
    Returns:
        ConversionResult: 変換結果
    """
    # ファイル形式の確認
    if not conversion_service.is_supported_format(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"サポートされていないファイル形式です。サポート形式: {', '.join(conversion_service.supported_formats)}"
        )
    
    # ファイルサイズの確認（10MB制限）
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ファイルサイズが10MBを超えています")
    
    # アップロードディレクトリにファイルを保存
    upload_path = os.path.join("./uploads", file.filename)
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {e}")
        raise HTTPException(status_code=500, detail="ファイルのアップロードに失敗しました")
    
    # ファイルを変換（プログレスコールバック付き）
    output_filename = f"{os.path.splitext(file.filename)[0]}.md"
    
    # Generate conversion ID first
    import uuid
    conversion_id = str(uuid.uuid4())
    logger.info(f"Starting conversion for file: {file.filename}, conversion_id: {conversion_id}")
    
    # Send initial progress
    await manager.send_progress(conversion_id, 0, "processing", "変換処理を開始中...", file.filename)
    
    async def progress_callback(conv_id: str, progress: int, status: str, step: str, filename: str):
        # Use the pre-generated conversion_id for consistency
        await manager.send_progress(conversion_id, progress, status, step, filename or file.filename)
    
    result = await conversion_service.convert_file(
        upload_path, 
        output_filename, 
        use_ai_mode=use_ai_mode,
        progress_callback=progress_callback
    )
    
    # Update result with our conversion_id
    if result:
        result.id = conversion_id
        # Send final progress
        await manager.send_progress(conversion_id, 100, "completed", "変換完了", file.filename)
    
    # API強化が有効な場合
    if use_api_enhancement and result.status == ConversionStatus.COMPLETED:
        try:
            output_path = os.path.join("./converted", output_filename)
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            enhanced_content = await api_service.enhance_markdown(content)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
        except Exception as e:
            logger.error(f"Markdown強化エラー: {e}")
    
    # バックグラウンドでアップロードファイルを削除
    background_tasks.add_task(os.remove, upload_path)
    
    return result

@router.post("/batch", response_model=BatchConversionResult)
async def batch_convert(
    files: List[UploadFile] = File(...),
    use_api_enhancement: bool = False,
    use_ai_mode: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    複数ファイルを一括変換
    
    Args:
        files: アップロードするファイルのリスト
        use_api_enhancement: OpenAI APIによる強化を使用するか
    
    Returns:
        BatchConversionResult: バッチ変換結果
    """
    upload_paths = []
    
    # すべてのファイルをアップロード
    for file in files:
        if not conversion_service.is_supported_format(file.filename):
            continue
        
        upload_path = os.path.join("./uploads", file.filename)
        try:
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            upload_paths.append(upload_path)
        except Exception as e:
            logger.error(f"ファイルアップロードエラー: {e}")
    
    # ファイルを一括変換
    results = await conversion_service.batch_convert(upload_paths, use_ai_mode=use_ai_mode)
    
    # API強化が有効な場合
    if use_api_enhancement:
        for result in results:
            if result.status == ConversionStatus.COMPLETED and result.output_file:
                try:
                    output_path = os.path.join("./converted", result.output_file)
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    enhanced_content = await api_service.enhance_markdown(content)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(enhanced_content)
                except Exception as e:
                    logger.error(f"Markdown強化エラー: {e}")
    
    # バックグラウンドでアップロードファイルを削除
    for path in upload_paths:
        background_tasks.add_task(os.remove, path)
    
    # 結果を集計
    successful = sum(1 for r in results if r.status == ConversionStatus.COMPLETED)
    failed = sum(1 for r in results if r.status == ConversionStatus.FAILED)
    
    return BatchConversionResult(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )

@router.get("/download/{filename}")
async def download_converted_file(filename: str):
    """
    変換済みファイルをダウンロード
    
    Args:
        filename: ダウンロードするファイル名
    
    Returns:
        FileResponse: ファイルレスポンス
    """
    file_path = os.path.join("./converted", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/markdown"
    )

@router.get("/supported-formats")
async def get_supported_formats():
    """サポートされているファイル形式を取得"""
    return {"formats": conversion_service.supported_formats}

@router.post("/cancel/{conversion_id}")
async def cancel_conversion(conversion_id: str):
    """
    変換をキャンセル
    
    Args:
        conversion_id: キャンセルする変換のID
        
    Returns:
        dict: キャンセル結果
    """
    success = cancel_manager.cancel_conversion(conversion_id)
    
    # WebSocketでキャンセル通知を送信
    if success:
        await manager.send_progress(
            conversion_id=conversion_id,
            progress=0,
            status="cancelled",
            current_step="変換がキャンセルされました",
            file_name=""
        )
    
    return {"success": success, "message": "変換がキャンセルされました" if success else "変換が見つかりません"}

@router.post("/convert-url", response_model=ConversionResult)
async def convert_url(request: URLConversionRequest):
    """
    URLを変換（YouTube URLなど）
    
    Args:
        request: URL変換リクエスト
    
    Returns:
        ConversionResult: 変換結果
    """
    # YouTube URL check
    if not (request.url.startswith('http://') or request.url.startswith('https://')):
        raise HTTPException(status_code=400, detail="有効なURLを指定してください")
    
    # Convert URL to markdown
    output_filename = f"url_conversion_{os.urandom(8).hex()}.md"
    result = await conversion_service.convert_file(request.url, output_filename)
    
    # API enhancement if enabled
    if request.use_api_enhancement and result.status == ConversionStatus.COMPLETED:
        try:
            output_path = os.path.join("./converted", output_filename)
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            enhanced_content = await api_service.enhance_markdown(content)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            result.markdown_content = enhanced_content
        except Exception as e:
            logger.error(f"Markdown enhancement error: {e}")
    
    return result

@router.post("/upload-enhanced", response_model=ConversionResult)
async def upload_and_convert_enhanced(
    file: UploadFile = File(...),
    use_ai_mode: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Enhanced file upload and conversion with AI mode support
    
    Args:
        file: File to upload
        use_ai_mode: Enable AI-enhanced conversion mode
    
    Returns:
        ConversionResult: Conversion result
    """
    # Check file format
    file_ext = os.path.splitext(file.filename)[1].lower()[1:]
    supported_formats = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 
                        'mp3', 'wav', 'ogg', 'm4a', 'flac', 'csv', 'json', 'xml', 'txt', 'zip']
    
    if file_ext not in supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
        )
    
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB")
    
    # Save uploaded file
    upload_path = os.path.join("./uploads", file.filename)
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")
    
    # Convert file with enhanced service
    output_filename = f"{os.path.splitext(file.filename)[0]}.md"
    result = await enhanced_service.convert_file_enhanced(
        upload_path, 
        output_filename,
        use_ai_mode=use_ai_mode
    )
    
    # Clean up uploaded file in background
    background_tasks.add_task(os.remove, upload_path)
    
    return result

@router.post("/convert-youtube-enhanced", response_model=ConversionResult)
async def convert_youtube_enhanced(
    url: str,
    use_ai_mode: bool = False
):
    """
    Convert YouTube URL with optional AI enhancement
    
    Args:
        url: YouTube URL to convert
        use_ai_mode: Enable AI-enhanced description
    
    Returns:
        ConversionResult: Conversion result
    """
    # Validate YouTube URL
    if not enhanced_service.is_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    output_filename = f"youtube_{enhanced_service.extract_youtube_id(url)}.md"
    result = await enhanced_service.convert_file_enhanced(
        "",
        output_filename,
        is_url=True,
        url_content=url,
        use_ai_mode=use_ai_mode
    )
    
    # Add AI-enhanced metadata if enabled
    if use_ai_mode and result.status == ConversionStatus.COMPLETED:
        try:
            # Enhance with AI analysis
            enhanced_content = enhanced_service.llm_client.enhance_document_content(
                result.markdown_content,
                "youtube_video",
                []
            )
            result.markdown_content = enhanced_content
            
            # Save enhanced version
            output_path = os.path.join("./converted", output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
        except Exception as e:
            logger.error(f"AI enhancement error: {e}")
    
    return result