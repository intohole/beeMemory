// 配置管理功能

// 初始化配置模块
function initConfigModule() {
    // 加载配置
    $('#loadConfig').on('click', function() {
        loadConfig();
    });
    
    // 保存配置
    $('#configForm').on('submit', function(e) {
        e.preventDefault();
        saveConfig();
    });
}

// 加载配置
function loadConfig() {
    // 获取表单数据
    const userId = $('#configUserId').val();
    const appName = $('#configAppName').val();
    
    // 验证数据
    if (!userId || !appName) {
        showError('请填写用户ID和应用名称');
        return;
    }
    
    // 发送请求
    makeRequest(`/api/memory/config?user_id=${userId}&app_name=${appName}`, 'GET', {}, function(response) {
        const config = response.data.config;
        
        // 填充表单
        $('#extractionPrompt').val(config.extraction_prompt);
        $('#mergeThreshold').val(config.merge_threshold);
        $('#expiryStrategy').val(config.expiry_strategy);
        $('#expiryDays').val(config.expiry_days);
        
        showSuccess('配置加载成功');
    });
}

// 保存配置
function saveConfig() {
    // 获取表单数据
    const userId = $('#configUserId').val();
    const appName = $('#configAppName').val();
    const extractionPrompt = $('#extractionPrompt').val().trim();
    const mergeThreshold = parseFloat($('#mergeThreshold').val());
    const expiryStrategy = $('#expiryStrategy').val();
    const expiryDays = parseInt($('#expiryDays').val());
    
    // 验证数据
    if (!userId || !appName) {
        showError('请填写用户ID和应用名称');
        return;
    }
    
    // 构建请求数据
    const config = {};
    if (extractionPrompt) {
        config.extraction_prompt = extractionPrompt;
    }
    if (!isNaN(mergeThreshold)) {
        config.merge_threshold = mergeThreshold;
    }
    config.expiry_strategy = expiryStrategy;
    if (!isNaN(expiryDays)) {
        config.expiry_days = expiryDays;
    }
    
    const data = {
        user_id: userId,
        app_name: appName,
        config: config
    };
    
    // 发送请求
    makeRequest(`/api/memory/config?user_id=${userId}&app_name=${appName}`, 'PUT', config, function(response) {
        showSuccess('配置保存成功');
    });
}
