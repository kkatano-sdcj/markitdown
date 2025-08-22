"""
ファイル変換サービス
markitdownライブラリを使用してファイルをMarkdown形式に変換
"""
import os
import time
import uuid
from typing import Optional, Dict, Any, List
from markitdown import MarkItDown
from models.data_models import ConversionResult, ConversionStatus, FileFormat
# Firebase機能（モック実装を使用）
from .mock_firebase_service import MockFirebaseService
from .enhanced_conversion_service import EnhancedConversionService
from .legacy_converter import LegacyConverter
from .markitdown_ai_service import MarkItDownAIService
import logging

logger = logging.getLogger(__name__)

class ConversionService:
    """ファイル変換を管理するサービスクラス"""
    
    def __init__(self):
        self.supported_formats = [f.value for f in FileFormat]
        self.upload_dir = "./uploads"
        self.output_dir = "./converted"
        self.md = MarkItDown()
        # Firebase機能（モック実装）
        self.firebase_service = MockFirebaseService()
        self.enable_database = True
        # Enhanced conversion service for additional formats
        self.enhanced_service = EnhancedConversionService()
        # Legacy converter for old binary formats
        self.legacy_converter = LegacyConverter()
        # MarkItDown AI service for LLM-integrated conversion
        self.markitdown_ai_service = MarkItDownAIService()
        
    def is_supported_format(self, filename: str) -> bool:
        """ファイル形式がサポートされているか確認"""
        ext = filename.split('.')[-1].lower()
        return ext in self.supported_formats
    
    def initialize_databases(self, firebase_config: Optional[Dict] = None, vector_db_path: str = "./chroma_db"):
        """データベースサービスを初期化（一時的に無効化）"""
        logger.info("Database services are temporarily disabled")
        self.enable_database = False
        # try:
        #     if firebase_config:
        #         self.firebase_service.initialize(credentials_dict=firebase_config)
        #     else:
        #         firebase_creds_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
        #         if firebase_creds_path:
        #             self.firebase_service.initialize(credentials_path=firebase_creds_path)
        #     
        #     self.vector_db_service.initialize(persist_directory=vector_db_path)
        #     self.enable_database = True
        #     logger.info("Database services initialized successfully")
        # except Exception as e:
        #     logger.error(f"Failed to initialize database services: {str(e)}")
        #     self.enable_database = False
    
    async def convert_file(self, input_path: str, output_filename: str, save_to_db: bool = True, metadata: Optional[Dict[str, Any]] = None, use_ai_mode: bool = False, progress_callback = None) -> ConversionResult:
        """
        単一ファイルの変換処理
        
        Args:
            input_path: 入力ファイルのパス
            output_filename: 出力ファイル名
            save_to_db: データベースに保存するかどうか
            metadata: ファイルのメタデータ
            
        Returns:
            ConversionResult: 変換結果
        """
        # Check if it's a URL (YouTube)
        if input_path.startswith('http://') or input_path.startswith('https://'):
            if self.enhanced_service.is_youtube_url(input_path):
                return await self.enhanced_service.convert_file_enhanced(
                    input_path="",
                    output_filename=output_filename,
                    is_url=True,
                    url_content=input_path
                )
        
        # Check file extension for special handling
        file_ext = os.path.splitext(input_path)[1].lower()[1:]
        
        # 画像ファイルは常にMarkItDownAIServiceで処理（OCRのため）
        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            return await self.markitdown_ai_service.convert_with_ai(
                file_path=input_path,
                output_filename=output_filename,
                use_ai_mode=use_ai_mode,
                progress_callback=progress_callback
            )
        
        # AI modeが有効な場合、MarkItDown AI Serviceを使用
        if use_ai_mode:
            return await self.markitdown_ai_service.convert_with_ai(
                file_path=input_path,
                output_filename=output_filename,
                use_ai_mode=True,
                progress_callback=progress_callback
            )
        
        # Special formats that need enhanced processing (without AI)
        if file_ext in ['zip', 'json', 'csv', 'mp3', 'wav', 'ogg', 'm4a', 'flac']:
            return await self.enhanced_service.convert_file_enhanced(
                input_path=input_path,
                output_filename=output_filename,
                use_ai_mode=False
            )
        
        # Original conversion logic for standard formats
        conversion_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Send initial progress
            if progress_callback:
                await progress_callback(conversion_id, 10, "processing", "ファイルを検証中...", os.path.basename(input_path))
            
            # 出力ファイルパスの生成
            output_path = os.path.join(self.output_dir, output_filename)
            
            if progress_callback:
                await progress_callback(conversion_id, 50, "processing", "変換中...", os.path.basename(input_path))
            
            # markitdownでファイルを変換
            result = self.md.convert(input_path)
            markdown_content = result.text_content
            
            if progress_callback:
                await progress_callback(conversion_id, 90, "processing", "保存中...", os.path.basename(input_path))
                
            # 変換結果をファイルに保存
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(markdown_content)
            
            # データベースに保存
            if save_to_db and self.enable_database:
                file_metadata = metadata or {}
                file_metadata.update({
                    'original_filename': os.path.basename(input_path),
                    'converted_filename': output_filename,
                    'file_size': os.path.getsize(input_path),
                    'conversion_time': time.time()
                })
                
                # Firebaseに保存
                self.firebase_service.save_markdown(
                    file_id=conversion_id,
                    content=markdown_content,
                    metadata=file_metadata
                )
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                await progress_callback(conversion_id, 100, "completed", "変換完了", os.path.basename(input_path))
            
            return ConversionResult(
                id=conversion_id,
                input_file=os.path.basename(input_path),
                output_file=output_filename,
                status=ConversionStatus.COMPLETED,
                processing_time=processing_time,
                markdown_content=markdown_content
            )
            
        except Exception as e:
            logger.error(f"ファイル変換エラー: {str(e)}")
            
            # Check if it's a legacy format that markitdown couldn't handle
            file_ext = os.path.splitext(input_path)[1].lower()[1:]
            if file_ext in ['ppt', 'doc', 'xls'] and "No converter attempted a conversion" in str(e):
                logger.info(f"Attempting legacy conversion for {file_ext} file")
                
                # Try legacy converter
                success, result_or_error = self.legacy_converter.convert(input_path)
                
                if success:
                    # Successfully converted to modern format, try again
                    try:
                        if progress_callback:
                            await progress_callback(conversion_id, 60, "processing", "レガシー形式を変換中...", os.path.basename(input_path))
                        
                        converted_path = result_or_error
                        result = self.md.convert(converted_path)
                        markdown_content = result.text_content
                        
                        # Save the converted markdown
                        output_path = os.path.join(self.output_dir, output_filename)
                        with open(output_path, 'w', encoding='utf-8') as output_file:
                            output_file.write(markdown_content)
                        
                        # Clean up temporary converted file
                        if os.path.exists(converted_path):
                            os.remove(converted_path)
                        
                        processing_time = time.time() - start_time
                        
                        if progress_callback:
                            await progress_callback(conversion_id, 100, "completed", "変換完了", os.path.basename(input_path))
                        
                        return ConversionResult(
                            id=conversion_id,
                            input_file=os.path.basename(input_path),
                            output_file=output_filename,
                            status=ConversionStatus.COMPLETED,
                            processing_time=processing_time,
                            markdown_content=markdown_content
                        )
                    except Exception as conv_error:
                        logger.error(f"Legacy conversion retry failed: {conv_error}")
                        error_msg = f"レガシー形式の変換に失敗しました: {str(conv_error)}"
                else:
                    # Provide helpful error message for legacy format
                    error_msg = result_or_error
            else:
                error_msg = f"変換エラー: {str(e)}"
            
            return ConversionResult(
                id=conversion_id,
                input_file=os.path.basename(input_path),
                status=ConversionStatus.FAILED,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
    
    async def batch_convert(self, file_paths: list[str], use_ai_mode: bool = False) -> list[ConversionResult]:
        """
        複数ファイルの一括変換
        
        Args:
            file_paths: 変換するファイルパスのリスト
            
        Returns:
            list[ConversionResult]: 各ファイルの変換結果
        """
        results = []
        
        for file_path in file_paths:
            # 出力ファイル名の生成（拡張子を.mdに変更）
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{base_name}.md"
            
            # ファイルを変換
            result = await self.convert_file(file_path, output_filename, use_ai_mode=use_ai_mode)
            results.append(result)
            
        return results
    
    async def search_similar_content(self, query: str, n_results: int = 5) -> list[Dict[str, Any]]:
        """
        類似コンテンツを検索
        
        Args:
            query: 検索クエリ
            n_results: 返す結果の数
            
        Returns:
            類似コンテンツのリスト
        """
        if not self.enable_database:
            logger.warning("Database services not enabled")
            return []
        
        # return self.vector_db_service.search_similar(query, n_results)
        return []
    
    async def get_stored_markdown(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        保存されたMarkdownファイルを取得
        
        Args:
            file_id: ファイルID
            
        Returns:
            Markdownファイルのデータ
        """
        if not self.enable_database:
            logger.warning("Database services not enabled")
            return None
        
        return self.firebase_service.get_markdown(file_id)
    
    async def list_stored_files(self, limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
        """
        保存されたファイルのリストを取得
        
        Args:
            limit: 取得する最大数
            offset: オフセット
            
        Returns:
            ファイルリスト
        """
        if not self.enable_database:
            logger.warning("Database services not enabled")
            return []
        
        return self.firebase_service.list_markdown_files(limit, offset)
    
    async def delete_stored_file(self, file_id: str) -> bool:
        """
        保存されたファイルを削除
        
        Args:
            file_id: ファイルID
            
        Returns:
            削除成功の可否
        """
        if not self.enable_database:
            logger.warning("Database services not enabled")
            return False
        
        firebase_result = self.firebase_service.delete_markdown(file_id)
        return firebase_result
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """古い一時ファイルを削除"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for directory in [self.upload_dir, self.output_dir]:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        try:
                            os.remove(file_path)
                            logger.info(f"古いファイルを削除: {file_path}")
                        except Exception as e:
                            logger.error(f"ファイル削除エラー: {e}")