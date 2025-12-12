// 聊天历史查询模块

// 初始化聊天历史模块
function initChatHistoryModule() {
    // 绑定聊天历史查询表单提交事件
    $('#chatHistoryForm').on('submit', function(e) {
        e.preventDefault();
        queryChatHistory();
    });
}

// 查询聊天历史
function queryChatHistory() {
    // 获取表单数据
    const userId = $('#chatHistoryUserId').val().trim();
    const appName = $('#chatHistoryAppName').val().trim();
    const sessionId = $('#chatHistorySessionId').val().trim();
    
    // 构建查询参数
    const queryParams = {
        user_id: userId,
        app_name: appName
    };
    
    // 如果提供了session_id，添加到查询参数
    if (sessionId) {
        queryParams.session_id = sessionId;
    }
    
    // 发送查询请求
    makeRequest('/api/memory/chat/history', 'GET', queryParams, function(response) {
        displayChatHistoryResults(response.data.chat_history);
    }, function(error) {
        console.error('查询聊天历史失败:', error);
        showError('查询聊天历史失败: ' + error.message);
    });
}

// 显示聊天历史查询结果
function displayChatHistoryResults(chatHistory) {
    const resultsContainer = $('#chatHistoryResults');
    
    // 清空之前的结果
    resultsContainer.empty();
    
    // 如果没有结果
    if (!chatHistory || chatHistory.length === 0) {
        resultsContainer.html(`
            <div class="alert alert-info text-center p-5">
                <i class="fa fa-info-circle fa-3x mb-3"></i>
                <h5>未找到相关聊天历史</h5>
                <p class="mb-0">请检查您的查询条件，或尝试使用其他搜索参数。</p>
            </div>
        `);
        return;
    }
    
    // 按会话ID分组
    const groupedBySession = {};
    chatHistory.forEach(chat => {
        if (!groupedBySession[chat.session_id]) {
            groupedBySession[chat.session_id] = [];
        }
        groupedBySession[chat.session_id].push(chat);
    });
    
    // 生成结果HTML
    let resultsHtml = '';
    
    // 遍历每个会话
    Object.entries(groupedBySession).forEach(([sessionId, messages]) => {
        // 获取会话的第一条消息时间作为会话开始时间
        const sessionStartTime = messages[0].timestamp;
        
        resultsHtml += `
            <div class="card mb-4 shadow-sm">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h6 class="card-title mb-0">
                        <i class="fa fa-comments mr-2"></i> 会话 ID: ${sessionId}
                    </h6>
                    <span class="badge bg-light text-primary">${messages.length} 条消息</span>
                </div>
                <div class="card-body">
                    <div class="mb-3 text-muted">
                        <i class="fa fa-clock-o mr-1"></i> 开始时间: ${formatDateTime(sessionStartTime)}
                    </div>
                    <div class="chat-messages">
        `;
        
        // 遍历该会话的所有消息
        messages.forEach(message => {
            // 根据角色选择不同的样式
            const isUser = message.role === 'user';
            const messageClass = isUser ? 'user-message' : 'assistant-message';
            const roleClass = isUser ? 'user-role' : 'assistant-role';
            const roleName = isUser ? '用户' : '助手';
            
            resultsHtml += `
                        <div class="message ${messageClass} mb-3">
                            <div class="message-header d-flex justify-content-between mb-1">
                                <span class="role ${roleClass}">${roleName}</span>
                                <span class="timestamp text-muted small">${formatDateTime(message.timestamp)}</span>
                            </div>
                            <div class="message-content p-2 rounded">
                                ${escapeHtml(message.content)}
                            </div>
                        </div>
            `;
        });
        
        resultsHtml += `
                    </div>
                </div>
            </div>
        `;
    });
    
    // 将生成的HTML添加到结果容器
    resultsContainer.html(resultsHtml);
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
