from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from app.core.config import settings


class ChromaClient:
    """Chroma客户端服务"""
    
    def __init__(self, 
                 host: Optional[str] = None, 
                 port: Optional[int] = None,
                 collection_name: Optional[str] = None):
        """初始化Chroma客户端
        
        Args:
            host: Chroma服务器地址
            port: Chroma服务器端口
            collection_name: 集合名称
        """
        self.host = host or settings.CHROMA_HOST
        self.port = port or settings.CHROMA_PORT
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        # 初始化Chroma客户端
        self.client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
    
    def add_embedding(self, 
                      embedding: List[float], 
                      document: str, 
                      memory_id: int,
                      user_id: str,
                      app_name: str) -> None:
        """添加单个Embedding向量
        
        Args:
            embedding: Embedding向量
            document: 文档内容
            memory_id: 记忆ID
            user_id: 用户ID
            app_name: 应用名称
        """
        self.collection.add(
            embeddings=[embedding],
            documents=[document],
            ids=[f"memory_{memory_id}"],
            metadatas=[{
                "memory_id": memory_id,
                "user_id": user_id,
                "app_name": app_name
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
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "user_id": user_id,
                "app_name": app_name
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
