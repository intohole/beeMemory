// 记忆查询功能

// 初始化查询模块
function initQueryModule() {
    // 提交查询表单
    $('#queryForm').on('submit', function(e) {
        e.preventDefault();
        queryMemories();
    });
}

// 查询记忆
function queryMemories() {
    // 获取表单数据
    const userId = $('#queryUserId').val();
    const appName = $('#queryAppName').val();
    const query = $('#queryContent').val().trim();
    const topK = parseInt($('#queryTopK').val());
    
    // 验证数据
    if (!userId || !appName || !query) {
        showError('请填写所有必填字段');
        return;
    }
    
    // 构建请求数据
    const data = {
        user_id: userId,
        app_name: appName,
        query: query,
        top_k: topK
    };
    
    // 发送请求
    makeRequest('/api/memory/query', 'POST', data, function(response) {
        displayQueryResults(response.data.results);
    });
}

// 显示查询结果
function displayQueryResults(results) {
    const resultsContainer = $('#queryResults');
    
    if (results && results.length > 0) {
        let resultsHtml = '<h5 class="mb-3">查询结果</h5>';
        
        results.forEach(function(result) {
            // 计算相似度百分比
            const similarityPercent = Math.round(result.similarity * 100);
            
            resultsHtml += `
                <div class="result-item">
                    <div class="result-header">
                        <div>
                            <div class="result-title">记忆ID: ${result.memory_id}</div>
                        </div>
                        <div class="result-similarity">
                            相似度: ${similarityPercent}%
                        </div>
                    </div>
                    <div class="result-content">${result.memory_content}</div>
                    <div class="result-meta">
                        <span>创建时间: ${formatDateTime(result.created_at)}</span>
                        ${result.extracted_elements ? `<span>要素: ${JSON.stringify(result.extracted_elements)}</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        resultsContainer.html(resultsHtml);
    } else {
        resultsContainer.html('<div class="text-center text-muted py-4">未找到匹配的记忆</div>');
    }
}
