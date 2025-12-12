// 主逻辑文件

// 初始化所有模块
$(document).ready(function() {
    // 初始化所有模块
    initSubmitModule();
    initQueryModule();
    initChatHistoryModule();
    initManageModule();
    initConfigModule();
    
    // 使用Bootstrap 5内置的标签页功能，无需手动实现
});

// 通用AJAX请求函数
function makeRequest(url, method, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        method: method,
        contentType: method === 'GET' ? 'application/x-www-form-urlencoded' : 'application/json',
        data: method === 'GET' ? data : JSON.stringify(data),
        beforeSend: function() {
            // 显示加载状态
            showLoading();
        },
        success: function(response) {
            hideLoading();
            // 统一处理API响应格式
            let apiResponse = response;
            
            // 如果响应没有success字段，将其包装成标准格式
            if (apiResponse.success === undefined) {
                apiResponse = {
                    success: true,
                    message: '操作成功',
                    data: response
                };
            }
            
            if (apiResponse.success) {
                if (successCallback) {
                    successCallback(apiResponse);
                } else {
                    showSuccess(apiResponse.message || '操作成功');
                }
            } else {
                if (errorCallback) {
                    errorCallback(apiResponse);
                } else {
                    showError(apiResponse.message || '操作失败');
                }
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            let errorMessage = '请求失败: ' + error;
            let errorDetails = '';
            
            // 提取详细错误信息
            if (xhr.responseJSON) {
                if (xhr.responseJSON.detail) {
                    errorMessage = xhr.responseJSON.detail;
                } else if (xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                } else if (typeof xhr.responseJSON === 'string') {
                    errorMessage = xhr.responseJSON;
                } else {
                    errorMessage = JSON.stringify(xhr.responseJSON);
                }
            } else if (xhr.responseText) {
                errorMessage = xhr.responseText;
            }
            
            // 显示完整错误信息
            const fullErrorMessage = `${errorMessage} (状态码: ${xhr.status})`;
            
            if (errorCallback) {
                errorCallback({ 
                    success: false, 
                    message: fullErrorMessage,
                    status: xhr.status,
                    error: error
                });
            } else {
                showError(fullErrorMessage);
            }
        }
    });
}

// 显示加载状态
function showLoading() {
    // 移除已有的加载和消息元素
    hideLoading();
    hideMessages();
    
    // 创建更美观的加载元素
    const loadingHtml = `
        <div class="loading-overlay">
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">处理中...</span>
                </div>
                <p class="mt-2">处理中...</p>
            </div>
        </div>
    `;
    $('body').append(loadingHtml);
}

// 隐藏加载状态
function hideLoading() {
    $('.loading-overlay').remove();
}

// 显示错误消息
function showError(message) {
    hideMessages();
    const errorHtml = `
        <div class="alert alert-danger alert-dismissible fade show shadow-lg" role="alert">
            <i class="fa fa-exclamation-circle me-2"></i>
            <strong>错误</strong>
            <p class="mb-0">${message}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $('.container').prepend(errorHtml);
    // 5秒后自动隐藏
    setTimeout(hideMessages, 5000);
}

// 显示成功消息
function showSuccess(message) {
    hideMessages();
    const successHtml = `
        <div class="alert alert-success alert-dismissible fade show shadow-lg" role="alert">
            <i class="fa fa-check-circle me-2"></i>
            <strong>成功</strong>
            <p class="mb-0">${message}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $('.container').prepend(successHtml);
    // 5秒后自动隐藏
    setTimeout(hideMessages, 5000);
}

// 显示警告消息
function showWarning(message) {
    hideMessages();
    const warningHtml = `
        <div class="alert alert-warning alert-dismissible fade show shadow-lg" role="alert">
            <i class="fa fa-warning me-2"></i>
            <strong>警告</strong>
            <p class="mb-0">${message}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $('.container').prepend(warningHtml);
    // 5秒后自动隐藏
    setTimeout(hideMessages, 5000);
}

// 隐藏所有消息
function hideMessages() {
    $('.alert').remove();
}

// 清空表单
function clearForm(formId) {
    $(formId)[0].reset();
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 初始化提交模块（由submit.js实现）
function initSubmitModule() {}

// 初始化查询模块（由query.js实现）
function initQueryModule() {}

// 初始化管理模块（由manage.js实现）
function initManageModule() {}

// 初始化配置模块（由config.js实现）
function initConfigModule() {}

// 初始化聊天历史模块（由chat_history.js实现）
function initChatHistoryModule() {}

// 添加防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 添加节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 显示确认对话框
function showConfirm(message, confirmCallback, cancelCallback) {
    const confirmHtml = `
        <div class="confirm-modal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.3s ease-out;">
            <div class="confirm-dialog" style="background: white; border-radius: 12px; padding: 2rem; max-width: 500px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.3); animation: slideUp 0.3s ease-out;">
                <div class="confirm-header" style="margin-bottom: 1.5rem;">
                    <h5 style="font-weight: 600; color: #333; margin: 0;"><i class="fa fa-question-circle" style="margin-right: 0.5rem; color: #667eea;"></i> 确认操作</h5>
                </div>
                <div class="confirm-body" style="margin-bottom: 2rem; color: #666;">
                    ${message}
                </div>
                <div class="confirm-footer" style="display: flex; justify-content: flex-end; gap: 0.75rem;">
                    <button class="btn btn-secondary" id="confirm-cancel" style="background: #6c757d; color: white;">取消</button>
                    <button class="btn btn-primary" id="confirm-ok">确认</button>
                </div>
            </div>
        </div>
    `;
    
    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    `;
    document.head.appendChild(style);
    
    // 添加确认对话框
    $('body').append(confirmHtml);
    
    // 绑定事件
    $('#confirm-ok').on('click', function() {
        $('.confirm-modal').remove();
        document.head.removeChild(style);
        if (confirmCallback) confirmCallback();
    });
    
    $('#confirm-cancel').on('click', function() {
        $('.confirm-modal').remove();
        document.head.removeChild(style);
        if (cancelCallback) cancelCallback();
    });
    
    // 点击背景关闭
    $('.confirm-modal').on('click', function(e) {
        if (e.target === this) {
            $('.confirm-modal').remove();
            document.head.removeChild(style);
            if (cancelCallback) cancelCallback();
        }
    });
    
    // ESC键关闭
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('.confirm-modal').remove();
            document.head.removeChild(style);
            if (cancelCallback) cancelCallback();
        }
    });
}

// 格式化数字，保留两位小数
function formatNumber(num, digits = 2) {
    return parseFloat(num).toFixed(digits);
}

// 生成唯一ID
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}
