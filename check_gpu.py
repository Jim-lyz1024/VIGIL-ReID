import torch
from transformers import AutoModel

# 检查基本信息
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Current device: {torch.cuda.current_device()}")
print(f"Device name: {torch.cuda.get_device_name(0)}")

# 测试模型加载和推理
print("\nLoading model...")
model = AutoModel.from_pretrained("google/siglip-so400m-patch14-384")
model = model.to('cuda:0')
model.eval()

print(f"Model device: {next(model.parameters()).device}")

# 测试推理速度
import time
dummy_input = torch.randn(64, 3, 384, 384).to('cuda:0')

print("\nWarming up...")
with torch.no_grad():
    for _ in range(3):
        _ = model.get_image_features(**{'pixel_values': dummy_input})

print("\nTiming inference...")
torch.cuda.synchronize()
start = time.time()
with torch.no_grad():
    for _ in range(10):
        features = model.get_image_features(**{'pixel_values': dummy_input})
        torch.cuda.synchronize()
end = time.time()

avg_time = (end - start) / 10
print(f"Average inference time for batch_size=64: {avg_time:.3f}s")
print(f"Images per second: {64/avg_time:.1f}")