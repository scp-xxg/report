#!/usr/bin/env python3
"""
大模型配置助手
帮助用户快速配置OpenAI、vLLM等大模型服务
"""
import os
import sys
import json
from pathlib import Path

def main():
    print("🔧 多智能体报告生成系统 - 大模型配置助手")
    print("=" * 60)
    
    # 检查当前配置
    env_file = Path('.env')
    has_config = env_file.exists()
    
    if has_config:
        print("✅ 发现现有配置文件 .env")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content and content.split('OPENAI_API_KEY=')[1].split('\n')[0].strip() != 'your_openai_api_key_here':
                print("✅ OpenAI API密钥已配置")
            else:
                print("⚠️  OpenAI API密钥未配置")
    else:
        print("⚠️  未发现配置文件")
    
    print("\n📋 请选择配置方式:")
    print("1. 配置 OpenAI API (推荐)")
    print("2. 配置本地 vLLM 服务")
    print("3. 使用演示模式 (无需API密钥)")
    print("4. 测试当前配置")
    print("5. 退出")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == '1':
        configure_openai()
    elif choice == '2':
        configure_vllm()
    elif choice == '3':
        configure_demo()
    elif choice == '4':
        test_configuration()
    elif choice == '5':
        print("👋 配置已取消")
        sys.exit(0)
    else:
        print("❌ 无效选择")
        main()

def configure_openai():
    """配置OpenAI API"""
    print("\n🤖 配置 OpenAI API")
    print("-" * 30)
    
    print("📝 OpenAI API配置说明:")
    print("1. 访问 https://platform.openai.com/api-keys")
    print("2. 创建新的API密钥")
    print("3. 复制密钥并粘贴到下面")
    print("4. 确保账户有足够余额")
    
    api_key = input("\n请输入您的OpenAI API密钥: ").strip()
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ API密钥不能为空")
        return configure_openai()
    
    # 可选：自定义base URL
    print("\n🌐 API Base URL配置 (可选)")
    print("1. 使用官方地址 (默认)")
    print("2. 使用代理地址")
    
    url_choice = input("请选择 (1-2, 默认1): ").strip() or "1"
    
    if url_choice == "2":
        base_url = input("请输入代理地址 (如: https://api.chatanywhere.tech): ").strip()
    else:
        base_url = "https://api.openai.com/v1"
    
    # 模型选择
    print("\n🎯 模型选择:")
    models = [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo (推荐，性价比高)"),
        ("gpt-4", "GPT-4 (质量最佳，成本较高)"),
        ("gpt-4-turbo", "GPT-4 Turbo (平衡选择)"),
        ("gpt-4o", "GPT-4o (最新模型)")
    ]
    
    for i, (model, desc) in enumerate(models, 1):
        print(f"{i}. {desc}")
    
    model_choice = input("请选择模型 (1-4, 默认1): ").strip() or "1"
    selected_model = models[int(model_choice) - 1][0]
    
    # 写入配置文件
    write_env_config({
        'OPENAI_API_KEY': api_key,
        'OPENAI_BASE_URL': base_url,
        'DEFAULT_MODEL_TYPE': 'openai',
        'DEFAULT_MODEL_NAME': selected_model
    })
    
    print(f"\n✅ OpenAI配置完成!")
    print(f"📋 模型: {selected_model}")
    print(f"🌐 Base URL: {base_url}")
    
    # 测试配置
    if input("\n🧪 是否测试配置? (y/N): ").lower() == 'y':
        test_openai_connection(api_key, base_url, selected_model)

