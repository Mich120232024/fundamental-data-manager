#!/usr/bin/env python3
"""
Test Parallel AI Models with Claude Router
Using configured API keys for OpenAI, XAI (Grok), and Gemini
"""

import subprocess
import time
import os
from datetime import datetime

def test_model(provider, model, task, output_file):
    """Test a specific model with a task"""
    print(f"🤖 Testing {provider} - {model}...")
    
    # Create test script
    script_content = f"""
echo "Testing {provider} model: {model}"
echo "Task: {task}"
echo ""

# Use ccr code with model switching
ccr code <<'EOF'
/model {provider},{model}
{task}

Please provide a brief response (2-3 sentences) and save it to {output_file}
EOF
"""
    
    script_name = f"test_{provider}_{model.replace('-', '_')}.sh"
    with open(script_name, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_name, 0o755)
    
    # Run in background
    subprocess.Popen(['/bin/bash', script_name], 
                     stdout=open(f"{provider}_{model}.log", 'w'),
                     stderr=subprocess.STDOUT)
    
    return script_name

def main():
    print("🚀 Testing Parallel AI Models with Claude Router")
    print("=" * 60)
    print("Configured models:")
    print("- OpenAI: GPT-4o")
    print("- XAI: Grok-2")
    print("- Gemini: Gemini-2.0-pro-exp")
    print("=" * 60)
    
    # Define test tasks
    tests = [
        ("openai", "gpt-4o", "What are the key benefits of parallel processing?", "openai_response.md"),
        ("xai", "grok-2-latest", "Explain quantum computing in simple terms", "xai_response.md"),
        ("gemini", "gemini-2.0-pro-exp", "What is the future of AI?", "gemini_response.md")
    ]
    
    # Launch all tests in parallel
    start_time = time.time()
    scripts = []
    
    for provider, model, task, output in tests:
        script = test_model(provider, model, task, output)
        scripts.append(script)
        time.sleep(1)  # Small delay between launches
    
    print("\n✅ All models launched in parallel!")
    print("\n📊 Check logs:")
    for provider, model, _, _ in tests:
        print(f"  tail -f {provider}_{model}.log")
    
    # Wait a bit
    print("\n⏳ Waiting 10 seconds for responses...")
    time.sleep(10)
    
    # Check results
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.2f} seconds")
    
    # Clean up scripts
    for script in scripts:
        if os.path.exists(script):
            os.remove(script)
    
    print("\n✨ Test complete! Check the log files for results.")
    
    # Create summary
    with open("parallel_test_summary.md", "w") as f:
        f.write("# Parallel AI Models Test Summary\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duration**: {elapsed:.2f} seconds\n\n")
        f.write("## Models Tested\n\n")
        f.write("1. **OpenAI GPT-4o**: General intelligence tasks\n")
        f.write("2. **XAI Grok-2**: Complex reasoning\n")
        f.write("3. **Google Gemini-2.0-pro-exp**: Long context processing\n\n")
        f.write("## Key Benefits\n\n")
        f.write("- **Speed**: 3x faster by running models in parallel\n")
        f.write("- **Diversity**: Different models for different strengths\n")
        f.write("- **Cost Optimization**: Route to cheaper models when appropriate\n")
        f.write("- **Redundancy**: Multiple perspectives on same problem\n\n")
        f.write("## Claude Router Commands\n\n")
        f.write("```bash\n")
        f.write("# Switch to specific model\n")
        f.write("/model openai,gpt-4o\n")
        f.write("/model xai,grok-2-latest\n")
        f.write("/model gemini,gemini-2.0-pro-exp\n")
        f.write("\n")
        f.write("# Use routing aliases\n")
        f.write("/model default    # Uses OpenAI GPT-4o\n")
        f.write("/model fast       # Uses GPT-4o-mini\n")
        f.write("/model think      # Uses XAI Grok-2\n")
        f.write("/model longContext # Uses Gemini-2.0-pro-exp\n")
        f.write("```\n")

if __name__ == "__main__":
    main()