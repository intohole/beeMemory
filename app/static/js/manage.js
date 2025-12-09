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
    makeRequest(`/api/memory/config?user_id=${userId}&app_name=${appName}`, 'GET', {}, function(response) {
        // 这里我们需要获取记忆列表，但当前API没有直接提供获取所有记忆的接口
        // 我们可以添加一个新的API接口来支持这个功能
        // 目前暂时显示提示信息
        const memoriesList = $('#memoriesList');
        memoriesList.html(`
            <div class="alert alert-info">
                <i class="fa fa-info-circle"></i>
                当前API暂不支持获取所有记忆列表功能。
                <br>
                您可以通过查询功能来查找特定记忆，或直接输入记忆ID进行删除。
            </div>
            
            <h5 class="mt-4 mb-3">直接删除记忆</h5>
            <div class="input-group mb-3">
                <input type="number" class="form-control" id="directMemoryId" placeholder="请输入记忆ID">
                <button type="button" class="btn btn-danger" id="directDeleteBtn">
                    <i class="fa fa-trash"></i> 删除
                </button>
            </div>
        `);
        
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
