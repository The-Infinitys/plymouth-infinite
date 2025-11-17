#!/bin/bash
#
# Plymouthテーマインストールスクリプト
# テーマをシステムにコピーし、有効化します。
# -----------------------------------------------------------

# エラーが発生したらすぐに終了
set -e

# エラーが発生したらすぐに終了する

# --- 1. プロジェクトのルートディレクトリに移動 ---
# スクリプトがどこから実行されても、常にプロジェクトのルートディレクトリを基準とする
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR/.."
echo "プロジェクトのルートディレクトリに移動しました: $(pwd)"

# --- 設定 ---
THEME_NAME="plymouth-infinite"
BUILD_DIR="./build"
INSTALL_PATH="/usr/share/plymouth/themes/$THEME_NAME"

# --- 引数処理 ---
SKIP_INITRAMFS=false
if [[ "$1" == "test" ]]; then
    SKIP_INITRAMFS=true
    echo "⚠️ テストモードが有効です。initramfsの更新はスキップされます。"
fi

# --- 権限チェック ---
if [[ $EUID -ne 0 ]]; then
   echo "🚨 エラー: このスクリプトはroot権限で実行する必要があります (sudoを使用してください)。"
   exit 1
fi

# --- ビルド済みファイルの存在チェック ---
if [ ! -d "$BUILD_DIR" ] || [ -z "$(ls -A $BUILD_DIR)" ]; then
    echo "🚨 エラー: ビルドディレクトリ '$BUILD_DIR' が存在しないか、空です。"
    echo "   先に './build.sh' を実行してテーマをビルドしてください。"
    exit 1
fi

# --- インストール処理 ---
echo "🚀 Plymouthテーマ '$THEME_NAME' のインストールを開始します..."

# 1. 既存のインストールパスをクリーンアップし、作成
echo "🧹 既存のテーマディレクトリをクリーンアップ中..."
rm -rf "$INSTALL_PATH"
echo "📁 インストールディレクトリを作成中: $INSTALL_PATH"
mkdir -p "$INSTALL_PATH"

# 2. ビルド済みファイルをコピー
echo "📤 テーマファイルを '$BUILD_DIR' から '$INSTALL_PATH' へコピー中..."
cp -r "$BUILD_DIR"/* "$INSTALL_PATH/"
echo "✅ テーマファイルのコピーが完了しました。"

# 3. 新しいテーマをデフォルトとして設定 (update-alternativesを使用)
echo "⚙️ update-alternatives を使用して Plymouth テーマを登録・設定中..."
# 注意: この方法は、Plymouthテーマの標準的な設定方法 (plymouth-set-default-theme) とは異なり、
# システムによっては正しくテーマが適用されない可能性があります。

# テーマパスを 'plymouth-default-theme' という代替手段グループに登録
# リンク名: plymouth-default-theme, リンク先: /usr/share/plymouth/themes/default
update-alternatives --install \
    /usr/share/plymouth/themes/default.plymouth \
    default.plymouth \
    "$INSTALL_PATH/$THEME_NAME.plymouth" 100  # 優先度 100 で登録

# 登録したテーマをアクティブに設定
update-alternatives --set default.plymouth "$INSTALL_PATH/$THEME_NAME.plymouth"

echo "✅ update-alternatives によるテーマの設定が完了しました。"

# 4. initramfsを更新
echo "🔄 初期RAMディスク (initramfs) を更新中..."

if [ "$SKIP_INITRAMFS" = true ]; then
    echo "   テストモードが有効なため、initramfs の更新はスキップされました。"
else
    # Ubuntu/Debian系向けのコマンド
    if command -v update-initramfs &> /dev/null; then
        update-initramfs -u
        echo "✅ update-initramfs が正常に完了しました。"

    # Fedora/RHEL系向けのコマンド（オプションとして追加）
    elif command -v dracut &> /dev/null; then
        dracut --force
        echo "✅ dracut が正常に完了しました。"
    else
        echo "⚠️ 警告: 'update-initramfs' または 'dracut' コマンドが見つかりません。"
        echo "   手動で initramfs の更新コマンドを実行してください。"
    fi
fi

# --- 完了 ---
echo "--------------------------------------------------------"
echo "🎉 Plymouthテーマ '$THEME_NAME' のインストール処理が完了しました。"
if [ "$SKIP_INITRAMFS" = true ]; then
    echo "   (initramfsの更新はスキップされました。テストが完了したら、手動で 'sudo update-initramfs -u' などを実行してください)"
else
    echo "   動作を確認するには、システムを再起動してください: sudo reboot"
fi
echo "--------------------------------------------------------"