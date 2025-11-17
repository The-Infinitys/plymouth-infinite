import argparse
import os
import math

# ==============================================================================
# 1. 定数とユーティリティ
# ==============================================================================

# モーフィングアニメーションに使用する座標リスト
# 元のパスポイントを使用します（10点）
PATH_POINTS = [
  [10, 30], [20, 50], [50, 50], [70, 10], [100, 10],
  [110, 30], [100, 50], [70, 50], [50, 10], [20, 10],
]
NUM_PATH_POINTS = len(PATH_POINTS) # 10

# パスのセグメント数 (M + 6 Ls = 7点を使用)
SEGMENT_COUNT = 6
PATH_POINTS_USED = SEGMENT_COUNT + 1 # 7点

# アニメーションの基本サイクル数
PATH_CYCLE_LENGTH = NUM_PATH_POINTS # パスの全ポイントを一周するのに10フレーム分の動き

# パスと色の両方をアニメーション全体で6回周回させる乗数
ANIMATION_CYCLE_MULTIPLIER = 6 

# カラーサイクルに使用する特定の色（6色）
# 遷移順序: F00 -> FF0 -> 0F0 -> 0FF -> 00F -> F0F -> F00
COLORS_CYCLE = ['F00', 'FF0', '0F0', '0FF', '00F', 'F0F']
WHITE_HEX = 'FFFFFF'
NUM_COLOR_TRANSITIONS = len(COLORS_CYCLE) # 6つの色遷移

# 1つの色遷移（例: F00 -> FF0）は 3つのサブセグメントで構成されます:
# 1. 白(W) -> 色1(C1)
# 2. 色1(C1) -> 色2(C2) (ユーザー指定のグラデーション中間部分)
# 3. 色2(C2) -> 白(W)
TOTAL_COLOR_SEGMENTS = NUM_COLOR_TRANSITIONS * 3 # 6 * 3 = 18

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """16進数カラーコード (RRGGBB または RGB) をRGBタプルに変換します。"""
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """RGBタプルを16進数カラーコードに変換します。"""
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"

def interpolate_color(start_hex: str, end_hex: str, t: float) -> str:
    """2つの色の間で線形補間を行い、結果の16進数カラーコードを返します。"""
    r1, g1, b1 = hex_to_rgb(start_hex)
    r2, g2, b2 = hex_to_rgb(end_hex)
    
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    
    return rgb_to_hex(r, g, b)

# ==============================================================================
# 2. フレーム生成ロジック
# ==============================================================================

def generate_frame_data(frame_index: int, total_frames: int) -> tuple[str, str, str]:
    """
    指定されたフレームインデックスにおけるSVGパスデータと色を計算します。
    
    Args:
        frame_index: 現在のフレーム番号 (0 から total_frames - 1)
        total_frames: アニメーションの総フレーム数
        
    Returns:
        (path_d: str, stroke_color1: str, stroke_color2: str)
    """
    
    # --------------------------------------------------
    # A. パス (モーフィング) の計算 - 6回周回
    # --------------------------------------------------
    
    # アニメーション全体を0.0からPATH_CYCLE_LENGTH * 6 までの値に正規化 (6回周回)
    cycle_norm = (frame_index / total_frames) * PATH_CYCLE_LENGTH * ANIMATION_CYCLE_MULTIPLIER
    # cycle_norm は 0.0 から約 60.0 まで変化

    # 基点となるキーフレームインデックス (0から9)
    base_index = math.floor(cycle_norm) % NUM_PATH_POINTS
    
    # 補間係数 (0.0 から 1.0)
    color_idx=math.floor(frame_index/total_frames * 6)
    c_interp=cycle_norm / PATH_CYCLE_LENGTH - color_idx
    t_interp = cycle_norm - math.floor(cycle_norm)

    path_d = ""
    points = []
    
    for k in range(PATH_POINTS_USED):
        # 現在のキーフレームでのポイントのインデックス
        idx_current = (base_index + k) % NUM_PATH_POINTS
        # 次のキーフレームでのポイントのインデックス (次のbase_indexに相当)
        idx_next = (base_index + 1 + k) % NUM_PATH_POINTS
        
        # 現在の座標と次の座標
        p_current = PATH_POINTS[idx_current]
        p_next = PATH_POINTS[idx_next]
        
        # 座標の線形補間
        x = p_current[0] + (p_next[0] - p_current[0]) * t_interp
        y = p_current[1] + (p_next[1] - p_current[1]) * t_interp
        
        # Mコマンドの最初の点だけは前の点がないためスキップ
        if k!=0:
          points.append((p_current[0],p_current[1]))
        points.append((x, y))
    if points:
        path_d += f"M {points[0][0]:.4f},{points[0][1]:.4f}"
        for x, y in points[1:]:
            path_d += f" L {x:.4f},{y:.4f}"

    color1=COLORS_CYCLE[color_idx%len(COLORS_CYCLE)]
    color2=COLORS_CYCLE[(color_idx+1)%len(COLORS_CYCLE)]
    t_color=1 - abs(c_interp - 0.5) * 2        
    stroke_color1 = interpolate_color(WHITE_HEX, color1, t_color)
    stroke_color2 = interpolate_color(WHITE_HEX, color2, t_color)

    return path_d, stroke_color1, stroke_color2

