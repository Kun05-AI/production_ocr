import platform
import sys
import torch

print('Python:', sys.version)
print('Platform:', platform.platform())
print('PyTorch:', torch.__version__)
print('PyTorch CUDA build:', torch.version.cuda)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    props = torch.cuda.get_device_properties(0)
    print(f'VRAM: {props.total_memory / 1024**3:.2f} GiB')
