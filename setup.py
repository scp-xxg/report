#!/usr/bin/env python3
"""
配置向导 - 帮助用户快速配置系统
"""
import os
import shutil

def setup_wizard():
    """配置向导主函数"""
    print("🔧 多智能体报告生成系统 - 配置向导")
    print("=" * 50)
    
    # 检查环境
    print("1️⃣ 环境检查...")
    check_environment()
    
    # 配置选择
    print("\n2️⃣ 选择配置模式...")
    config_mode = choose_config_mode()
    
    # 生成配置文件
    print("\n3️⃣ 生成配置文件...")
    generate_config(config_mode)
    
    # 完成提示
    print("\n🎉 配置完成！")
    show_next_steps()

def check_environment():
    """检查运行环境"""
    import sys
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"   ✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"   ⚠️  Python版本过低: {python_version.major}.{python_version.minor}")
        print("      建议使用Python 3.8或更高版本")
    
    # 检查依赖包
    required_packages = [
        "requests", "matplotlib", "pandas", "python-docx"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package} 已安装")
        except ImportError:
            print(f"   ❌ {package} 未安装")
            print(f"      请运行: pip install {package}")
    
    # 检查目录结构
    required_dirs = ["agents", "utils", "examples", "output"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ 目录存在: {dir_name}")
        else:
            print(f"   ⚠️  目录不存在: {dir_name}")

def choose_config_mode():
    """选择配置模式"""
    print("   请选择配置模式:")
    print("   1. OpenAI API模式（需要API密钥）")
    print("   2. 本地vLLM模式（需要本地模型服务）")
    print("   3. 演示模式（无需API，功能受限）")
    print("   4. 自定义配置")
    
    while True:
        try:
            choice = input("\n   请输入选择（1-4，默认3）: ").strip()
            if not choice:
                choice = "3"
            
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                return choice_num
            else:
                print("   ❌ 请输入1-4之间的数字")
        except ValueError:
            print("   ❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n   👋 用户取消配置")
            return 3

def generate_config(mode):
    """生成配置文件"""
    config_content = ""
    
    if mode == 1:  # OpenAI模式
        print("   📝 配置OpenAI API模式...")
        api_key = input("   请输入OpenAI API密钥: ").strip()
        
        config_content = f"""# OpenAI API 配置
OPENAI_API_KEY={api_key}
OPENAI_BASE_URL=https://api.openai.com/v1

# 系统配置
DEFAULT_OUTPUT_DIR=./output
DEFAULT_MODEL_TYPE=openai
DEFAULT_MODEL_NAME=gpt-3.5-turbo

# LangSmith 配置（可选）
# LANGSMITH_API_KEY=your_langsmith_api_key
# LANGSMITH_PROJECT=multi-agent-report-generator
# LANGSMITH_TRACING=true
"""
    
    elif mode == 2:  # vLLM模式
        print("   📝 配置本地vLLM模式...")
        base_url = input("   请输入vLLM服务地址（默认http://localhost:8000）: ").strip()
        if not base_url:
            base_url = "http://localhost:8000"
        
        model_name = input("   请输入模型名称（默认Qwen/Qwen3-4B）: ").strip()
        if not model_name:
            model_name = "Qwen/Qwen3-4B"
        
        config_content = f"""# 本地 vLLM 配置
VLLM_BASE_URL={base_url}

# 系统配置
DEFAULT_OUTPUT_DIR=./output
DEFAULT_MODEL_TYPE=vllm
DEFAULT_MODEL_NAME={model_name}

# OpenAI API 配置（备用）
# OPENAI_API_KEY=your_openai_api_key
# OPENAI_BASE_URL=https://api.openai.com/v1
"""
    
    elif mode == 3:  # 演示模式
        print("   📝 配置演示模式...")
        config_content = """# 演示模式配置
# 此模式不需要真实的API密钥，仅用于演示和测试

# 系统配置
DEFAULT_OUTPUT_DIR=./output
DEFAULT_MODEL_TYPE=demo
DEFAULT_MODEL_NAME=demo-model

# 如需使用真实API，请取消下面的注释并填入正确信息
# OPENAI_API_KEY=your_openai_api_key
# VLLM_BASE_URL=http://localhost:8000
"""
    
    else:  # 自定义模式
        print("   📝 自定义配置模式...")
        print("   请参考 .env.example 文件进行手动配置")
        config_content = """# 自定义配置
# 请根据你的实际情况填写配置信息

# OpenAI API 配置
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1

# 本地 vLLM 配置
# VLLM_BASE_URL=http://localhost:8000

# 系统配置
DEFAULT_OUTPUT_DIR=./output
DEFAULT_MODEL_TYPE=openai
DEFAULT_MODEL_NAME=gpt-3.5-turbo

# LangSmith 配置（可选）
# LANGSMITH_API_KEY=your_langsmith_api_key
# LANGSMITH_PROJECT=multi-agent-report-generator
# LANGSMITH_TRACING=true
"""
    
    # 保存配置文件
    env_file = ".env"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"   ✅ 配置文件已生成: {env_file}")
    
    # 设置文件权限（保护API密钥）
    try:
        os.chmod(env_file, 0o600)
        print("   🔒 已设置配置文件权限（仅当前用户可读写）")
    except:
        print("   ⚠️  无法设置文件权限，请手动保护配置文件")

def show_next_steps():
    """显示后续步骤"""
    print("\n📚 接下来你可以:")
    print("   1. 运行快速开始: python quick_start.py")
    print("   2. 运行完整示例: python examples/demo.py") 
    print("   3. 查看使用教程: cat USAGE_GUIDE.md")
    print("   4. 运行系统测试: python test.py")
    
    print("\n💡 使用技巧:")
    print("   - 如需修改配置，重新运行此脚本或直接编辑 .env 文件")
    print("   - 如遇问题，请查看 USAGE_GUIDE.md 中的故障排除部分")
    print("   - 建议先运行 quick_start.py 熟悉系统功能")

def create_directories():
    """创建必要的目录"""
    directories = [
        "output",
        "output/charts", 
        "logs",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ 目录已创建: {directory}")

if __name__ == "__main__":
    try:
        setup_wizard()
    except KeyboardInterrupt:
        print(f"\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        print(f"💡 请检查文件权限或手动配置 .env 文件")
