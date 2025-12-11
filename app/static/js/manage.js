// 记忆管理功能

// 初始化管理模块
function initManageModule() {
    // 加载记忆列表
    $('#loadMemories').on('click', function() {
        loadMemories();
    });
    
    // 删除记忆
    $(document).on('click', '.delete-memory', function() {
        const memoryId = $(this).data('memory-id');
        deleteMemory(memoryId);
    });
}

// 加载记忆列表
function loadMemories() {
    // 获取表单数据
    const userId = $('#manageUserId').val();
    const appName = $('#manageAppName').val();
    
    // 验证数据
    if (!userId || !appName) {
        showError('请填写用户ID和应用名称');
        return;
    }
    
    // 发送请求
    makeRequest(`/api/memory/list?user_id=${userId}&app_name=${appName}`, 'GET', {}, function(response) {
        const memoriesList = $('#memoriesList');
        const memories = response.data.memories;
        
        if (memories && memories.length > 0) {
            let memoriesHtml = `
                <h5 class="mb-3">记忆列表</h5>
                <div class="memories-table-container">
                    <table class="table table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>记忆ID</th>
                                <th>内容</th>
                                <th>优先级</th>
                                <th>标签</th>
                                <th>最后访问时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            memories.forEach(function(memory) {
                // 格式化优先级
                let priorityText = '';
                if (memory.memory_priority === 5) priorityText = '<span class="badge bg-danger">最高</span>';
                else if (memory.memory_priority === 4) priorityText = '<span class="badge bg-warning">高</span>';
                else if (memory.memory_priority === 3) priorityText = '<span class="badge bg-info">中</span>';
                else if (memory.memory_priority === 2) priorityText = '<span class="badge bg-secondary">低</span>';
                else priorityText = '<span class="badge bg-light text-dark">最低</span>';
                
                // 格式化标签
                const tagsHtml = memory.memory_tags && memory.memory_tags.length > 0 ? 
                    memory.memory_tags.map(tag => `<span class="badge bg-primary me-1">${tag}</span>`).join('') : 
                    '<span class="text-muted">无</span>';
                
                memoriesHtml += `
                    <tr>
                        <td>${memory.memory_id}</td>
                        <td class="memory-content">${memory.memory_content.substring(0, 100)}${memory.memory_content.length > 100 ? '...' : ''}</td>
                        <td>${priorityText}</td>
                        <td>${tagsHtml}</td>
                        <td>${formatDateTime(memory.last_accessed_at)}</td>
                        <td>
                            <button type="button" class="btn btn-danger btn-sm delete-memory" data-memory-id="${memory.memory_id}">
                                <i class="fa fa-trash"></i> 删除
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            memoriesHtml += `
                        </tbody>
                    </table>
                </div>
            `;
            
            memoriesList.html(memoriesHtml);
        } else {
            memoriesList.html(`
                <div class="alert alert-warning">
                    <i class="fa fa-warning"></i>
                    未找到相关记忆
                </div>
                
                <h5 class="mt-4 mb-3">直接删除记忆</h5>
                <div class="input-group mb-3">
                    <input type="number" class="form-control" id="directMemoryId" placeholder="请输入记忆ID">
                    <button type="button" class="btn btn-danger" id="directDeleteBtn">
                        <i class="fa fa-trash"></i> 删除
                    </button>
                </div>
            `);
        }
        
        // 添加直接删除事件监听
        $('#directDeleteBtn').on('click', function() {
            const memoryId = $('#directMemoryId').val();
            if (memoryId) {
                deleteMemory(memoryId);
            } else {
                showError('请输入记忆ID');
            }
        });
    });
}

// 删除记忆
function deleteMemory(memoryId) {
    if (confirm(`确定要删除记忆ID为 ${memoryId} 的记忆吗？`)) {
        // 发送删除请求
        makeRequest(`/api/memory/${memoryId}`, 'DELETE', {}, function(response) {
            showSuccess('记忆删除成功');
            // 清空直接删除输入框
            $('#directMemoryId').val('');
        });
    }
}
