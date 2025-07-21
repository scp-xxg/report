// 统一状态管理器 - 解决双脚本冲突问题
console.log('🔧 加载统一状态管理器...');

// 全局状态管理器
window.UnifiedState = {
    // 配置状态
    config: {
        topic: '',
        angle: '',
        type: 'research',
        length: 'medium',
        formats: ['markdown'],
        enableCharts: true,
        enablePolish: true
    },
    
    // 系统状态
    system: {
        isGenerating: false,
        currentStep: 1,
        maxStep: 4,
        generationProgress: 0
    },
    
    // 智能体状态
    agents: {
        outline: { status: 'waiting', name: '大纲生成智能体' },
        content: { status: 'waiting', name: '内容生成智能体' },
        polish: { status: 'waiting', name: '润色智能体' },
        chart: { status: 'waiting', name: '图表生成智能体' }
    },
    
    // 更新配置
    updateConfig(updates) {
        Object.assign(this.config, updates);
        console.log('📝 配置已更新:', this.config);
        this.syncToLegacyStates();
    },
    
    // 同步到旧状态系统
    syncToLegacyStates() {
        // 同步到 AppState（如果存在）
        if (window.AppState) {
            window.AppState.reportConfig = { ...this.config };
            window.AppState.isGenerating = this.system.isGenerating;
        }
        
        // 同步到步骤导航器（如果存在）
        if (window.navigator && window.navigator.config) {
            window.navigator.config = { ...this.config };
        }
    },
    
    // 验证配置
    validateConfig() {
        const errors = [];
        
        if (!this.config.topic || this.config.topic.length < 10) {
            errors.push('研究主题至少需要10个字符');
        }
        
        if (this.config.formats.length === 0) {
            errors.push('至少需要选择一种输出格式');
        }
        
        return errors;
    },
    
    // 生成报告
    async generateReport() {
        if (this.system.isGenerating) {
            console.warn('⚠️ 报告正在生成中，请勿重复提交');
            return;
        }
        
        // 验证配置
        const errors = this.validateConfig();
        if (errors.length > 0) {
            alert('配置错误：\n' + errors.join('\n'));
            return;
        }
        
        this.system.isGenerating = true;
        this.syncToLegacyStates();
        
        try {
            console.log('🚀 开始生成报告...');
            this.showProgress();
            
            const requestData = {
                topic: this.config.topic,
                reportType: this.config.type,
                reportLength: this.config.length,
                enableCharts: this.config.enableCharts,
                enablePolish: this.config.enablePolish,
                formats: this.config.formats
            };
            
            console.log('📤 发送请求数据:', requestData);
            
            const response = await fetch(`${window.location.origin}/api/generate-report`, {
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
            console.log('📥 收到响应:', result);
            
            this.showResult(result);
            
        } catch (error) {
            console.error('❌ 报告生成失败:', error);
            alert('报告生成失败：' + error.message);
            this.hideProgress();
        } finally {
            this.system.isGenerating = false;
            this.syncToLegacyStates();
        }
    },
    
    // 显示进度
    showProgress() {
        const generationControl = document.getElementById('generationControl');
        const generationProgress = document.getElementById('generationProgress');
        
        if (generationControl) generationControl.style.display = 'none';
        if (generationProgress) generationProgress.style.display = 'block';
        
        // 模拟进度更新
        this.simulateProgress();
    },
    
    // 隐藏进度
    hideProgress() {
        const generationControl = document.getElementById('generationControl');
        const generationProgress = document.getElementById('generationProgress');
        
        if (generationControl) generationControl.style.display = 'block';
        if (generationProgress) generationProgress.style.display = 'none';
    },
    
    // 模拟进度
    simulateProgress() {
        const agents = ['outline', 'content', 'polish', 'chart'];
        let currentIndex = 0;
        
        const updateProgress = () => {
            if (currentIndex < agents.length && this.system.isGenerating) {
                const agent = agents[currentIndex];
                this.updateAgentStatus(agent, 'working');
                
                this.system.generationProgress = Math.min(((currentIndex + 0.5) / agents.length) * 100, 95);
                this.updateProgressBar();
                
                currentIndex++;
                setTimeout(updateProgress, 2000);
            }
        };
        
        updateProgress();
    },
    
    // 更新智能体状态
    updateAgentStatus(agentKey, status) {
        if (this.agents[agentKey]) {
            this.agents[agentKey].status = status;
            
            const agentElement = document.getElementById(`${agentKey}Agent`);
            if (agentElement) {
                const statusElement = agentElement.querySelector('.agent-status');
                if (statusElement) {
                    statusElement.textContent = this.getStatusText(status);
                    statusElement.className = `agent-status status-${status}`;
                }
            }
        }
    },
    
    // 获取状态文本
    getStatusText(status) {
        const statusMap = {
            waiting: '等待中',
            working: '工作中',
            completed: '已完成',
            error: '错误'
        };
        return statusMap[status] || status;
    },
    
    // 更新进度条
    updateProgressBar() {
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${this.system.generationProgress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(this.system.generationProgress)}%`;
        }
    },
    
    // 显示结果
    showResult(result) {
        console.log('📊 显示生成结果...');
        
        // 完成所有智能体
        Object.keys(this.agents).forEach(agent => {
            this.updateAgentStatus(agent, 'completed');
        });
        
        // 设置100%进度
        this.system.generationProgress = 100;
        this.updateProgressBar();
        
        // 显示结果界面
        setTimeout(() => {
            this.renderResult(result);
        }, 1000);
    },
    
    // 渲染结果
    renderResult(result) {
        const generationProgress = document.getElementById('generationProgress');
        const generationResult = document.getElementById('generationResult');
        const newReportBtn = document.getElementById('newReportBtn');
        
        if (generationProgress) generationProgress.style.display = 'none';
        if (newReportBtn) newReportBtn.style.display = 'inline-flex';
        
        if (generationResult) {
            generationResult.style.display = 'block';
            generationResult.innerHTML = this.generateResultHTML(result);
        }
        
        this.showNotification('报告生成完成！', 'success');
    },
    
    // 生成结果HTML
    generateResultHTML(result) {
        const downloadButtons = this.generateDownloadButtons(result.output_files || {});
        
        return `
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
                        <span class="stat-value">${result.topic || this.config.topic}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">生成模式</span>
                        <span class="stat-value">${result.mode === 'demo' ? '演示模式' : '正式模式'}</span>
                    </div>
                </div>
                <div class="download-section">
                    <h4>下载报告</h4>
                    <div class="download-grid">
                        ${downloadButtons}
                    </div>
                </div>
            </div>
        `;
    },
    
    // 生成下载按钮
    generateDownloadButtons(files) {
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
                <span>${formatNames[format] || format.toUpperCase()}</span>
            </a>
        `).join('');
    },
    
    // 显示通知
    showNotification(message, type = 'info') {
        const existing = document.getElementById('unified-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.id = 'unified-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            opacity: 0;
            transition: all 0.3s ease;
            max-width: 400px;
        `;
        
        notification.style.backgroundColor = type === 'success' ? '#28a745' : 
                                           type === 'error' ? '#dc3545' : 
                                           type === 'warning' ? '#ffc107' : '#007bff';
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => notification.style.opacity = '1', 100);
        
        // 自动隐藏
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
};

// 覆盖生成报告函数
window.generateReportUnified = function() {
    console.log('🎯 使用统一状态管理器生成报告');
    return window.UnifiedState.generateReport();
};

console.log('✅ 统一状态管理器已加载');
