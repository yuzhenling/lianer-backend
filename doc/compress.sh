#!/bin/bash

# 源目录（存放原始音频文件）
SOURCE_DIR="/home/yu/gitdev/shengyibaodian/app/static/audio"  # 替换为你的源目录路径

# 输出目录（存放压缩后的文件）
OUTPUT_DIR="/home/yu/gitdev/shengyibaodian/app/static/audio/compressed"  # 替换为你的目标目录路径

# 创建输出目录（如果不存在）
mkdir -p "$OUTPUT_DIR"

# 支持的音频格式（可自行添加）
FORMATS=("*.mp3" "*.wav" "*.flac" "*.ogg" "*.m4a")

# 压缩参数（比特率，单位k；值越小文件越小，但音质越差）
BITRATE="64k"  # 建议范围：32k（低质量）~128k（平衡）

# 遍历所有音频文件并压缩
for format in "${FORMATS[@]}"; do
  while IFS= read -r -d '' file; do
    # 获取文件名（不含路径和扩展名）
    filename=$(basename "$file" | sed 's/\.[^.]*$//')

    # 输出文件路径（统一为.mp3格式）
    output_file="$OUTPUT_DIR/$filename.mp3"

    # 使用FFmpeg压缩
    ffmpeg -i "$file" -b:a "$BITRATE" -vn "$output_file" -y

    echo "已压缩: $file → $output_file"
  done < <(find "$SOURCE_DIR" -type f -name "$format" -print0)
done

echo "批量压缩完成！输出目录: $OUTPUT_DIR"