#!/bin/bash

# 定义目标目录列表
TARGET_DIRS=(
  "./origin_data/throughput/congest"
  "./origin_data/throughput/rain"
  "./origin_data/throughput/random_loss"
  "./origin_data/throughput/reconfig&hadover"
  "./origin_data/standard"
  "./origin_data/intra-protocol/2flow"
  "./origin_data/intra-protocol/3flow"
  "./origin_data/inter-protocol"
)

# 递归处理目录函数
process_dir() {
  local dir="$1"
  local folder_name=$(basename "$dir")
  
  # 处理当前目录中的文件
  tmp_file="$dir/tmp.txt"
  new_txt="$dir/$folder_name.txt"
  if [ -f "$tmp_file" ]; then
    mv "$tmp_file" "$new_txt"
    echo "已将 $tmp_file 重命名为 $new_txt"
  fi

  json_file=$(find "$dir" -maxdepth 1 -name "*.json" | head -n 1)
  if [ -n "$json_file" ]; then
    new_json="$dir/$folder_name.json"
    mv "$json_file" "$new_json"
    echo "已将 $json_file 重命名为 $new_json"
  fi

  pcc_log="$dir/pcc_log"
  if [ -f "$pcc_log" ]; then
    mv "$pcc_log" "$dir/PCC"
    echo "已将 $pcc_log 重命名为 $dir/PCC"
  fi

  # 递归处理子目录
  for subdir in "$dir"/*/; do
    if [ -d "$subdir" ]; then
      process_dir "$subdir"
    fi
  done
}

# 主循环：处理所有目标目录
for target in "${TARGET_DIRS[@]}"; do
  # 解析为绝对路径（避免相对路径问题）
  target_dir=$(cd "$target" 2>/dev/null && pwd)
  if [ -z "$target_dir" ]; then
    echo "警告：目录不存在或无法访问 -> $target"
    continue
  fi

  echo "正在处理目录: $target_dir"
  process_dir "$target_dir"
done

echo "所有目录处理完成"