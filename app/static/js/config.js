// 配置管理功能

// 初始化tooltip
function initTooltips() {
    // 初始化所有tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// 初始化配置模块
function initConfigModule() {
    // 初始化tooltip
    initTooltips();
    
    // 加载配置
    $('#loadAppConfig').on('click', loadAppConfig);
    
    // 加载所有应用配置
    $('#loadAllAppConfigs').on('click', loadAllAppConfigs);
    
    // 保存配置
    $('#appConfigForm').on('submit', function(e) {
        e.preventDefault();
        saveAppConfig();
    });
    
    // 配置列表标签页显示时自动加载配置列表
    $('#config-list-tab').on('shown.bs.tab', loadAllAppConfigs);
    
    // 添加提取字段
    $('#addExtractionField').on('click', addExtractionField);
    
    // 动态删除提取字段
    $('#extractionFieldsList').on('click', '.remove-field', function() {
        $(this).closest('.extraction-field-item').remove();
    });
}

// 提取字段HTML模板
const extractionFieldTemplate = `
    <div class="extraction-field-item mb-3 border p-3 rounded">
        <div class="row g-3">
            <div class="col-md-5">
                <label class="form-label">字段名</label>
                <input type="text" class="form-control field-name" placeholder="例如：user_intent" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">字段描述</label>
                <input type="text" class="form-control field-desc" placeholder="例如：用户的主要意图" required>
            </div>
            <div class="col-md-1 align-self-end">
                <button type="button" class="btn btn-danger btn-sm remove-field">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
        </div>
    </div>
`;

// 添加提取字段
function addExtractionField(fieldName = '', fieldDesc = '') {
    // 创建新的提取字段项
    const fieldItem = $(extractionFieldTemplate);
    
    // 如果提供了字段名和描述，填充内容
    if (fieldName && fieldDesc) {
        fieldItem.find('.field-name').val(fieldName);
        fieldItem.find('.field-desc').val(fieldDesc);
    }
    
    // 添加到列表
    $('#extractionFieldsList').append(fieldItem);
}

// 加载配置
function loadAppConfig() {
    // 获取表单数据
    const appName = $('#configAppName').val();
    
    // 验证数据
    if (!appName) {
        showError('请填写应用名称');
        return;
    }
    
    // 发送请求
    makeRequest(`/api/memory/app/config?app_name=${appName}`, 'GET', {}, function(response) {
        const config = response.data;
        
        // 填充表单
        $('#extractionTemplate').val(config.extraction_template);
        $('#conversationRounds').val(config.conversation_rounds);
        $('#maxSummaryLength').val(config.max_summary_length);
        $('#similarityThreshold').val(config.similarity_threshold);
        $('#enableAutoSummarize').prop('checked', config.enable_auto_summarize);
        $('#enableElementExtraction').prop('checked', config.enable_element_extraction);
        
        // 填充权重配置
        if (config.priority_weights) {
            $('#contentLengthWeight').val(config.priority_weights.content_length || 0.3);
            $('#elementCountWeight').val(config.priority_weights.element_count || 0.4);
            $('#accessFrequencyWeight').val(config.priority_weights.access_frequency || 0.3);
        }
        
        // 填充记忆合并配置
        $('#mergeStrategy').val(config.merge_strategy || 'similarity');
        $('#mergeThreshold').val(config.merge_threshold || 0.8);
        $('#mergeWindowMinutes').val(config.merge_window_minutes || 60);
        
        // 填充记忆清理配置
        $('#expiryStrategy').val(config.expiry_strategy || 'never');
        $('#expiryDays').val(config.expiry_days || 30);
        $('#memoryLimit').val(config.memory_limit || 1000);
        
        // 填充记忆评分配置
        $('#enableSemanticScoring').prop('checked', config.enable_semantic_scoring || false);
        $('#accessScoreWeight').val(config.access_score_weight || 0.5);
        $('#priorityScoreWeight').val(config.priority_score_weight || 0.3);
        $('#recencyScoreWeight').val(config.recency_score_weight || 0.2);
        
        // 填充提取字段列表
        fillExtractionFields(config.extraction_fields || {});
        
        showSuccess('配置加载成功');
    });
}

// 填充提取字段列表
function fillExtractionFields(extractionFields) {
    // 清空现有列表
    $('#extractionFieldsList').empty();
    
    // 如果没有提取字段，添加一个默认字段
    if (Object.keys(extractionFields).length === 0) {
        addExtractionField();
        return;
    }
    
    // 遍历提取字段，使用统一的添加函数
    for (const [fieldName, fieldDesc] of Object.entries(extractionFields)) {
        addExtractionField(fieldName, fieldDesc);
    }
}

// 加载所有应用配置
function loadAllAppConfigs() {
    // 发送请求获取所有应用配置
    makeRequest('/api/memory/app/config', 'GET', {}, function(response) {
        const appConfigs = response.data;
        
        // 填充应用配置列表
        fillAppConfigsList(appConfigs);
        showSuccess('应用配置列表加载成功');
    });
}

// 填充应用配置列表
function fillAppConfigsList(configs) {
    const tbody = $('#appConfigsTableBody');
    tbody.empty();
    
    if (configs.length === 0) {
        // 显示空数据提示
        const emptyRow = $('<tr></tr>');
        emptyRow.append($('<td></td>').attr('colspan', '6').addClass('text-center py-4 text-muted').html('<i class="fa fa-info-circle"></i> 暂无应用配置，请先创建'));
        tbody.append(emptyRow);
        return;
    }
    
    configs.forEach(config => {
        const row = $('<tr></tr>');
        
        // 应用名称
        row.append($('<td></td>').text(config.app_name));
        
        // 自动总结
        const autoSummarizeIcon = config.enable_auto_summarize ? 
            '<i class="fa fa-check text-success"></i>' : 
            '<i class="fa fa-times text-danger"></i>';
        row.append($('<td></td>').html(autoSummarizeIcon).addClass('text-center'));
        
        // 要素提取
        const elementExtractionIcon = config.enable_element_extraction ? 
            '<i class="fa fa-check text-success"></i>' : 
            '<i class="fa fa-times text-danger"></i>';
        row.append($('<td></td>').html(elementExtractionIcon).addClass('text-center'));
        
        // 相似度阈值
        row.append($('<td></td>').text(config.similarity_threshold).addClass('text-center'));
        
        // 对话更新轮数
        row.append($('<td></td>').text(config.conversation_rounds).addClass('text-center'));
        
        // 操作按钮
        const operations = $('<td></td>').addClass('text-center');
        const editBtn = $('<button></button>')
            .addClass('btn btn-sm btn-primary me-2')
            .html('<i class="fa fa-edit"></i> 编辑')
            .attr('title', '编辑该应用配置')
            .attr('data-bs-toggle', 'tooltip')
            .attr('data-bs-placement', 'top')
            .click(function() {
                // 选择应用配置，切换到编辑标签页并填充表单
                const tab = new bootstrap.Tab($('#config-edit-tab-tab'));
                tab.show();
                
                // 填充表单
                $('#configAppName').val(config.app_name);
                loadAppConfig();
            });
        
        operations.append(editBtn);
        row.append(operations);
        
        // 添加到表格
        tbody.append(row);
    });
    
    // 重新初始化tooltip
    initTooltips();
}

// 保存配置
function saveAppConfig() {
    // 获取表单数据
    const appName = $('#configAppName').val();
    const extractionTemplate = $('#extractionTemplate').val().trim();
    const conversationRounds = parseInt($('#conversationRounds').val());
    const maxSummaryLength = parseInt($('#maxSummaryLength').val());
    const similarityThreshold = parseFloat($('#similarityThreshold').val());
    const enableAutoSummarize = $('#enableAutoSummarize').is(':checked');
    const enableElementExtraction = $('#enableElementExtraction').is(':checked');
    
    // 获取权重配置
    const contentLengthWeight = parseFloat($('#contentLengthWeight').val());
    const elementCountWeight = parseFloat($('#elementCountWeight').val());
    const accessFrequencyWeight = parseFloat($('#accessFrequencyWeight').val());
    
    // 获取记忆合并配置
    const mergeStrategy = $('#mergeStrategy').val();
    const mergeThreshold = parseFloat($('#mergeThreshold').val());
    const mergeWindowMinutes = parseInt($('#mergeWindowMinutes').val());
    
    // 获取记忆清理配置
    const expiryStrategy = $('#expiryStrategy').val();
    const expiryDays = parseInt($('#expiryDays').val());
    const memoryLimit = parseInt($('#memoryLimit').val());
    
    // 获取记忆评分配置
    const enableSemanticScoring = $('#enableSemanticScoring').is(':checked');
    const accessScoreWeight = parseFloat($('#accessScoreWeight').val());
    const priorityScoreWeight = parseFloat($('#priorityScoreWeight').val());
    const recencyScoreWeight = parseFloat($('#recencyScoreWeight').val());
    
    // 验证数据
    if (!appName) {
        showError('请填写应用名称');
        return;
    }
    
    // 验证提取字段列表
    const fieldItems = $('.extraction-field-item');
    if (fieldItems.length === 0) {
        showError('请至少添加一个提取字段');
        return;
    }
    
    // 验证每个提取字段
    let hasEmptyField = false;
    fieldItems.each(function() {
        const fieldName = $(this).find('.field-name').val().trim();
        const fieldDesc = $(this).find('.field-desc').val().trim();
        
        if (!fieldName || !fieldDesc) {
            hasEmptyField = true;
            return false; // 退出循环
        }
    });
    
    if (hasEmptyField) {
        showError('所有提取字段的字段名和描述不能为空');
        return;
    }
    
    // 验证数字输入
    if (isNaN(conversationRounds) || conversationRounds < 1 || conversationRounds > 20) {
        showError('对话更新轮数必须是1-20之间的整数');
        return;
    }
    
    if (isNaN(maxSummaryLength) || maxSummaryLength < 100 || maxSummaryLength > 2000) {
        showError('最大总结长度必须是100-2000之间的整数');
        return;
    }
    
    if (isNaN(similarityThreshold) || similarityThreshold < 0 || similarityThreshold > 1) {
        showError('相似度阈值必须是0-1之间的数字');
        return;
    }
    
    // 验证合并配置
    if (isNaN(mergeThreshold) || mergeThreshold < 0 || mergeThreshold > 1) {
        showError('合并相似度阈值必须是0-1之间的数字');
        return;
    }
    
    if (isNaN(mergeWindowMinutes) || mergeWindowMinutes < 5 || mergeWindowMinutes > 1440) {
        showError('时间窗口必须是5-1440分钟之间的整数');
        return;
    }
    
    // 验证清理配置
    if (isNaN(expiryDays) || expiryDays < 1 || expiryDays > 365) {
        showError('过期天数必须是1-365之间的整数');
        return;
    }
    
    if (isNaN(memoryLimit) || memoryLimit < 100 || memoryLimit > 10000) {
        showError('记忆数量限制必须是100-10000之间的整数');
        return;
    }
    
    // 验证评分配置
    if (isNaN(accessScoreWeight) || accessScoreWeight < 0 || accessScoreWeight > 1) {
        showError('访问频率权重必须是0-1之间的数字');
        return;
    }
    
    if (isNaN(priorityScoreWeight) || priorityScoreWeight < 0 || priorityScoreWeight > 1) {
        showError('优先级权重必须是0-1之间的数字');
        return;
    }
    
    if (isNaN(recencyScoreWeight) || recencyScoreWeight < 0 || recencyScoreWeight > 1) {
        showError('时效性权重必须是0-1之间的数字');
        return;
    }
    
    // 验证权重
    if (isNaN(contentLengthWeight) || contentLengthWeight < 0 || contentLengthWeight > 1) {
        showError('内容长度权重必须是0-1之间的数字');
        return;
    }
    
    if (isNaN(elementCountWeight) || elementCountWeight < 0 || elementCountWeight > 1) {
        showError('要素数量权重必须是0-1之间的数字');
        return;
    }
    
    if (isNaN(accessFrequencyWeight) || accessFrequencyWeight < 0 || accessFrequencyWeight > 1) {
        showError('访问频率权重必须是0-1之间的数字');
        return;
    }
    
    // 权重之和建议为1.0，但不强制要求
    const totalWeight = contentLengthWeight + elementCountWeight + accessFrequencyWeight;
    if (Math.abs(totalWeight - 1.0) > 0.1) {
        // 只给出警告，不阻止提交
        showError(`权重之和为${totalWeight.toFixed(2)}，建议调整为1.0左右`);
    }
    
    // 收集提取字段
    const extractionFields = {};
    $('.extraction-field-item').each(function() {
        const fieldName = $(this).find('.field-name').val().trim();
        const fieldDesc = $(this).find('.field-desc').val().trim();
        
        if (fieldName && fieldDesc) {
            extractionFields[fieldName] = fieldDesc;
        }
    });
    
    // 构建请求数据
    const configData = {
        extraction_template: extractionTemplate,
        extraction_fields: extractionFields,
        conversation_rounds: conversationRounds,
        max_summary_length: maxSummaryLength,
        similarity_threshold: similarityThreshold,
        enable_auto_summarize: enableAutoSummarize,
        enable_element_extraction: enableElementExtraction,
        priority_weights: {
            content_length: contentLengthWeight,
            element_count: elementCountWeight,
            access_frequency: accessFrequencyWeight
        },
        // 记忆合并配置
        merge_strategy: mergeStrategy,
        merge_threshold: mergeThreshold,
        merge_window_minutes: mergeWindowMinutes,
        // 记忆清理配置
        expiry_strategy: expiryStrategy,
        expiry_days: expiryDays,
        memory_limit: memoryLimit,
        // 记忆评分配置
        enable_semantic_scoring: enableSemanticScoring,
        access_score_weight: accessScoreWeight,
        priority_score_weight: priorityScoreWeight,
        recency_score_weight: recencyScoreWeight
    };
    
    // 发送请求
    makeRequest(`/api/memory/app/config?app_name=${appName}`, 'PUT', configData, function(response) {
        showSuccess('配置保存成功');
        
        // 重新加载所有配置列表
        loadAllAppConfigs();
    });
}
