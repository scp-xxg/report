// 多智能体报告生成系统 - 改进版前端脚本
const API_BASE_URL = 'http://localhost:8080';

// 全局状态管理
const AppState = {
    currentStep: 1,
    maxStep: 4,
    currentSection: 'generate',
    isSidebarCollapsed: false,
    theme: 'light',
    reportConfig: {
        topic: '',
        angle: '',
        type: 'research',
        length: 'medium',
        formats: ['markdown'],
        enableCharts: true,
        enablePolish: true,
        model: 'demo-model',
        provider: 'demo'
    },
    providers: {
        demo: { name: '演示模式', models: ['demo-model'], enabled: true },
        openai: { name: 'OpenAI', models: [], enabled: false },
        vllm: { name: '本地vLLM', models: [], enabled: false }
    },
    isGenerating: false,
    generationProgress: 0,
    agents: {
        outline: { name: '大纲生成智能体', status: 'waiting', progress: 0 },
        content: { name: '内容生成智能体', status: 'waiting', progress: 0 },
        polish: { name: '润色智能体', status: 'waiting', progress: 0 },
        chart: { name: '图表生成智能体', status: 'waiting', progress: 0 }
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // 加载保存的设置
        loadSettings();
        
        // 检查系统状态
        await checkSystemHealth();
        
        // 加载AI提供商配置
        await loadProviders();
        
        // 设置事件监听器
        setupEventListeners();
        
        // 初始化界面
        updateUI();
        
        console.log('✅ 应用初始化完成');
    } catch (error) {
        console.error('❌ 应用初始化失败:', error);
        showNotification('应用初始化失败，请刷新页面重试', 'error');
    }
}

// 检查系统健康状态
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        
        if (data.status === 'ok') {
            updateSystemStatus('online', '服务正常');
            console.log('✅ 系统状态正常');
        } else {
            updateSystemStatus('offline', '服务异常');
        }
    } catch (error) {
        updateSystemStatus('offline', '连接失败');
        console.warn('⚠️ 无法连接到后端服务');
    }
}

// 更新系统状态显示
function updateSystemStatus(status, message) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = statusIndicator?.nextElementSibling;
    
    if (statusIndicator) {
        statusIndicator.className = `status-indicator ${status}`;
    }
    
    if (statusText) {
        statusText.textContent = message;
    }
    
    // 更新当前模式显示
    const currentModeEl = document.getElementById('currentMode');
    if (currentModeEl) {
        currentModeEl.textContent = AppState.providers[AppState.reportConfig.provider]?.name || '演示模式';
    }
}

// 加载AI提供商配置
async function loadProviders() {
    try {
        // 这里可以从后端API加载实际的提供商配置
        // 现在使用默认配置
        updateProviderSelector();
        updateModelSelector();
    } catch (error) {
        console.warn('加载提供商配置失败，使用默认配置');
    }
}

// 更新提供商选择器
function updateProviderSelector() {
    const providerSelect = document.getElementById('aiProvider');
    if (!providerSelect) return;
    
    providerSelect.innerHTML = '';
    
    Object.entries(AppState.providers).forEach(([key, provider]) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = provider.name;
        option.disabled = !provider.enabled;
        providerSelect.appendChild(option);
    });
    
    providerSelect.value = AppState.reportConfig.provider;
}

// 更新模型选择器
function updateModelSelector() {
    const modelSelect = document.getElementById('aiModel');
    if (!modelSelect) return;
    
    const provider = AppState.providers[AppState.reportConfig.provider];
    if (!provider) return;
    
    modelSelect.innerHTML = '';
    
    provider.models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    
    modelSelect.value = AppState.reportConfig.model;
}