def generate_svg_file(frame_index: int, total_frames: int, output_dir: str):
    """単一のSVGファイルを生成して保存します。"""
    
    path_d, stroke_color1, stroke_color2 = generate_frame_data(frame_index, total_frames)
    
    # ファイル名のフォーマット (throbber-0000.svg, throbber-0001.svg, ...)
    filename = os.path.join(output_dir, f"throbber-{frame_index:04d}.svg")
    
    # SVGテンプレート - linearGradientを使用して単色をパスに適用
    svg_content = f"""\
<svg
    viewBox="0 0 120 60" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">

    <defs>
        <!-- 時間によって変化する単色を表現するための線形グラデーションを定義 -->
        <!-- 始点と終点の両方に計算された stroke_color を設定することで、パス全体を均一に塗ります -->
        <linearGradient id="animated-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="{stroke_color1}" />
            <stop offset="100%" stop-color="{stroke_color2}" />
        </linearGradient>
    </defs>
    
    <path
        d="{path_d}"
        fill="none"
        stroke="url(#animated-gradient)"
        stroke-width="8"
        stroke-linecap="round"
        stroke-linejoin="round"
    />
</svg>
"""
    
    with open(filename, 'w') as f:
        f.write(svg_content)

def main():
    parser = argparse.ArgumentParser(
        description="Plymouthアニメーション用のSVGフレームを生成します。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "total_frames", 
        type=int, 
        help="生成するSVGフレームの総数。108（カラーサイクル数18×周回数6）の倍数で、かつパスアニメーションの滑らかさを考慮して120以上を推奨します。\n例: 120, 216, 360, 432"
    )
    
    args = parser.parse_args()
    total_frames = args.total_frames
    output_dir = "throbber_frames"

    if total_frames < 1:
        print("エラー: 総フレーム数は1以上の整数である必要があります。")
        return

    # 出力ディレクトリを作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"ディレクトリ '{output_dir}' を作成しました。")
    
    print(f"総フレーム数: {total_frames}、SVGフレームの生成を開始します...")

    for i in range(total_frames):
        generate_svg_file(i, total_frames, output_dir)
        if (i + 1) % 50 == 0 or i == total_frames - 1:
             print(f"進行状況: {i + 1}/{total_frames} フレーム")

    print(f"\n✅ {total_frames} 個のSVGフレームが '{output_dir}' ディレクトリに正常に生成されました。")
    print("\nこれらのファイルは、Plymouthの`.script`ファイルで使用できます。")


if __name__ == "__main__":
    main()