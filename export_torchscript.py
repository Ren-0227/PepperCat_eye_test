import torch
from image_processing import OCTClassifier  # 或 train_model

# 加载全模型对象
model = torch.load('full_model.pth', map_location='cpu')
model.eval()
# 导出为TorchScript
scripted = torch.jit.script(model)
scripted.save('oct_scripted.pt')
print("TorchScript模型已导出为 oct_scripted.pt")