// HTML中调用的函数 - 更新模型列表
function updateModels() {
    const providerSelect = document.getElementById('aiProvider');
    if (providerSelect) {
        AppState.reportConfig.provider = providerSelect.value;
        AppState.reportConfig.model = AppState.providers[AppState.reportConfig.provider]?.models[0] || 'demo-model';
        updateModelSelector();
        updateSystemStatus(AppState.providers[AppState.reportConfig.provider]?.enabled ? 'online' : 'offline', 
                          AppState.providers[AppState.reportConfig.provider]?.name || '服务异常');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 研究主题输入监听
    const topicInput = document.getElementById('research-topic');
    if (topicInput) {
        topicInput.addEventListener('input', function() {
            AppState.reportConfig.topic = this.value;
            updateCharCount(this);
            updateStepButton(1);
        });
    }
    
    // 自定义角度输入监听
    const angleInput = document.getElementById('custom-angle');
    if (angleInput) {
        angleInput.addEventListener('input', function() {
            AppState.reportConfig.angle = this.value;
        });
    }
    
    // 报告配置监听
    setupConfigListeners();
    
    // 文件上传监听
    setupFileUpload();
    
    // 主题切换
    setupThemeToggle();
    
    // 侧边栏切换
    setupSidebarToggle();
    
    // 键盘快捷键
    setupKeyboardShortcuts();
}

// 设置配置监听器
function setupConfigListeners() {
    const configElements = [
        { id: 'reportType', key: 'type' },
        { id: 'reportLength', key: 'length' },
        { id: 'aiModel', key: 'model' },
        { id: 'enableCharts', key: 'enableCharts' },
        { id: 'enablePolish', key: 'enablePolish' }
    ];
    
    configElements.forEach(({ id, key }) => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', function() {
                if (this.type === 'checkbox') {
                    AppState.reportConfig[key] = this.checked;
                } else {
                    AppState.reportConfig[key] = this.value;
                }
                updateConfigSummary();
            });
        }
    });
    
    // 格式选择监听
    const formatCheckboxes = document.querySelectorAll('input[name="formats"]');
    formatCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const formats = Array.from(formatCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            AppState.reportConfig.formats = formats.length > 0 ? formats : ['markdown'];
            updateConfigSummary();
        });
    });
}

// 设置文件上传
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.querySelector('.upload-area');
    const uploadedFiles = document.getElementById('uploadedFiles');
    
    if (!fileInput || !uploadArea) return;
    
    // 点击上传
    fileInput.addEventListener('change', handleFileUpload);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        fileInput.files = e.dataTransfer.files;
        handleFileUpload();
    });
}

// 处理文件上传
async function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadedFiles = document.getElementById('uploadedFiles');
    
    if (!fileInput.files.length || !uploadedFiles) return;
    
    uploadedFiles.innerHTML = '';
    
    for (let file of fileInput.files) {
        // 验证文件大小和类型
        if (file.size > 16 * 1024 * 1024) {
            showNotification(`文件 ${file.name} 超过16MB限制`, 'error');
            continue;
        }
        
        const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            showNotification(`文件 ${file.name} 格式不支持`, 'error');
            continue;
        }
        
        // 显示文件信息
        const fileItem = document.createElement('div');
        fileItem.className = 'uploaded-file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file"></i>
                <span class="file-name">${file.name}</span>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            </div>
            <button class="file-remove" onclick="removeFile('${file.name}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        uploadedFiles.appendChild(fileItem);
        
        // 上传文件到后端
        try {
            await uploadFileToServer(file);
        } catch (error) {
            showNotification(`上传文件 ${file.name} 失败`, 'error');
        }
    }
}

// 上传文件到服务器
async function uploadFileToServer(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Upload failed');
    }
    
    const result = await response.json();
    showNotification(`文件 ${file.name} 上传成功`, 'success');
    return result;
}

// 设置主题切换
function setupThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

// 切换主题
function toggleTheme() {
    AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', AppState.theme);
    
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = AppState.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    saveSettings();
}

