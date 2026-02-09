#!/usr/bin/env bash

# ================== CONFIG ==================
# Each entry: "Description|command to execute"
mEntries=(
  "Run QNX x86_64 QEMU | bazel run --config qnx-x86_64 //qnx_x86_64:run"
  "Run Linux x86_64 Docker | bazel run --config linux-x86_64 //linux_x86_64:run"
  "Run Elektrobit Corbos aarch64 QEMU | bazel build --config eb-aarch64 //ebclfsa_aarch64/scrample_integration:run"
  "Exit|exit 0"
)

# ================== INTERNAL ==================
mDescriptions=()
mCommands=()

for mEntry in "${mEntries[@]}"; do
  mDescriptions+=("${mEntry%%|*}")
  mCommands+=("${mEntry#*|}")
done

mSelected=0
mCount=${#mDescriptions[@]}

draw_menu() {
  clear
  echo "Use ↑ ↓ to navigate, Enter to run, q to quit"
  echo

  for i in "${!mDescriptions[@]}"; do
    if [[ $i -eq $mSelected ]]; then
      printf "  \e[7m %s \e[0m\n" "${mDescriptions[$i]}"
    else
      printf "    %s\n" "${mDescriptions[$i]}"
    fi
  done
}

run_selected() {
  clear
  echo "▶ ${mDescriptions[$mSelected]}"
  echo

  eval "${mCommands[$mSelected]}"
}

# ================== LOOP ==================
while true; do
  draw_menu

  IFS= read -rsn1 mKey
  case "$mKey" in
    $'\x1b')
      read -rsn2 mKey
      case "$mKey" in
        "[A") ((mSelected = (mSelected - 1 + mCount) % mCount)) ;;
        "[B") ((mSelected = (mSelected + 1) % mCount)) ;;
      esac
      ;;
    "")
      run_selected
      exit $?
      ;;
    q)
      exit 0
      ;;
  esac
done
