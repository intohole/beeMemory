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
    const userId = $('#queryUserId').val().trim();
    const appName = $('#queryAppName').val().trim();
    const query = $('#queryContent').val().trim();
    const topK = parseInt($('#queryTopK').val());
    
    // 验证数据
    if (!userId) {
        showError('请填写用户ID');
        $('#queryUserId').focus();
        return;
    }
    
    if (!appName) {
        showError('请填写应用名称');
        $('#queryAppName').focus();
        return;
    }
    
    if (!query) {
        showError('请填写查询内容');
        $('#queryContent').focus();
        return;
    }
    
    if (query.length < 2) {
        showError('查询内容不能少于2个字符');
        $('#queryContent').focus();
        return;
    }
    
    if (isNaN(topK) || topK < 1 || topK > 20) {
        showError('返回数量必须是1-20之间的整数');
        $('#queryTopK').val(5);
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
            // Chroma返回的是距离，需要转换为相似度（相似度 = 1 - 距离）
            const distance = result.similarity;
            const similarity = 1 - distance;
            // 计算相似度百分比
            const similarityPercent = Math.round(similarity * 100);
            
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
                    <div class="result-content">${result.document || result.memory_content}</div>
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