// 设置侧边栏切换
function setupSidebarToggle() {
    const toggleButtons = document.querySelectorAll('.sidebar-toggle, .mobile-menu-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', toggleSidebar);
    });
}

// 切换侧边栏
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    if (window.innerWidth <= 768) {
        // 移动端：显示/隐藏侧边栏
        sidebar.classList.toggle('show');
    } else {
        // 桌面端：收起/展开侧边栏
        sidebar.classList.toggle('collapsed');
        AppState.isSidebarCollapsed = sidebar.classList.contains('collapsed');
        saveSettings();
    }
}

// 设置键盘快捷键
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter: 下一步或生成报告
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (AppState.currentStep < AppState.maxStep) {
                nextStep(AppState.currentStep + 1);
            } else if (AppState.currentStep === AppState.maxStep && !AppState.isGenerating) {
                startGeneration();
            }
        }
        
        // Escape: 关闭弹窗
        if (e.key === 'Escape') {
            closeModal();
        }
        
        // Ctrl/Cmd + /: 切换侧边栏
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            toggleSidebar();
        }
    });
}

// 显示指定章节
function showSection(sectionName) {
    // 更新导航状态
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[onclick="showSection('${sectionName}')"]`).parentElement;
    activeNavItem.classList.add('active');
    
    // 更新内容区域
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionName + 'Section');
    if (targetSection) {
        targetSection.classList.add('active');
        AppState.currentSection = sectionName;
    }
    
    // 更新页面标题
    const titles = {
        generate: '新建报告',
        history: '历史记录',
        settings: '系统设置',
        templates: '报告模板',
        about: '关于系统'
    };
    
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        pageTitle.textContent = titles[sectionName] || '多智能体报告系统';
    }
    
    // 移动端自动关闭侧边栏
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        sidebar?.classList.remove('show');
    }
}

// 向导步骤控制
function nextStep(stepNumber) {
    if (stepNumber > AppState.maxStep) return;
    
    // 验证当前步骤
    if (!validateCurrentStep()) {
        return;
    }
    
    // 隐藏当前步骤
    document.querySelectorAll('.wizard-step').forEach(step => {
        step.classList.remove('active');
    });
    
    // 显示目标步骤
    const targetStep = document.getElementById(`step${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');
        AppState.currentStep = stepNumber;
    }
    
    // 更新进度指示器
    updateProgressIndicator();
    
    // 特殊处理
    if (stepNumber === 2) {
        generateAngleSuggestions();
    } else if (stepNumber === 4) {
        updateConfigSummary();
    }
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevStep(stepNumber) {
    if (stepNumber < 1) return;
    nextStep(stepNumber);
}

// 验证当前步骤
function validateCurrentStep() {
    switch (AppState.currentStep) {
        case 1:
            if (!AppState.reportConfig.topic.trim()) {
                showNotification('请输入研究主题', 'warning');
                return false;
            }
            if (AppState.reportConfig.topic.length < 10) {
                showNotification('研究主题至少需要10个字符', 'warning');
                return false;
            }
            return true;
            
        case 2:
            // 步骤2可选，总是通过
            return true;
            
        case 3:
            if (AppState.reportConfig.formats.length === 0) {
                showNotification('请至少选择一种输出格式', 'warning');
                return false;
            }
            return true;
            
        default:
            return true;
    }
}

// 更新进度指示器
function updateProgressIndicator() {
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
        const stepNum = index + 1;
        indicator.classList.remove('active', 'completed');
        
        if (stepNum === AppState.currentStep) {
            indicator.classList.add('active');
        } else if (stepNum < AppState.currentStep) {
            indicator.classList.add('completed');
        }
    });
}

// 更新步骤按钮状态
function updateStepButton(stepNumber) {
    const button = document.getElementById(`step${stepNumber}Next`);
    if (!button) return;
    
    switch (stepNumber) {
        case 1:
            const topic = AppState.reportConfig.topic.trim();
            button.disabled = topic.length < 10;
            break;
    }
}

