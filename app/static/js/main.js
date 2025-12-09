// 主逻辑文件

// 页面加载完成后执行
$(document).ready(function() {
    // 初始化所有模块
    initSubmitModule();
    initQueryModule();
    initManageModule();
    initConfigModule();
    
    // 添加页面切换事件监听
    $('.nav-link').on('click', function(e) {
        // 更新导航栏激活状态
        $('.nav-link').removeClass('active');
        $(this).addClass('active');
    });
});

// 通用AJAX请求函数
function makeRequest(url, method, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function() {
            // 显示加载状态
            showLoading();
        },
        success: function(response) {
            hideLoading();
            if (response.success) {
                if (successCallback) {
                    successCallback(response);
                }
            } else {
                if (errorCallback) {
                    errorCallback(response);
                } else {
                    showError(response.message || '操作失败');
                }
            }
        },
        error: function(xhr, status, error) {
            hideLoading();
            let errorMessage = '请求失败: ' + error;
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                errorMessage = xhr.responseJSON.detail;
            }
            if (errorCallback) {
                errorCallback({ success: false, message: errorMessage });
            } else {
                showError(errorMessage);
            }
        }
    });
}

// 显示加载状态
function showLoading() {
    // 移除已有的加载和消息元素
    hideLoading();
    hideMessages();
    
    // 创建加载元素
    const loadingHtml = `
        <div class="loading">
            <i class="fa fa-spinner fa-spin"></i> 处理中...
        </div>
    `;
    $('main').append(loadingHtml);
}

// 隐藏加载状态
function hideLoading() {
    $('.loading').remove();
}

// 显示错误消息
function showError(message) {
    hideMessages();
    const errorHtml = `
        <div class="error-message">
            <i class="fa fa-exclamation-circle"></i>
            <div>
                <strong>错误</strong>
                <p>${message}</p>
            </div>
        </div>
    `;
    $('main').prepend(errorHtml);
    // 3秒后自动隐藏
    setTimeout(hideMessages, 5000);
}

// 显示成功消息
function showSuccess(message) {
    hideMessages();
    const successHtml = `
        <div class="success-message">
            <i class="fa fa-check-circle"></i>
            <div>
                <strong>成功</strong>
                <p>${message}</p>
            </div>
        </div>
    `;
    $('main').prepend(successHtml);
    // 3秒后自动隐藏
    setTimeout(hideMessages, 5000);
}

// 隐藏所有消息
function hideMessages() {
    $('.error-message, .success-message').remove();
}

// 清空表单
function clearForm(formId) {
    $(formId)[0].reset();
}

// 格式化日期时间
function formatDateTime(dateString) {
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
