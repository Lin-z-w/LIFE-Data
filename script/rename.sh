#!/bin/bash

# 检查是否提供目录参数
if [ -z "$1" ]; then
  echo "请提供目标目录路径。用法: $0 /path/to/main_dir"
  exit 1
fi

TARGET_DIR="$1"

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
  echo "目录 $TARGET_DIR 不存在！"
  exit 1
fi

# 遍历所有子文件夹
for subdir in "$TARGET_DIR"/*/; do
  folder_name=$(basename "$subdir")
  tmp_file="${subdir}tmp.txt"
  new_txt="${subdir}${folder_name}.txt"

  # 重命名 tmp.txt -> 文件夹名.txt
  if [ -f "$tmp_file" ]; then
    mv "$tmp_file" "$new_txt"
    echo "已将 $tmp_file 重命名为 $new_txt"
  fi

  # 查找所有 .json 文件（只处理第一个）
  json_file=$(find "$subdir" -maxdepth 1 -name "*.json" | head -n 1)
  if [ -n "$json_file" ]; then
    new_json="${subdir}${folder_name}.json"
    mv "$json_file" "$new_json"
    echo "已将 $json_file 重命名为 $new_json"
  fi
done