// 更新字符计数
function updateCharCount(input) {
    const charCount = document.getElementById('charCount');
    if (charCount) {
        const count = input.value.length;
        charCount.textContent = count;
        
        if (count > 500) {
            charCount.style.color = 'var(--error-color)';
        } else if (count > 400) {
            charCount.style.color = 'var(--warning-color)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
    }
}

// 生成研究角度建议
function generateAngleSuggestions() {
    const angleSuggestions = document.getElementById('angleSuggestions');
    if (!angleSuggestions) return;
    
    const suggestions = [
        { title: '技术发展视角', desc: '关注技术创新、发展趋势和技术挑战' },
        { title: '商业应用视角', desc: '分析商业价值、市场机会和盈利模式' },
        { title: '社会影响视角', desc: '探讨对社会、文化和生活方式的影响' },
        { title: '政策法规视角', desc: '研究相关政策、法规和治理框架' },
        { title: '比较分析视角', desc: '横向比较不同方案、方法或案例' },
        { title: '未来展望视角', desc: '预测发展趋势和未来可能性' }
    ];
    
    angleSuggestions.innerHTML = `
        <h4>推荐的研究角度</h4>
        <div class="angle-grid">
            ${suggestions.map(suggestion => `
                <div class="angle-card" onclick="selectAngle('${suggestion.title}', '${suggestion.desc}')">
                    <h5>${suggestion.title}</h5>
                    <p>${suggestion.desc}</p>
                </div>
            `).join('')}
        </div>
    `;
}

// 选择研究角度
function selectAngle(title, desc) {
    // 更新选中状态
    document.querySelectorAll('.angle-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
    
    // 更新自定义角度输入框
    const customAngleInput = document.getElementById('custom-angle');
    if (customAngleInput) {
        customAngleInput.value = `${title}: ${desc}`;
        AppState.reportConfig.angle = customAngleInput.value;
    }
}

// 更新配置摘要
function updateConfigSummary() {
    const configSummary = document.getElementById('configSummary');
    if (!configSummary) return;
    
    const typeLabels = {
        research: '研究报告',
        analysis: '分析报告',
        technical: '技术文档',
        business: '商业计划'
    };
    
    const lengthLabels = {
        short: '简要版 (5-10页)',
        medium: '标准版 (15-25页)',
        long: '详细版 (30-50页)'
    };
    
    configSummary.innerHTML = `
        <h3><i class="fas fa-eye"></i> 配置概览</h3>
        <div class="summary-grid">
            <div class="summary-item">
                <span class="summary-label">研究主题</span>
                <span class="summary-value">${AppState.reportConfig.topic.substring(0, 50)}${AppState.reportConfig.topic.length > 50 ? '...' : ''}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">报告类型</span>
                <span class="summary-value">${typeLabels[AppState.reportConfig.type]}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">报告长度</span>
                <span class="summary-value">${lengthLabels[AppState.reportConfig.length]}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">输出格式</span>
                <span class="summary-value">${AppState.reportConfig.formats.join(', ').toUpperCase()}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">图表生成</span>
                <span class="summary-value">${AppState.reportConfig.enableCharts ? '启用' : '禁用'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">内容润色</span>
                <span class="summary-value">${AppState.reportConfig.enablePolish ? '启用' : '禁用'}</span>
            </div>
        </div>
    `;
}

// 开始生成报告
async function startGeneration() {
    if (AppState.isGenerating) return;
    
    AppState.isGenerating = true;
    AppState.generationProgress = 0;
    
    // 隐藏生成控制，显示进度
    const generationControl = document.getElementById('generationControl');
    const generationProgress = document.getElementById('generationProgress');
    const backBtn = document.getElementById('backBtn');
    
    if (generationControl) generationControl.style.display = 'none';
    if (generationProgress) generationProgress.style.display = 'block';
    if (backBtn) backBtn.style.display = 'none';
    
    try {
        // 重置智能体状态
        resetAgentStatus();
        
        // 开始生成过程
        await performGeneration();
        
    } catch (error) {
        console.error('生成报告失败:', error);
        showNotification('生成报告失败，请重试', 'error');
        
        // 恢复界面
        if (generationControl) generationControl.style.display = 'block';
        if (generationProgress) generationProgress.style.display = 'none';
        if (backBtn) backBtn.style.display = 'inline-flex';
        
        AppState.isGenerating = false;
    }
}

// 执行生成过程
async function performGeneration() {
    const agents = ['outline', 'content', 'polish', 'chart'];
    const agentNames = {
        outline: '大纲生成智能体',
        content: '内容生成智能体', 
        polish: '润色智能体',
        chart: '图表生成智能体'
    };
    
    // 准备请求数据
    const requestData = {
        topic: AppState.reportConfig.topic,
        reportType: AppState.reportConfig.type,
        reportLength: AppState.reportConfig.length,
        enableCharts: AppState.reportConfig.enableCharts,
        enablePolish: AppState.reportConfig.enablePolish,
        formats: AppState.reportConfig.formats
    };
    
    // 模拟渐进式进度更新
    let currentAgentIndex = 0;
    
    const progressInterval = setInterval(() => {
        if (currentAgentIndex < agents.length) {
            const currentAgent = agents[currentAgentIndex];
            updateAgentStatus(currentAgent, 'working');
            
            // 更新整体进度
            AppState.generationProgress = Math.min(((currentAgentIndex + 0.5) / agents.length) * 100, 95);
            updateOverallProgress();
            
            currentAgentIndex++;
        }
    }, 2000);
    
    try {
        // 发送生成请求
        const response = await fetch(`${API_BASE_URL}/api/generate-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // 清除进度定时器
        clearInterval(progressInterval);
        
        // 完成所有智能体状态
        agents.forEach(agent => {
            updateAgentStatus(agent, 'completed');
        });
        
        // 设置100%进度
        AppState.generationProgress = 100;
        updateOverallProgress();
        
        // 延迟显示结果
        setTimeout(() => {
            showGenerationResult(result);
        }, 1000);
        
    } catch (error) {
        clearInterval(progressInterval);
        throw error;
    }
}

// 重置智能体状态
function resetAgentStatus() {
    Object.keys(AppState.agents).forEach(agent => {
        updateAgentStatus(agent, 'waiting');
    });
}

// 更新智能体状态
function updateAgentStatus(agentKey, status) {
    AppState.agents[agentKey].status = status;
    
    const agentElement = document.getElementById(`${agentKey}Agent`);
    if (!agentElement) return;
    
    const statusElement = agentElement.querySelector('.agent-status');
    if (!statusElement) return;
    
    // 更新状态样式
    statusElement.className = `agent-status ${status}`;
    
    // 更新状态文本
    const statusTexts = {
        waiting: '等待中',
        working: '工作中...',
        completed: '已完成',
        error: '出错了'
    };
    
    statusElement.querySelector('span').textContent = statusTexts[status] || status;
}

// 更新整体进度
function updateOverallProgress() {
    const progressFill = document.getElementById('overallProgress');
    const progressPercent = document.getElementById('progressPercent');
    const progressTime = document.getElementById('progressTime');
    
    if (progressFill) {
        progressFill.style.width = `${AppState.generationProgress}%`;
    }
    
    if (progressPercent) {
        progressPercent.textContent = `${Math.round(AppState.generationProgress)}%`;
    }
    
    if (progressTime && AppState.generationProgress < 100) {
        const remainingTime = Math.max(1, Math.round((100 - AppState.generationProgress) * 0.3));
        progressTime.textContent = `预计剩余时间: ${remainingTime}秒`;
    } else if (progressTime) {
        progressTime.textContent = '生成完成！';
    }
}

// 显示生成结果
function showGenerationResult(result) {
    const generationProgress = document.getElementById('generationProgress');
    const generationResult = document.getElementById('generationResult');
    const newReportBtn = document.getElementById('newReportBtn');
    
    if (generationProgress) generationProgress.style.display = 'none';
    if (newReportBtn) newReportBtn.style.display = 'inline-flex';
    
    if (generationResult) {
        generationResult.style.display = 'block';
        generationResult.innerHTML = `
            <div class="result-header">
                <h3><i class="fas fa-check-circle"></i> 报告生成完成！</h3>
                <p>您的报告已经生成完成，请选择下载格式。</p>
            </div>
            <div class="result-content">
                <div class="result-stats">
                    <div class="stat-item">
                        <span class="stat-label">生成时间</span>
                        <span class="stat-value">${result.processing_time || 15.8}秒</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">报告主题</span>
                        <span class="stat-value">${result.topic || AppState.reportConfig.topic}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">生成模式</span>
                        <span class="stat-value">${result.mode === 'demo' ? '演示模式' : '正式模式'}</span>
                    </div>
                </div>
                <div class="download-section">
                    <h4>下载报告</h4>
                    <div class="download-grid">
                        ${generateDownloadButtons(result.output_files || {})}
                    </div>
                </div>
            </div>
        `;
    }
    
    AppState.isGenerating = false;
    showNotification('报告生成完成！', 'success');
}

// 生成下载按钮
function generateDownloadButtons(files) {
    const formatIcons = {
        markdown: 'fab fa-markdown',
        json: 'fas fa-code',
        docx: 'fas fa-file-word', 
        pdf: 'fas fa-file-pdf'
    };
    
    const formatNames = {
        markdown: 'Markdown',
        json: 'JSON',
        docx: 'Word文档',
        pdf: 'PDF文档'
    };
    
    return Object.entries(files).map(([format, url]) => `
        <a href="${url}" class="download-btn" download>
            <i class="${formatIcons[format] || 'fas fa-download'}"></i>
            <span>下载 ${formatNames[format] || format.toUpperCase()}</span>
        </a>
    `).join('');
}

// 重置向导
function resetWizard() {
    // 重置状态
    AppState.currentStep = 1;
    AppState.isGenerating = false;
    AppState.generationProgress = 0;
    AppState.reportConfig.topic = '';
    AppState.reportConfig.angle = '';
    
    // 重置界面
    document.getElementById('research-topic').value = '';
    document.getElementById('custom-angle').value = '';
    document.getElementById('uploadedFiles').innerHTML = '';
    
    // 显示第一步
    nextStep(1);
    
    // 隐藏结果
    const generationResult = document.getElementById('generationResult');
    const generationControl = document.getElementById('generationControl');
    const backBtn = document.getElementById('backBtn');
    const newReportBtn = document.getElementById('newReportBtn');
    
    if (generationResult) generationResult.style.display = 'none';
    if (generationControl) generationControl.style.display = 'block';
    if (backBtn) backBtn.style.display = 'inline-flex';
    if (newReportBtn) newReportBtn.style.display = 'none';
    
    showNotification('已重置，可以开始新的报告生成', 'info');
}

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeFile(filename) {
    // 移除文件显示
    const fileItems = document.querySelectorAll('.uploaded-file-item');
    fileItems.forEach(item => {
        if (item.querySelector('.file-name').textContent === filename) {
            item.remove();
        }
    });
    
    showNotification(`已移除文件 ${filename}`, 'info');
}

// 通知系统
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(notification);
    
    // 显示动画
    setTimeout(() => notification.classList.add('show'), 10);
    
    // 自动移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// 弹窗管理
function showModal(title, content) {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    
    if (modalTitle) modalTitle.textContent = title;
    if (modalContent) modalContent.innerHTML = content;
    if (modalOverlay) {
        modalOverlay.style.display = 'flex';
        setTimeout(() => modalOverlay.classList.add('active'), 10);
    }
}

function closeModal() {
    const modalOverlay = document.getElementById('modalOverlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        setTimeout(() => {
            modalOverlay.style.display = 'none';
        }, 300);
    }
}

// 配置AI提供商
function configureProvider(provider) {
    const configs = {
        openai: {
            title: '配置 OpenAI',
            content: `
                <div class="form-group">
                    <label for="openaiApiKey">API Key</label>
                    <input type="password" id="openaiApiKey" placeholder="sk-...">
                </div>
                <div class="form-group">
                    <label for="openaiBaseUrl">Base URL</label>
                    <input type="url" id="openaiBaseUrl" value="https://api.openai.com/v1">
                </div>
            `
        },
        vllm: {
            title: '配置 本地vLLM',
            content: `
                <div class="form-group">
                    <label for="vllmBaseUrl">服务地址</label>
                    <input type="url" id="vllmBaseUrl" value="http://localhost:8000" placeholder="http://localhost:8000">
                </div>
                <div class="form-group">
                    <label for="vllmModel">模型名称</label>
                    <input type="text" id="vllmModel" placeholder="模型名称">
                </div>
            `
        }
    };
    
    const config = configs[provider];
    if (config) {
        showModal(config.title, config.content);
    }
}

function saveProviderConfig() {
    // 这里应该保存提供商配置
    showNotification('配置已保存', 'success');
    closeModal();
}

// 历史记录管理
function refreshHistory() {
    showNotification('历史记录已刷新', 'info');
}

function clearHistory() {
    if (confirm('确定要清空所有历史记录吗？此操作不可撤销。')) {
        showNotification('历史记录已清空', 'info');
    }
}

function clearAllData() {
    if (confirm('确定要清除所有数据吗？包括历史记录、设置等。此操作不可撤销。')) {
        localStorage.clear();
        showNotification('所有数据已清除', 'info');
        setTimeout(() => location.reload(), 1000);
    }
}

// 设置管理
function loadSettings() {
    try {
        const saved = localStorage.getItem('report-system-settings');
        if (saved) {
            const settings = JSON.parse(saved);
            AppState.theme = settings.theme || 'light';
            AppState.isSidebarCollapsed = settings.sidebarCollapsed || false;
            
            // 应用设置
            document.documentElement.setAttribute('data-theme', AppState.theme);
            
            const sidebar = document.getElementById('sidebar');
            if (sidebar && AppState.isSidebarCollapsed) {
                sidebar.classList.add('collapsed');
            }
            
            const themeIcon = document.getElementById('themeIcon');
            if (themeIcon) {
                themeIcon.className = AppState.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
        }
    } catch (error) {
        console.warn('加载设置失败:', error);
    }
}

function saveSettings() {
    try {
        const settings = {
            theme: AppState.theme,
            sidebarCollapsed: AppState.isSidebarCollapsed
        };
        localStorage.setItem('report-system-settings', JSON.stringify(settings));
    } catch (error) {
        console.warn('保存设置失败:', error);
    }
}

function changeTheme() {
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        AppState.theme = themeSelect.value;
        if (AppState.theme === 'auto') {
            AppState.theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        document.documentElement.setAttribute('data-theme', AppState.theme);
        saveSettings();
    }
}

// 更新界面
function updateUI() {
    updateProgressIndicator();
    updateStepButton(1);
    updateConfigSummary();
}

// 监听系统主题变化
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (AppState.theme === 'auto') {
            AppState.theme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', AppState.theme);
        }
    });
}

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('全局错误:', e.error);
    showNotification('发生了一个错误，请刷新页面重试', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('未处理的Promise拒绝:', e.reason);
    showNotification('网络请求失败，请检查连接', 'error');
});

console.log('✅ 多智能体报告生成系统前端脚本加载完成');
