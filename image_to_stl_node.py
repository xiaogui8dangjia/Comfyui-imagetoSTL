import os
import numpy as np
from PIL import Image
import trimesh


class ImageToSTLNode:
    @classmethod
    def INPUT_TYPES(s):
        # 固定导出路径
        output_dir = r"C:\Users\Administrator\Desktop"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        default_base_name = "模型"
        default_extension = ".stl"
        default_save_path = os.path.join(output_dir, f"{default_base_name}{default_extension}")
        return {
            "required": {
                "image": ("IMAGE",),
                "save_path": ("STRING", {"default": default_save_path}),
                "height_scale": ("FLOAT", {"default": 20.0, "min": 10.0, "max": 40.0, "step": 0.1}),
                "x_scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "y_scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1})
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("stl_file_path",)
    FUNCTION = "convert_image_to_stl"
    CATEGORY = "Custom Nodes"

    def convert_image_to_stl(self, image, save_path, height_scale, x_scale, y_scale):
        try:
            # 将 ComfyUI 的图像数据转换为 PIL 图像
            image = Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

            # 处理图像，这里可以参考你提供的 JavaScript 代码中的图像处理逻辑
            maxResolution = 500
            scale = min(maxResolution / image.width, maxResolution / image.height)
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.BICUBIC)

            # 获取图像数据
            image_data = image.getdata()

            # 根据图像数据创建带高度的 3D 几何形状
            vertices, faces = self.create_geometry_from_image_data(image_data, new_width, new_height, height_scale, x_scale, y_scale)

            # 调整顶点坐标使模型中心位于原点且最低点在Z轴0平面
            vertices = self.center_vertices(vertices, new_width * x_scale, new_height * y_scale, height_scale)

            # 创建 trimesh 对象
            mesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces)

            # 顺时针旋转 180 度（绕 Z 轴）
            rotation_matrix = trimesh.transformations.rotation_matrix(np.radians(180), [0, 0, 1])
            mesh_obj.apply_transform(rotation_matrix)

            # 处理文件名避免重复
            save_path = self.get_non_duplicate_path(save_path)

            # 导出 STL 文件
            stl_file_path = self.export_stl(mesh_obj, save_path)

            return (stl_file_path,)

        except Exception as e:
            print(f"Error converting image to STL: {e}")
            return ("",)

    def create_geometry_from_image_data(self, image_data, width, height, height_scale, x_scale, y_scale):
        vertices = []
        faces = []
        # 假设图像是灰度图，将像素值映射到高度
        for y in range(height):
            for x in range(width):
                pixel = image_data[y * width + x]
                if isinstance(pixel, tuple):
                    # 如果是彩色图像，取第一个通道（这里简单处理）
                    height_value = pixel[0] / 255.0 * height_scale
                else:
                    height_value = pixel / 255.0 * height_scale
                # 反转X坐标
                vertices.append([(width - 1 - x) * x_scale, y * y_scale, height_value])
        for y in range(height - 1):
            for x in range(width - 1):
                index1 = y * width + x
                index2 = y * width + x + 1
                index3 = (y + 1) * width + x
                index4 = (y + 1) * width + x + 1
                # 再次调整面的顶点顺序
                faces.append([index1, index2, index4])
                faces.append([index1, index4, index3])
        return np.array(vertices), np.array(faces)

    def export_stl(self, mesh_obj, save_path):
        # 保存 STL 文件
        mesh_obj.export(save_path)
        return save_path

    def get_non_duplicate_path(self, path):
        base_name, extension = os.path.splitext(path)
        counter = 1
        while os.path.exists(path):
            path = f"{base_name}_{counter}{extension}"
            counter += 1
        return path

    def center_vertices(self, vertices, width, height, height_scale):
        # 计算模型在 x 和 y 方向的中心偏移量
        x_offset = width / 2
        y_offset = height / 2
        for vertex in vertices:
            vertex[0] -= x_offset
            vertex[1] -= y_offset
        return vertices


# 节点定义
NODE_CLASS_MAPPINGS = {
    "ImageToSTLNode": ImageToSTLNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToSTLNode": "Image to STL Converter"
}
