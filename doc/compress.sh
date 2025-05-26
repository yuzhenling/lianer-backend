#!/bin/bash

# 源目录（存放原始音频文件）
SOURCE_DIR="/home/yu/gitdev/shengyibaodian/app/static/audio/origin"  # 替换为你的源目录路径

# 输出目录（存放压缩后的文件）
OUTPUT_DIR="/home/yu/gitdev/shengyibaodian/app/static/audio/compressed"  # 替换为你的目标目录路径

# 创建输出目录（如果不存在）
mkdir -p "$OUTPUT_DIR"

# 支持的音频格式（可自行添加）
#FORMATS=("*.mp3" "*.wav" "*.flac" "*.ogg" "*.m4a")
FORMATS=("*.wav")
# 压缩参数（比特率，单位k；值越小文件越小，但音质越差）
BITRATE="64k"  # 建议范围：32k（低质量）~128k（平衡）

# 遍历所有音频文件并压缩
#for format in "${FORMATS[@]}"; do
#  while IFS= read -r -d '' file; do
#    # 获取文件名（不含路径和扩展名）
#    fullname=$(readlink -f "$file")
#    echo "--------------------------->"$fullname
#    filename=`echo "$fullname" | awk -F/ '{split($NF, arr, "."); print arr[1]}'`
#    # 输出文件路径（统一为.mp3格式）
#    output_file="$OUTPUT_DIR/$filename.mp3"
#
#    # 使用FFmpeg压缩
#    echo "ffmpeg -i "$file" -b:a "$BITRATE" -vn "$output_file" -y"
#    ffmpeg -i "$file" -b:a "$BITRATE" -vn "$output_file" -y
#
#    echo "已压缩: $file → $output_file"
##    sleep 1
#  done < <(find "$SOURCE_DIR" -type f -name "$format" -exec realpath -z {} \;)
#done

for file in "$SOURCE_DIR"/*; do
    # 只处理普通文件（跳过目录）
    if [[ -f "$file" ]]; then
        # 获取绝对路径（防止路径问题）
        fullpath=$(realpath "$file")
        echo "正在处理: $fullpath"

        # 提取文件名（不含路径和扩展名）
        filename=`echo "$fullpath" | awk -F/ '{split($NF, arr, "."); print arr[1]}'`

        # 设置输出路径（统一为 .mp3 格式）
        output_file="$OUTPUT_DIR/$filename.mp3"

        # 使用 FFmpeg 压缩
        echo "ffmpeg -i "$fullpath" -b:a "$BITRATE" -vn "$output_file" -y"
        ffmpeg -i "$fullpath" -b:a "$BITRATE" -vn "$output_file" -y

        echo "已压缩: $fullpath → $output_file"
    fi
done


echo "批量压缩完成！输出目录: $OUTPUT_DIR"