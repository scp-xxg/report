// 步骤导航完全重写 - 解决自定义研究角度无法进入下一步的问题
console.log('🔧 加载步骤导航完全重写脚本...');

// 完全重写的步骤导航系统
class StepNavigator {
    constructor() {
        this.currentStep = 1;
        this.maxStep = 4;
        this.config = {
            topic: '',
            angle: '',
            type: 'research',
            length: 'medium',
            formats: ['markdown'],
            enableCharts: true,
            enablePolish: true
        };
        this.isInitialized = false;
    }
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 初始化步骤导航系统...');
        
        // 重新绑定所有步骤按钮
        this.rebindStepButtons();
        
        // 设置输入框监听
        this.setupInputListeners();
        
        this.isInitialized = true;
        console.log('✅ 步骤导航系统初始化完成');
        
        this.showNotification('✅ 步骤导航系统已重新初始化', 'success');
    }
    
    rebindStepButtons() {
        // 重新绑定步骤1按钮
        const step1Next = document.getElementById('step1Next');
        if (step1Next) {
            this.replaceButton(step1Next, (e) => {
                e.preventDefault();
                const topic = document.getElementById('research-topic')?.value?.trim() || '';
                
                if (topic.length < 10) {
                    this.showNotification(`⚠️ 请输入至少10个字符的研究主题\n当前长度: ${topic.length}/10`, 'warning');
                    return;
                }
                
                this.config.topic = topic;
                this.goToStep(2);
            });
        }
        
        // 重新绑定步骤2按钮
        const step2Next = document.getElementById('step2Next');
        if (step2Next) {
            this.replaceButton(step2Next, (e) => {
                e.preventDefault();
                
                // 获取自定义研究角度
                const customAngle = document.getElementById('custom-angle')?.value?.trim() || '';
                this.config.angle = customAngle;
                
                console.log('📝 步骤2 - 自定义研究角度:', customAngle);
                
                // 直接跳转到步骤3，不做验证（因为角度是可选的）
                this.goToStep(3);
            });
        }
        
        // 重新绑定步骤3按钮
        const step3Next = document.getElementById('step3Next');
        if (step3Next) {
            this.replaceButton(step3Next, (e) => {
                e.preventDefault();
                
                // 收集配置信息
                this.collectConfig();
                
                // 验证必需的配置
                if (this.config.formats.length === 0) {
                    this.showNotification('⚠️ 请至少选择一种输出格式', 'warning');
                    return;
                }
                
                this.goToStep(4);
            });
        }
        
        // 重新绑定上一步按钮
        document.querySelectorAll('[onclick*="prevStep"]').forEach(btn => {
            const stepMatch = btn.getAttribute('onclick').match(/prevStep\\((\\d+)\\)/);
            if (stepMatch) {
                const targetStep = parseInt(stepMatch[1]);
                this.replaceButton(btn, (e) => {
                    e.preventDefault();
                    this.goToStep(targetStep);
                });
            }
        });
    }
    
    replaceButton(button, handler) {
        // 移除原有的onclick属性
        button.removeAttribute('onclick');
        
        // 克隆按钮以清除所有事件监听器
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // 绑定新的事件处理器
        newButton.addEventListener('click', handler);
        
        return newButton;
    }
    
    setupInputListeners() {
        // 主题输入监听
        const topicInput = document.getElementById('research-topic');
        if (topicInput) {
            topicInput.addEventListener('input', (e) => {
                this.config.topic = e.target.value.trim();
                this.updateStep1Button();
            });
        }
        
        // 自定义角度输入监听
        const angleInput = document.getElementById('custom-angle');
        if (angleInput) {
            angleInput.addEventListener('input', (e) => {
                this.config.angle = e.target.value.trim();
                console.log('📝 自定义角度更新:', this.config.angle);
            });
        }
    }
    
    updateStep1Button() {
        const button = document.getElementById('step1Next');
        const topic = this.config.topic;
        
        if (button) {
            if (topic.length >= 10) {
                button.disabled = false;
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
                button.innerHTML = '<i class="fas fa-arrow-right"></i> ✅ 下一步：设定研究角度';
            } else {
                button.disabled = true;
                button.style.opacity = '0.6';
                button.style.cursor = 'not-allowed';
                button.innerHTML = `<i class="fas fa-arrow-right"></i> ⏳ 下一步：设定研究角度 (${topic.length}/10)`;
            }
        }
    }
    
    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.maxStep) {
            console.warn('⚠️ 无效的步骤号:', stepNumber);
            return;
        }
        
        console.log(`🔄 跳转到步骤 ${stepNumber}`);
        
        try {
            // 隐藏所有步骤
            document.querySelectorAll('.wizard-step').forEach(step => {
                step.classList.remove('active');
                step.style.display = 'none';
            });
            
            // 显示目标步骤
            const targetStep = document.getElementById(`step${stepNumber}`);
            if (!targetStep) {
                throw new Error(`步骤${stepNumber}元素不存在`);
            }
            
            targetStep.classList.add('active');
            targetStep.style.display = 'block';
            
            // 更新当前步骤
            this.currentStep = stepNumber;
            
            // 更新进度指示器
            this.updateProgressIndicator();
            
            // 特殊处理
            if (stepNumber === 2) {
                this.generateAngleSuggestions();
            } else if (stepNumber === 4) {
                this.showConfigSummary();
            }
            
            // 滚动到顶部
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            console.log(`✅ 成功跳转到步骤 ${stepNumber}`);
            this.showNotification(`✅ 已进入步骤${stepNumber}`, 'success');
            
        } catch (error) {
            console.error('❌ 跳转失败:', error);
            this.showNotification('❌ 跳转失败: ' + error.message, 'error');
        }
    }
    
    updateProgressIndicator() {
        document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (stepNum === this.currentStep) {
                indicator.classList.add('active');
            } else if (stepNum < this.currentStep) {
                indicator.classList.add('completed');
            }
        });
    }
    
    generateAngleSuggestions() {
        const container = document.getElementById('angleSuggestions');
        if (!container || !this.config.topic) return;
        
        const suggestions = [
            { title: '技术创新角度', desc: '从技术发展和创新应用的角度分析' },
            { title: '市场应用角度', desc: '从商业价值和市场前景的角度探讨' },
            { title: '社会影响角度', desc: '从对社会和个人生活影响的角度研究' },
            { title: '发展趋势角度', desc: '从未来发展方向和趋势的角度预测' }
        ];
        
        container.innerHTML = suggestions.map(s => `
            <div class="angle-card" onclick="navigator.selectAngle('${s.title}', '${s.desc}')">
                <h5>${s.title}</h5>
                <p>${s.desc}</p>
            </div>
        `).join('');
    }
    
    selectAngle(title, desc) {
        // 更新选中状态
        document.querySelectorAll('.angle-card').forEach(card => {
            card.classList.remove('selected');
        });
        event.currentTarget.classList.add('selected');
        
        // 更新自定义角度输入框
        const customAngleInput = document.getElementById('custom-angle');
        if (customAngleInput) {
            const angleText = `${title}: ${desc}`;
            customAngleInput.value = angleText;
            this.config.angle = angleText;
        }
    }
    
    collectConfig() {
        // 收集配置信息
        const reportType = document.getElementById('reportType')?.value || 'research';
        const reportLength = document.getElementById('reportLength')?.value || 'medium';
        const enableCharts = document.getElementById('enableCharts')?.checked ?? true;
        const enablePolish = document.getElementById('enablePolish')?.checked ?? true;
        
        this.config.type = reportType;
        this.config.length = reportLength;
        this.config.enableCharts = enableCharts;
        this.config.enablePolish = enablePolish;
        
        // 收集输出格式
        const formatCheckboxes = document.querySelectorAll('input[name="formats"]:checked');
        this.config.formats = Array.from(formatCheckboxes).map(cb => cb.value);
        
        if (this.config.formats.length === 0) {
            this.config.formats = ['markdown'];
        }
    }
    
    showConfigSummary() {
        const summary = document.getElementById('configSummary');
        if (!summary) return;
        
        const typeLabels = {
            research: '研究报告',
            analysis: '分析报告', 
            technical: '技术文档',
            business: '商业计划'
        };
        
        summary.innerHTML = `
            <h3><i class="fas fa-eye"></i> 配置概览</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-label">研究主题</span>
                    <span class="summary-value">${this.config.topic.substring(0, 50)}${this.config.topic.length > 50 ? '...' : ''}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">研究角度</span>
                    <span class="summary-value">${this.config.angle || '未指定'}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">报告类型</span>
                    <span class="summary-value">${typeLabels[this.config.type]}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">输出格式</span>
                    <span class="summary-value">${this.config.formats.join(', ').toUpperCase()}</span>
                </div>
            </div>
        `;
    }
    
    showNotification(message, type = 'info') {
        const existing = document.getElementById('navigator-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.id = 'navigator-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 99999;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            font-size: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            opacity: 0;
            transition: all 0.3s ease;
            max-width: 80%;
            text-align: center;
            white-space: pre-line;
        `;
        
        notification.style.backgroundColor = type === 'success' ? '#28a745' : 
                                           type === 'error' ? '#dc3545' : 
                                           type === 'warning' ? '#ffc107' : '#007bff';
        
        if (type === 'warning') {
            notification.style.color = '#000';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.style.opacity = '1', 100);
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }
}

// 创建全局导航器实例
const navigator = new StepNavigator();

// 初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => navigator.init(), 500);
    });
} else {
    setTimeout(() => navigator.init(), 500);
}

// 暴露到全局作用域供调试使用
window.navigator = navigator;
window.testNavigation = function(step) {
    navigator.goToStep(step || 3);
};

console.log('✅ 步骤导航完全重写脚本已加载');
console.log('💡 使用 testNavigation(3) 测试跳转到步骤3');
