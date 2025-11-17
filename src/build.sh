#!/bin/bash
#
# Plymouthテーマのビルドスクリプト
# 
# 前提条件:
# 1. プロジェクトのルートディレクトリで実行されること。
# 2. SVGをPNGに変換するための 'rsvg-convert' コマンドがインストールされていること。
# 3. ローディングアニメーションを生成する 'src/cross-loading.py' が存在すること。
#
# -----------------------------------------------------------

# エラーが発生したらすぐに終了する
set -e

# --- 1. プロジェクトのルートディレクトリに移動 ---
# スクリプトがどこから実行されても、常にプロジェクトのルートディレクトリを基準とする
IMG_SIZE=256
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR/.."
echo "プロジェクトのルートディレクトリに移動しました: $(pwd)"

TOTAL_FRAME=360
# --- 2. buildディレクトリのクリーンアップと作成 ---
BUILD_DIR="./build"
echo "🧹 古いビルドディレクトリをクリーンアップ中..."
rm -rf "$BUILD_DIR"
echo "📁 新しいビルドディレクトリを作成中: $BUILD_DIR"
mkdir -p "$BUILD_DIR"

# --- 3. ローディングアニメーションフレームの生成 ---
PYTHON_SCRIPT="./src/cross-loading.py"
THROBBER_DIR="./throbber_frames"

if [ -f "$PYTHON_SCRIPT" ]; then
    echo "⚙️ ローディングアニメーションフレームを生成中..."
    
    # 既存のthrobber_framesをクリーンアップ
    rm -rf "$THROBBER_DIR"
    
    # Pythonスクリプトを実行して360枚のSVGフレームを生成
    python3 "$PYTHON_SCRIPT" $TOTAL_FRAME

    if [ ! -d "$THROBBER_DIR" ]; then
        echo "🚨 エラー: Pythonスクリプトが $THROBBER_DIR を作成しませんでした。ビルドを中断します。"
        exit 1
    fi
else
    echo "🚨 エラー: Pythonスクリプト '$PYTHON_SCRIPT' が見つかりません。ビルドを中断します。"
    exit 1
fi

# --- 4. 360枚のSVGフレームをPNGに変換し、buildディレクトリに入れる ---
echo "🖼️ $TOTAL_FRAME 枚のSVGフレームをPNGに一括変換中..."
# rsvg-convertを使用してSVGをPNGに変換
# rsvg-convertがない場合はエラーメッセージを表示して終了
if ! command -v rsvg-convert &> /dev/null
then
    echo "🚨 エラー: 'rsvg-convert' コマンドが見つかりません。"
    echo "  librsvg (または対応するパッケージ) をインストールしてください (例: sudo apt install librsvg2-bin)"
    exit 1
fi

for svg_file in "$THROBBER_DIR"/*.svg; do
    # ファイル名から拡張子を除去 (例: throbber_frames/frame-001.svg -> frame-001)
    filename=$(basename -- "$svg_file")
    filename_no_ext="${filename%.*}"
    
    # PNGに変換してbuildディレクトリに出力
    rsvg-convert -w $IMG_SIZE -h $IMG_SIZE -o "$BUILD_DIR/$filename_no_ext.png" "$svg_file"
done

echo "✅ アニメーションフレームの変換が完了しました。"
# 生成したSVGフレームディレクトリを削除 (中間ファイル)
rm -rf "$THROBBER_DIR"

# --- 5. 個別SVGファイルをPNGに変換 ---
echo "🖼️ 個別SVGファイルをPNGに変換中..."

# 変換リストを定義: (ソースSVG, ターゲットPNG名)
declare -A SVG_CONVERSIONS
SVG_CONVERSIONS[src/lock.svg]="lock.png"
SVG_CONVERSIONS[src/entry-nolock.svg]="entry-nolock.png"
SVG_CONVERSIONS[src/entry.svg]="entry.png"
SVG_CONVERSIONS[src/watermark.svg]="watermark.png"

for svg_source in "${!SVG_CONVERSIONS[@]}"; do
    png_target="${SVG_CONVERSIONS[$svg_source]}"
    
    if [ -f "$svg_source" ]; then
        rsvg-convert -o "$BUILD_DIR/$png_target" "$svg_source"
        echo "   -> $svg_source を $BUILD_DIR/$png_target に変換しました。"
    else
        echo "⚠️ 警告: ファイル '$svg_source' が見つかりません。"
    fi
done

# --- 6. src/imgディレクトリからの静的ファイルのコピー ---
IMG_SRC_DIR="./src/img"
echo "📋 静的ファイルを $IMG_SRC_DIR からコピー中..."

# コピーするファイルのリスト
STATIC_FILES=(
    "bullet.png"
    "capslock.png"
    "keyboard_24px.png"
    "keyboard_48px.png"
    "keyboard.png"
    "keymap_render.png"
    "lock.svg"  # 意図的にSVGのままコピー
    "progress-00.png"
)

for file in "${STATIC_FILES[@]}"; do
    if [ -f "$IMG_SRC_DIR/$file" ]; then
        cp "$IMG_SRC_DIR/$file" "$BUILD_DIR/"
        echo "   -> $file をコピーしました。"
    else
        echo "⚠️ 警告: ファイル '$IMG_SRC_DIR/$file' が見つかりません。"
    fi
done

# --- 7. Plymouth設定ファイルのコピー ---
echo "📄 Plymouth設定ファイルをコピー中..."
PLT_FILES=(
    "src/plymouth-infinite.grub"
    "src/plymouth-infinite.plymouth"
    "src/plymouth-infinite.script"
)

for file in "${PLT_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BUILD_DIR/"
        echo "   -> $file をコピーしました。"
    else
        echo "⚠️ 警告: ファイル '$file' が見つかりません。"
    fi
done

# --- 8. 完了 ---
echo "--------------------------------------------------------"
echo "✨ ビルドプロセスが正常に完了しました！"
echo "   テーマファイルは '$BUILD_DIR' ディレクトリにあります。"
echo "--------------------------------------------------------"