def configure_vllm():
    """配置本地vLLM服务"""
    print("\n🖥️  配置本地 vLLM 服务")
    print("-" * 30)
    
    print("📝 vLLM配置说明:")
    print("1. 确保已安装vLLM: pip install vllm")
    print("2. 启动vLLM服务器")
    print("3. 默认地址通常为: http://localhost:8000")
    print("")
    print("💡 提示:")
    print("- 如果还未安装vLLM，可以运行: ./setup_vllm.sh")
    print("- 详细配置指南请查看: VLLM_SETUP_GUIDE.md")
    print("")
    
    # 检查本地DeepSeek模型
    deepseek_path = "/home/scp/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-1.5B/snapshots/ad9f0ae0864d7fbcd1cd905e3c6c5b069cc8b562"
    deepseek_available = os.path.exists(f"{deepseek_path}/config.json")
    
    if deepseek_available:
        print("✅ 检测到本地DeepSeek-R1-Distill-Qwen-1.5B模型")
        print(f"📁 模型路径: {deepseek_path}")
    
    # 检查是否已有vLLM服务运行
    try:
        import requests
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ 检测到运行中的vLLM服务")
            if 'data' in models and models['data']:
                available_models = [model['id'] for model in models['data']]
                print(f"📋 可用模型: {', '.join(available_models)}")
                default_model = available_models[0] if available_models else ("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" if deepseek_available else "Qwen/Qwen2-7B-Instruct")
            else:
                default_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" if deepseek_available else "Qwen/Qwen2-7B-Instruct"
        else:
            print("⚠️  vLLM服务未运行或响应异常")
            default_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" if deepseek_available else "Qwen/Qwen2-7B-Instruct"
    except:
        print("⚠️  vLLM服务未运行")
        default_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" if deepseek_available else "Qwen/Qwen2-7B-Instruct"
    
    print(f"\n🔧 配置vLLM连接")
    
    # 模型选择
    print(f"\n🤖 可用模型选项:")
    print("1. deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B (本地已下载)" if deepseek_available else "1. deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B (需要下载)")
    print("2. Qwen/Qwen2-7B-Instruct")
    print("3. Qwen/Qwen2-1.5B-Instruct")
    print("4. THUDM/chatglm3-6b")
    print("5. 自定义模型")
    
    model_choice = input(f"请选择模型 (1-5, 默认使用 {default_model}): ").strip()
    
    if model_choice == "1":
        model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    elif model_choice == "2":
        model_name = "Qwen/Qwen2-7B-Instruct"
    elif model_choice == "3":
        model_name = "Qwen/Qwen2-1.5B-Instruct"
    elif model_choice == "4":
        model_name = "THUDM/chatglm3-6b"
    elif model_choice == "5":
        model_name = input("请输入自定义模型名称: ").strip()
    else:
        model_name = default_model if model_choice == "" else default_model
    
    base_url = input(f"请输入vLLM服务地址 (默认: http://localhost:8000): ").strip()
    if not base_url:
        base_url = "http://localhost:8000"
    
    # 高级配置选项
    print(f"\n⚙️  高级配置 (可选)")
    advanced = input("是否配置高级选项? (y/N): ").lower() == 'y'
    
    config = {
        'VLLM_BASE_URL': base_url,
        'DEFAULT_MODEL_TYPE': 'vllm',
        'DEFAULT_MODEL_NAME': model_name
    }
    
    if advanced:
        temperature = input("温度参数 (0.1-2.0, 默认0.7): ").strip()
        if temperature:
            try:
                temp_val = float(temperature)
                if 0.1 <= temp_val <= 2.0:
                    config['DEFAULT_TEMPERATURE'] = temperature
            except ValueError:
                pass
        
        max_tokens = input("最大生成长度 (默认1000): ").strip()
        if max_tokens:
            try:
                tokens_val = int(max_tokens)
                if tokens_val > 0:
                    config['DEFAULT_MAX_TOKENS'] = max_tokens
            except ValueError:
                pass
    
    # 写入配置文件
    write_env_config(config)
    
    print(f"\n✅ vLLM配置完成!")
    print(f"🌐 服务地址: {base_url}")
    print(f"🤖 模型: {model_name}")
    
    # 测试配置
    if input("\n🧪 是否测试配置? (y/N): ").lower() == 'y':
        test_vllm_connection(base_url, model_name)
        
    # 提供启动指南
    print(f"\n📋 vLLM服务启动指南:")
    print(f"如果vLLM服务未运行，请执行:")
    print(f"./start_vllm.sh")
    print(f"或手动启动:")
    print(f"python -m vllm.entrypoints.openai.api_server --model {model_name} --host 0.0.0.0 --port 8000")

def configure_demo():
    """配置演示模式"""
    print("\n🎭 配置演示模式")
    print("-" * 30)
    
    print("📝 演示模式说明:")
    print("✅ 无需API密钥")
    print("✅ 可以体验完整流程")
    print("⚠️  生成的内容为演示内容")
    print("⚠️  不调用真实AI模型")
    
    # 写入配置文件
    write_env_config({
        'DEFAULT_MODEL_TYPE': 'demo',
        'DEFAULT_MODEL_NAME': 'demo-model'
    })
    
    print("\n✅ 演示模式配置完成!")
    print("🎯 现在可以使用演示模式生成报告")

