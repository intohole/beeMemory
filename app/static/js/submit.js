// 聊天历史提交功能

// 初始化提交模块
function initSubmitModule() {
    // 动态添加消息
    $('#addMessage').on('click', function() {
        addMessageItem();
    });
    
    // 删除消息
    $(document).on('click', '.remove-message', function() {
        removeMessageItem($(this));
    });
    
    // 提交表单
    $('#submitForm').on('submit', function(e) {
        e.preventDefault();
        submitChatHistory();
    });
}

// 添加消息项
function addMessageItem() {
    const messageHtml = `
        <div class="message-item mb-3 border p-3 rounded">
            <div class="row g-2">
                <div class="col-md-2">
                    <select class="form-select" name="role">
                        <option value="user">用户</option>
                        <option value="assistant">助手</option>
                    </select>
                </div>
                <div class="col-md-9">
                    <textarea class="form-control" name="content" rows="2" placeholder="请输入消息内容" required></textarea>
                </div>
                <div class="col-md-1 align-self-end">
                    <button type="button" class="btn btn-danger btn-sm remove-message">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    $('#messagesList').append(messageHtml);
}

// 删除消息项
function removeMessageItem(button) {
    // 确保至少保留一条消息
    if ($('.message-item').length > 1) {
        button.closest('.message-item').remove();
    } else {
        showError('至少需要保留一条消息');
    }
}

// 提交聊天历史
function submitChatHistory() {
    // 获取表单数据
    const userId = $('#submitUserId').val().trim();
    const appName = $('#submitAppName').val().trim();
    
    // 获取消息列表
    const messages = [];
    let hasEmptyContent = false;
    
    $('.message-item').each(function() {
        const role = $(this).find('[name="role"]').val();
        const content = $(this).find('[name="content"]').val().trim();
        
        if (!content) {
            hasEmptyContent = true;
            return false; // 退出循环
        }
        
        messages.push({ role, content });
    });
    
    // 验证数据
    if (!userId) {
        showError('请填写用户ID');
        $('#submitUserId').focus();
        return;
    }
    
    if (!appName) {
        showError('请填写应用名称');
        $('#submitAppName').focus();
        return;
    }
    
    if (hasEmptyContent) {
        showError('所有消息内容不能为空');
        return;
    }
    
    if (messages.length === 0) {
        showError('请至少添加一条消息');
        return;
    }
    
    if (messages.length > 20) {
        showError('消息数量不能超过20条');
        return;
    }
    
    // 构建请求数据
    const data = {
        user_id: userId,
        app_name: appName,
        messages: messages
    };
    
    // 发送请求
    makeRequest('/api/memory/submit', 'POST', data, function(response) {
        showSuccess('聊天历史提交成功！记忆ID: ' + response.data.memory_id);
        // 重置表单
        clearSubmitForm();
    });
}

// 重置提交表单
function clearSubmitForm() {
    $('#submitUserId').val('');
    $('#submitAppName').val('');
    
    // 保留一条空消息
    $('#messagesList').html(`
        <div class="message-item mb-3 border p-3 rounded">
            <div class="row g-2">
                <div class="col-md-2">
                    <select class="form-select" name="role">
                        <option value="user">用户</option>
                        <option value="assistant">助手</option>
                    </select>
                </div>
                <div class="col-md-9">
                    <textarea class="form-control" name="content" rows="2" placeholder="请输入消息内容" required></textarea>
                </div>
                <div class="col-md-1 align-self-end">
                    <button type="button" class="btn btn-danger btn-sm remove-message">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `);
}
