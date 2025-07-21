"""
多智能体报告生成系统使用示例
演示如何使用系统生成报告
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coordinator import ReportCoordinator

def demo_basic_usage():
    """
    基本使用示例
    """
    print("=== 多智能体报告生成系统 - 基本使用示例 ===\n")
    
    # 初始化协调器
    # 注意：需要设置相应的API密钥或本地模型地址
    coordinator = ReportCoordinator(
        model_type="openai",  # 可以改为 "vllm" 使用本地模型
        model_name="gpt-3.5-turbo",  # 或本地模型名称
        # api_key="your-api-key",  # 如果使用OpenAI
        # base_url="http://localhost:8000",  # 如果使用本地vLLM
        output_dir="./demo_output"
    )
    
    # 生成报告
    topic = "人工智能在医疗领域的应用"
    
    print(f"正在生成报告：{topic}")
    print("这可能需要几分钟时间...\n")
    
    result = coordinator.generate_report(
        topic=topic,
        report_type="research",  # 研究报告类型
        enable_charts=True,      # 启用图表生成
        enable_polish=True,      # 启用内容润色
        output_formats=["markdown", "json"]  # 输出格式
    )
    
    # 输出结果
    if result["status"] == "success":
        print("✅ 报告生成成功！")
        print(f"📊 主题: {result['topic']}")
        print(f"⏱️  用时: {result['processing_time']:.2f} 秒")
        print(f"📁 输出文件:")
        for format_type, filepath in result["output_files"].items():
            print(f"   - {format_type}: {filepath}")
        
        # 显示报告概要
        data = result["data"]
        print(f"\n📋 报告概要:")
        print(f"   - 章节数: {len(data['outline'])}")
        print(f"   - 总字数: {sum(len(content) for content in data['sections'].values())}")
        print(f"   - 图表数: {len(data['charts'])}")
        
        print(f"\n📝 章节列表:")
        for i, section in enumerate(data['outline'], 1):
            print(f"   {i}. {section}")
    
    else:
        print("❌ 报告生成失败")
        print(f"错误信息: {result['error']}")

def demo_advanced_usage():
    """
    高级使用示例
    """
    print("\n=== 多智能体报告生成系统 - 高级使用示例 ===\n")
    
    # 使用本地vLLM模型的示例
    coordinator = ReportCoordinator(
        model_type="vllm",
        model_name="Qwen/Qwen3-4B",  # 或其他本地模型
        base_url="http://localhost:8000",
        output_dir="./advanced_output"
    )
    
    # 生成商业报告
    business_topic = "新能源汽车市场分析"
    
    print(f"正在生成商业报告：{business_topic}")
    
    result = coordinator.generate_report(
        topic=business_topic,
        report_type="business",     # 商业报告类型
        enable_charts=True,
        enable_polish=True,
        output_formats=["markdown", "docx", "json"]
    )
    
    # 查看系统状态
    status = coordinator.get_system_status()
    print(f"\n🔧 系统状态:")
    print(f"   工作流程状态: {status['workflow_status']}")
    print(f"   输出目录: {status['output_directory']}")

def demo_custom_workflow():
    """
    自定义工作流程示例
    """
    print("\n=== 自定义工作流程示例 ===\n")
    
    coordinator = ReportCoordinator(output_dir="./custom_output")
    
    # 只生成大纲（不生成完整内容）
    print("1. 生成技术报告大纲")
    
    # 这里展示如何单独使用各个智能体
    outline = coordinator.outline_agent.generate_outline(
        "区块链技术在供应链管理中的应用",
        "technical"
    )
    
    print("生成的大纲:")
    for i, section in enumerate(outline, 1):
        print(f"   {i}. {section}")
    
    # 只生成部分章节内容
    print("\n2. 生成部分章节内容")
    selected_sections = outline[:3]  # 只生成前3个章节
    
    sections_content = {}
    for section in selected_sections:
        content = coordinator.content_agent.generate_section_content(
            section, 
            "区块链技术在供应链管理中的应用"
        )
        sections_content[section] = content
        print(f"   ✅ 已生成: {section}")

def main():
    """
    主函数 - 运行所有示例
    """
    try:
        # 基本使用示例
        demo_basic_usage()
        
        # 高级使用示例（如果有本地模型）
        # demo_advanced_usage()
        
        # 自定义工作流程示例
        # demo_custom_workflow()
        
        print("\n🎉 所有示例运行完成！")
        print("\n💡 提示:")
        print("   - 请根据实际情况配置API密钥或本地模型地址")
        print("   - 生成的报告文件保存在相应的输出目录中")
        print("   - 可以根据需要修改报告主题和类型")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        print("\n🔧 故障排除:")
        print("   1. 检查API密钥是否正确配置")
        print("   2. 检查网络连接是否正常")
        print("   3. 检查本地模型服务是否启动")
        print("   4. 检查依赖包是否正确安装")

if __name__ == "__main__":
    main()
