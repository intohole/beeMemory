#!/usr/bin/env python3
"""
创建测试数据脚本，用于初始化应用配置和用户数据
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import engine
from app.models.memory import UserMemory, AppConfig, ChatHistory


def create_test_data():
    """创建测试数据"""
    print("开始创建测试数据...")
    
    # 创建数据库会话
    with Session(engine) as db:
        # 创建测试应用配置
        print("1. 创建测试应用配置...")
        app_config = AppConfig(
            app_name="test_app",
            extraction_template="Extract key elements from the following conversation. Focus on important facts, preferences, and any other information that should be remembered.",
            extraction_fields={
                "user_intent": "用户的主要意图",
                "key_points": "关键点列表",
                "entities": "实体列表"
            },
            conversation_rounds=3,
            max_summary_length=500,
            similarity_threshold=0.8,
            enable_auto_summarize=True,
            enable_element_extraction=True,
            priority_weights={
                "content_length": 0.3,
                "element_count": 0.4,
                "access_frequency": 0.3
            },
            merge_strategy="similarity",
            merge_threshold=0.8,
            merge_window_minutes=60,
            expiry_strategy="last_access",
            expiry_days=30,
            memory_limit=1000,
            enable_semantic_scoring=False,
            access_score_weight=0.5,
            priority_score_weight=0.3,
            recency_score_weight=0.2
        )
        
        # 检查是否已存在
        existing_config = db.query(AppConfig).filter(AppConfig.app_name == "test_app").first()
        if existing_config:
            print("✅ 测试应用配置已存在，跳过创建")
        else:
            db.add(app_config)
            db.commit()
            print("✅ 测试应用配置创建成功")
        
        # 创建测试用户记忆
        print("2. 创建测试用户记忆...")
        
        # 检查是否已存在用户ID为1的记忆
        existing_memory = db.query(UserMemory).filter(UserMemory.user_id == "1").first()
        if existing_memory:
            print("✅ 测试用户记忆已存在，跳过创建")
        else:
            # 创建两条测试记忆
            test_memories = [
                UserMemory(
                    user_id="1",
                    app_name="test_app",
                    memory_content="用户是张三，今年28岁，是一名软件工程师，喜欢编程和旅游。",
                    extracted_elements={
                        "user_intent": "介绍个人信息",
                        "key_points": ["28岁", "软件工程师", "喜欢编程和旅游"],
                        "entities": ["张三"]
                    },
                    memory_priority=4,
                    memory_tags=["个人信息", "编程", "旅游"],
                    last_accessed_at=datetime.now(),
                    is_active=True,
                    is_archived=False
                ),
                UserMemory(
                    user_id="1",
                    app_name="test_app",
                    memory_content="用户计划明年3月去北京旅游，希望了解北京的景点和美食推荐。",
                    extracted_elements={
                        "user_intent": "咨询旅游信息",
                        "key_points": ["明年3月", "北京旅游", "景点推荐", "美食推荐"],
                        "entities": ["北京"]
                    },
                    memory_priority=5,
                    memory_tags=["旅游", "北京", "计划"],
                    last_accessed_at=datetime.now(),
                    is_active=True,
                    is_archived=False
                )
            ]
            
            for memory in test_memories:
                db.add(memory)
            
            db.commit()
            print("✅ 测试用户记忆创建成功")
        
        # 创建测试聊天历史
        print("3. 创建测试聊天历史...")
        
        # 检查是否已存在聊天历史
        existing_chat = db.query(ChatHistory).filter(ChatHistory.user_id == "1").first()
        if existing_chat:
            print("✅ 测试聊天历史已存在，跳过创建")
        else:
            # 创建两条测试聊天记录
            test_chats = [
                ChatHistory(
                    user_id="1",
                    app_name="test_app",
                    session_id="test_session_1",
                    role="user",
                    content="你好，我是张三，今年28岁，是一名软件工程师。",
                    timestamp=datetime.now() - timedelta(days=1)
                ),
                ChatHistory(
                    user_id="1",
                    app_name="test_app",
                    session_id="test_session_1",
                    role="assistant",
                    content="你好，张三！很高兴认识你。",
                    timestamp=datetime.now() - timedelta(days=1)
                ),
                ChatHistory(
                    user_id="1",
                    app_name="test_app",
                    session_id="test_session_1",
                    role="user",
                    content="我计划明年3月去北京旅游，希望了解北京的景点和美食推荐。",
                    timestamp=datetime.now() - timedelta(days=1)
                ),
                ChatHistory(
                    user_id="1",
                    app_name="test_app",
                    session_id="test_session_1",
                    role="assistant",
                    content="北京有很多值得游览的地方，比如故宫、长城、颐和园等。美食方面，北京烤鸭、炸酱面、豆汁儿都是当地特色。",
                    timestamp=datetime.now() - timedelta(days=1)
                )
            ]
            
            for chat in test_chats:
                db.add(chat)
            
            db.commit()
            print("✅ 测试聊天历史创建成功")
        
        print("\n🎉 测试数据创建完成！")
        print("\n测试信息：")
        print("- 用户ID: 1")
        print("- 应用名称: test_app")
        print("- 可访问的前端页面: http://localhost:8080")
        print("- API文档: http://localhost:8080/docs")


if __name__ == "__main__":
    create_test_data()