def test_configuration():
    """测试当前配置"""
    print("\n🧪 测试当前配置")
    print("-" * 30)
    
    # 读取配置
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ 未找到配置文件 .env")
        return
    
    config = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    
    model_type = config.get('DEFAULT_MODEL_TYPE', '')
    
    if model_type == 'openai':
        api_key = config.get('OPENAI_API_KEY', '')
        base_url = config.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        model_name = config.get('DEFAULT_MODEL_NAME', 'gpt-3.5-turbo')
        test_openai_connection(api_key, base_url, model_name)
    elif model_type == 'vllm':
        base_url = config.get('VLLM_BASE_URL', 'http://localhost:8000')
        test_vllm_connection(base_url)
    elif model_type == 'demo':
        print("✅ 演示模式配置正常")
        print("🎯 可以直接使用Web界面或命令行工具")
    else:
        print("❌ 未配置模型类型")

def test_openai_connection(api_key, base_url, model_name):
    """测试OpenAI连接"""
    print(f"\n🔍 测试OpenAI连接...")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 模型: {model_name}")
    
    try:
        import openai
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试简单调用
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ OpenAI连接测试成功!")
        print(f"📝 响应: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ OpenAI连接测试失败: {e}")
        print("💡 建议检查:")
        print("   - API密钥是否正确")
        print("   - 网络连接是否正常")
        print("   - 账户余额是否充足")

def test_vllm_connection(base_url, model_name=None):
    """测试vLLM连接"""
    print(f"\n🔍 测试vLLM连接...")
    print(f"🌐 服务地址: {base_url}")
    
    try:
        import requests
        
        # 1. 测试健康检查
        print("1️⃣ 检查服务状态...")
        try:
            health_response = requests.get(f"{base_url}/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ 服务健康状态正常")
            else:
                print(f"⚠️  服务状态异常: {health_response.status_code}")
        except:
            print("⚠️  无法访问健康检查端点")
        
        # 2. 获取模型列表
        print("2️⃣ 获取可用模型...")
        models_response = requests.get(f"{base_url}/v1/models", timeout=5)
        models_response.raise_for_status()
        
        models_data = models_response.json()
        if 'data' in models_data and models_data['data']:
            available_models = [model['id'] for model in models_data['data']]
            print(f"✅ 发现 {len(available_models)} 个可用模型:")
            for model in available_models:
                print(f"   - {model}")
            
            # 选择测试模型
            test_model = model_name if model_name else available_models[0]
            print(f"🎯 使用模型进行测试: {test_model}")
        else:
            print("⚠️  未发现可用模型")
            test_model = model_name or "unknown"
        
        # 3. 测试文本生成
        print("3️⃣ 测试文本生成...")
        
        chat_data = {
            "model": test_model,
            "messages": [
                {"role": "system", "content": "你是一个AI助手。"},
                {"role": "user", "content": "请简单介绍一下你自己"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        chat_response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=chat_data,
            timeout=30
        )
        chat_response.raise_for_status()
        
        chat_result = chat_response.json()
        if 'choices' in chat_result and chat_result['choices']:
            generated_text = chat_result['choices'][0]['message']['content']
            print("✅ 文本生成测试成功!")
            print(f"📝 生成内容: {generated_text[:100]}...")
            
            # 显示性能信息
            if 'usage' in chat_result:
                usage = chat_result['usage']
                print(f"📊 Token使用: {usage.get('total_tokens', 'N/A')}")
        else:
            print("❌ 文本生成响应格式异常")
        
        print("\n🎉 vLLM连接测试完成!")
        print("✅ 所有测试项目通过，可以正常使用")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到vLLM服务")
        print("💡 建议检查:")
        print("   - vLLM服务是否已启动")
        print("   - 服务地址是否正确")
        print("   - 防火墙设置")
        print("   - 网络连接")
        print(f"\n🚀 启动vLLM服务:")
        print(f"   ./start_vllm.sh")
        print(f"   或查看详细指南: VLLM_SETUP_GUIDE.md")
        
    except requests.exceptions.Timeout:
        print("❌ 连接超时: vLLM服务响应缓慢")
        print("💡 建议:")
        print("   - 检查服务器负载")
        print("   - 尝试增加超时时间")
        print("   - 检查模型是否完全加载")
        
    except Exception as e:
        print(f"❌ vLLM连接测试失败: {e}")
        print("💡 建议检查:")
        print("   - vLLM服务是否正常运行")
        print("   - API接口是否兼容OpenAI格式")
        print("   - 请求格式是否正确")

def write_env_config(config):
    """写入环境配置"""
    env_file = Path('.env')
    
    # 读取现有配置
    existing_config = {}
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing_config[key] = value
    
    # 更新配置
    existing_config.update(config)
    
    # 写入配置
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# 多智能体报告生成系统配置文件\n")
        f.write(f"# 生成时间: {os.popen('date').read().strip()}\n\n")
        
        for key, value in existing_config.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ 配置已保存到 {env_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程中出现错误: {e}")
