#!/usr/bin/env python3
"""
快速开始脚本 - 一键运行报告生成示例
"""
import os
import sys
from datetime import datetime

def quick_start():
    """快速开始函数"""
    print("🚀 多智能体报告生成系统 - 快速开始")
    print("=" * 50)
    
    # 检查环境
    print("1️⃣ 检查运行环境...")
    try:
        from coordinator import ReportCoordinator
        print("   ✅ 模块导入成功")
    except ImportError as e:
        print(f"   ❌ 模块导入失败: {e}")
        print("   💡 请确保在正确的目录下运行此脚本")
        return False
    
    # 检查输出目录
    output_dir = "./quick_start_output"
    os.makedirs(output_dir, exist_ok=True)
    print(f"   ✅ 输出目录已创建: {output_dir}")
    
    # 初始化系统
    print("\n2️⃣ 初始化系统...")
    try:
        # 这里使用模拟模式，不需要真实的API密钥
        coordinator = ReportCoordinator(
            model_type="demo",  # 演示模式
            output_dir=output_dir
        )
        print("   ✅ 系统初始化成功")
    except Exception as e:
        print(f"   ❌ 系统初始化失败: {e}")
        return False
    
    # 生成演示报告
    print("\n3️⃣ 生成演示报告...")
    demo_topics = [
        "人工智能技术发展现状",
        "云计算在企业数字化转型中的作用",
        "区块链技术应用前景分析"
    ]
    
    print("   请选择一个主题：")
    for i, topic in enumerate(demo_topics, 1):
        print(f"   {i}. {topic}")
    
    try:
        choice = input("\n   请输入选择（1-3，默认1）: ").strip()
        if not choice:
            choice = "1"
        
        topic_index = int(choice) - 1
        if 0 <= topic_index < len(demo_topics):
            selected_topic = demo_topics[topic_index]
        else:
            selected_topic = demo_topics[0]
            
        print(f"   📝 已选择主题: {selected_topic}")
        
    except (ValueError, KeyboardInterrupt):
        selected_topic = demo_topics[0]
        print(f"   📝 使用默认主题: {selected_topic}")
    
    # 模拟报告生成过程
    print(f"\n4️⃣ 正在生成报告...")
    print("   ⏳ 这是一个演示过程，实际使用需要配置API密钥")
    
    # 创建演示输出
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    demo_content = generate_demo_report(selected_topic)
    
    # 保存演示文件
    demo_file = os.path.join(output_dir, f"demo_report_{timestamp}.md")
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    print(f"   ✅ 演示报告已生成: {demo_file}")
    
    # 显示后续步骤
    print("\n🎉 演示完成！")
    print("\n📚 接下来的步骤:")
    print("   1. 配置API密钥（编辑 .env 文件）")
    print("   2. 运行真实示例: python examples/demo.py")
    print("   3. 查看使用教程: cat USAGE_GUIDE.md")
    print("   4. 开始生成你的专业报告！")
    
    return True

def generate_demo_report(topic):
    """生成演示报告内容"""
    return f"""# {topic}

> 📝 这是一个演示报告，展示多智能体报告生成系统的输出格式
> 🕒 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 🤖 生成方式: 多智能体协作系统

## 目录

1. 概述与背景
2. 现状分析
3. 技术特点
4. 应用案例
5. 发展趋势
6. 挑战与机遇
7. 结论与建议

## 1. 概述与背景

{topic}是当前科技发展的重要方向之一。随着数字化转型的深入推进，相关技术正在各个领域发挥越来越重要的作用。

本报告通过多智能体协作生成，旨在全面分析该领域的发展现状、技术特点、应用前景以及面临的挑战。

## 2. 现状分析

当前，{topic}领域呈现出以下几个特点：

- **技术成熟度不断提升**：核心技术逐渐完善，应用场景不断扩大
- **市场需求持续增长**：企业和个人用户对相关解决方案的需求日益旺盛
- **生态系统日趋完善**：从基础设施到应用层面都有了长足发展
- **标准化程度提高**：行业标准和规范逐步建立和完善

## 3. 技术特点

{topic}具有以下核心技术特征：

### 3.1 创新性
采用先进的技术架构和算法模型，在效率和性能方面有显著提升。

### 3.2 可扩展性
支持大规模部署和应用，能够满足不同规模用户的需求。

### 3.3 安全性
内置多层安全机制，确保数据和系统的安全可靠。

## 4. 应用案例

在实际应用中，{topic}已经在多个领域取得了成功：

- **金融科技**：提升了交易效率和风险控制能力
- **智能制造**：优化了生产流程和质量管理
- **智慧城市**：改善了城市管理和公共服务
- **教育医疗**：提高了服务质量和覆盖范围

## 5. 发展趋势

未来，{topic}的发展将呈现以下趋势：

1. **技术融合加深**：与其他新兴技术的结合更加紧密
2. **应用领域扩展**：向更多垂直领域渗透
3. **标准化进程加速**：行业标准和规范进一步完善
4. **生态建设完善**：产业链上下游协同发展

## 6. 挑战与机遇

### 6.1 面临的挑战
- 技术复杂性不断增加
- 人才短缺问题突出
- 安全和隐私保护要求提高
- 监管政策有待完善

### 6.2 发展机遇
- 政策支持力度加大
- 市场需求快速增长
- 技术创新空间广阔
- 国际合作机会增多

## 7. 结论与建议

### 7.1 结论
{topic}作为重要的技术发展方向，具有广阔的应用前景和巨大的发展潜力。当前正处于快速发展的关键时期，需要各方共同努力推动其健康发展。

### 7.2 建议
1. **加大研发投入**：持续推进技术创新和突破
2. **完善人才培养**：建立完整的人才培养体系
3. **强化安全保障**：建立健全安全防护机制
4. **推进标准化**：积极参与标准制定和推广

---

## 附录：图表说明

📊 **注意**: 在实际使用中，系统会自动生成相关的数据图表，包括：
- 市场规模发展趋势图
- 技术成熟度对比图
- 应用领域分布饼图
- 发展阶段时间线图

---

*本报告由多智能体报告生成系统自动生成，仅供演示使用。*
*实际使用时，请配置真实的API密钥以获得更专业的内容。*
"""

if __name__ == "__main__":
    try:
        success = quick_start()
        if success:
            print(f"\n✨ 演示运行成功！请查看输出目录中的文件。")
        else:
            print(f"\n💔 演示运行失败，请检查环境配置。")
    except KeyboardInterrupt:
        print(f"\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print(f"💡 请确保在 /home/scp/report 目录下运行此脚本")
