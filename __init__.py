# 这是 __init__.py 文件的示例
# 导入自定义节点类
from .image_to_stl_node import ImageToSTLNode

# 定义节点类映射
NODE_CLASS_MAPPINGS = {
    "ImageToSTLNode": ImageToSTLNode
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToSTLNode": "ImageToSTLNode"
}