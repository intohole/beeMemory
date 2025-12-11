from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from app.core.config import settings
from app.core.logging import get_logger
import os

logger = get_logger(__name__)


class ChromaClient:
    """Chroma客户端服务"""
    
    def __init__(self, 
                 collection_name: Optional[str] = None):
        """初始化Chroma客户端
        
        Args:
            collection_name: 集合名称
        """
        # 使用新的配置结构
        self.config = settings.chroma
        self.collection_name = collection_name or self.config.collection_name
        
        logger.info(f"Initializing ChromaClient...")
        logger.info(f"Collection name: {self.collection_name}")
        logger.info(f"Chroma config: {self.config.model_dump()}")
        
        if self.config.use_persistent_client:
            # 使用本地持久化客户端
            logger.info("Using Chroma PersistentClient (local storage)")
            logger.info("Note: When using PersistentClient, host and port settings are ignored")
            
            # 创建chroma数据目录
            chroma_data_path = self.config.persist_directory or os.path.join(os.getcwd(), "chroma_data")
            os.makedirs(chroma_data_path, exist_ok=True)
            
            # 初始化Chroma客户端（本地文件存储）
            self.client = chromadb.PersistentClient(
                path=chroma_data_path,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
        else:
            # 使用远程客户端
            logger.info(f"Using Chroma HttpClient (remote: {self.config.host}:{self.config.port})")
            logger.info("Note: When using HttpClient, persist_directory setting is ignored")
            
            # 初始化Chroma远程客户端
            self.client = chromadb.HttpClient(
                host=self.config.host,
                port=self.config.port,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
        
        # 获取或创建集合
        logger.info(f"Getting or creating collection: {self.collection_name}")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        logger.info(f"ChromaClient initialized successfully")
    
    def add_embedding(self, 
                      embedding: List[float], 
                      document: str, 
                      memory_id: int,
                      user_id: str,
                      app_name: str, 
                      similarity_threshold: float = 0.95) -> None:
        """添加单个Embedding向量，支持相似Embedding共享
        
        Args:
            embedding: Embedding向量
            document: 文档内容
            memory_id: 记忆ID
            user_id: 用户ID
            app_name: 应用名称
            similarity_threshold: 相似Embedding的阈值，超过此阈值则共享
        """
        # 先尝试查找相似的Embedding
        similar_results = self.collection.query(
            query_embeddings=[embedding],
            n_results=1,
            where={
                "$and": [
                    {"user_id": user_id},
                    {"app_name": app_name}
                ]
            }
        )
        
        # 检查是否有相似度超过阈值的Embedding
        try:
            if similar_results and similar_results["ids"] and len(similar_results["ids"]) > 0 and len(similar_results["ids"][0]) > 0:
                similar_id = similar_results["ids"][0][0]
                similarity = 1 - similar_results["distances"][0][0]  # 转换为相似度
                
                if similarity >= similarity_threshold:
                    # 找到了相似的Embedding，复用它
                    # 记录Embedding共享关系
                    logger.info(f"Sharing embedding {similar_id} for memory {memory_id} with similarity {similarity}")
                    # 这里可以添加一个共享关系的记录，例如存储到数据库
                    # 目前我们直接添加新的文档引用，共享相同的Embedding
                    self.collection.add(
                        embeddings=[embedding],  # 虽然共享，但为了简单，还是添加新的Embedding
                        documents=[document],
                        ids=[f"memory_{memory_id}"],
                        metadatas=[{
                            "memory_id": memory_id,
                            "user_id": user_id,
                            "app_name": app_name,
                            "shared_embedding": True,
                            "similarity": similarity,
                            "original_embedding_id": similar_id
                        }]
                    )
                    return
        except (IndexError, KeyError) as e:
            # 如果查询结果处理失败，跳过相似检查，直接添加新的Embedding
            logger.warning(f"Failed to check similar embeddings: {e}")
        
        # 如果没有找到相似的Embedding，添加新的
        self.collection.add(
            embeddings=[embedding],
            documents=[document],
            ids=[f"memory_{memory_id}"],
            metadatas=[{
                "memory_id": memory_id,
                "user_id": user_id,
                "app_name": app_name,
                "shared_embedding": False
            }]
        )
    
    def add_embeddings(self, 
                      embeddings: List[List[float]], 
                      documents: List[str], 
                      memory_ids: List[int],
                      user_ids: List[str],
                      app_names: List[str]) -> None:
        """添加多个Embedding向量
        
        Args:
            embeddings: Embedding向量列表
            documents: 文档内容列表
            memory_ids: 记忆ID列表
            user_ids: 用户ID列表
            app_names: 应用名称列表
        """
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=[f"memory_{memory_id}" for memory_id in memory_ids],
            metadatas=[{
                "memory_id": memory_id,
                "user_id": user_id,
                "app_name": app_name
            } for memory_id, user_id, app_name in zip(memory_ids, user_ids, app_names)]
        )
    
    def query_embeddings(self, 
                        query_embedding: List[float], 
                        user_id: str,
                        app_name: str,
                        top_k: int = 5) -> List[Dict[str, Any]]:
        """查询相似Embedding向量
        
        Args:
            query_embedding: 查询Embedding向量
            user_id: 用户ID
            app_name: 应用名称
            top_k: 返回结果数量
            
        Returns:
            查询结果列表，每个结果包含memory_id、similarity和document
        """
        # 使用$and操作符组合多个条件
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "$and": [
                    {"user_id": user_id},
                    {"app_name": app_name}
                ]
            }
        )
        
        # 处理查询结果
        processed_results = []
        for i in range(len(results["ids"][0])):
            result = {
                "memory_id": results["metadatas"][0][i]["memory_id"],
                "similarity": results["distances"][0][i],
                "document": results["documents"][0][i]
            }
            processed_results.append(result)
        
        return processed_results
    
    def update_embedding(self, 
                        memory_id: int,
                        embedding: Optional[List[float]] = None,
                        document: Optional[str] = None,
                        user_id: Optional[str] = None,
                        app_name: Optional[str] = None) -> None:
        """更新Embedding向量
        
        Args:
            memory_id: 记忆ID
            embedding: 新的Embedding向量
            document: 新的文档内容
            user_id: 新的用户ID
            app_name: 新的应用名称
        """
        metadata = None
        if user_id or app_name:
            metadata = {}
            if user_id:
                metadata["user_id"] = user_id
            if app_name:
                metadata["app_name"] = app_name
        
        self.collection.update(
            ids=[f"memory_{memory_id}"],
            embeddings=[embedding] if embedding else None,
            documents=[document] if document else None,
            metadatas=[metadata] if metadata else None
        )
    
    def delete_embedding(self, memory_id: int) -> None:
        """删除Embedding向量
        
        Args:
            memory_id: 记忆ID
        """
        self.collection.delete(
            ids=[f"memory_{memory_id}"]
        )
    
    def delete_embeddings_by_filter(self, user_id: Optional[str] = None, app_name: Optional[str] = None) -> None:
        """根据条件删除Embedding向量
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
        """
        where = {}
        if user_id:
            where["user_id"] = user_id
        if app_name:
            where["app_name"] = app_name
        
        if where:
            self.collection.delete(
                where=where
            )
    
    def reset(self) -> None:
        """重置Chroma客户端，删除所有数据"""
        self.client.reset()
        # 重新创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
