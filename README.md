# temporary_images

GitHub 图片 CDN 仓库，配合 jsDelivr 使用。

## CDN 访问

```
https://cdn.jsdelivr.net/gh/smallyangy/temporary_images@master/images/<文件名>

如：https://cdn.jsdelivr.net/gh/smallyangy/temporary_images@master/images/视频.png
```

## 使用上传脚本

```bash
# 1. 复制配置文件并填入 token
cp config.example.json config.json

# 2. 安装依赖
pip install requests

# 3. 上传图片
python upload.py photo.png
python upload.py img1.jpg img2.jpg img3.png   # 批量上传
```
