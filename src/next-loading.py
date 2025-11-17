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

# カラーサイクルに使用する特定の色（6色）
COLORS = ['F00', 'FF0', '0F0', '0FF', '00F', 'F0F']

# アニメーションの基本サイクル数
PATH_CYCLE_LENGTH = NUM_PATH_POINTS # パスの全ポイントを一周するのに10フレーム分の動き

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

def generate_frame_data(frame_index: int, total_frames: int) -> tuple[str, str]:
    """
    指定されたフレームインデックスにおけるSVGパスデータと色を計算します。
    
    Args:
        frame_index: 現在のフレーム番号 (0 から total_frames - 1)
        total_frames: アニメーションの総フレーム数
        
    Returns:
        (path_d: str, stroke_color: str)
    """
    
    # --------------------------------------------------
    # A. パス (モーフィング) の計算
    # --------------------------------------------------
    
    # アニメーション全体を0.0からPATH_CYCLE_LENGTH (10) までの値に正規化
    cycle_norm = (frame_index / total_frames) * PATH_CYCLE_LENGTH

    # 基点となるキーフレームインデックス (0から9)
    base_index = math.floor(cycle_norm) % NUM_PATH_POINTS
    
    # 補間係数 (0.0 から 1.0)
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
        if k!=0:
          points.append((p_current[0],p_current[1]))
        points.append((x, y))

    # パスデータの構築 (M - L - L - ...)
    if points:
        path_d += f"M {points[0][0]:.4f},{points[0][1]:.4f}"
        for x, y in points[1:]:
            path_d += f" L {x:.4f},{y:.4f}"

    # --------------------------------------------------
    # B. 色 (カラーサイクル) の計算 (滑らかなグラデーションを保証)
    # --------------------------------------------------
    
    TOTAL_COLOR_SEGMENTS = len(COLORS) * 2 # 12 segments: W->C, C->W, W->C, ...
    
    # アニメーション全体にわたる正規化された時間 (0.0 <= t < TOTAL_COLOR_SEGMENTS)
    # total_framesで割り、TOTAL_COLOR_SEGMENTSを掛けることで、総時間スケールを12サイクルに正規化
    normalized_time = (frame_index / total_frames) * TOTAL_COLOR_SEGMENTS
    
    # 現在のセグメントインデックス (0から11)
    color_segment_index = math.floor(normalized_time) % TOTAL_COLOR_SEGMENTS
    
    # セグメント内の補間係数 (0.0 から 1.0)
    # normalized_timeから現在のセグメントの開始時間(color_segment_index)を引くことで、0.0から1.0の値を得る
    t_color = normalized_time - color_segment_index

    # 開始色と終了色を決定
    WHITE_HEX = 'FFFFFF'
    
    if color_segment_index % 2 == 0:
        # 偶数インデックス: WHITE -> COLOR
        start_hex = WHITE_HEX
        color_index = color_segment_index // 2
        end_hex = COLORS[color_index]
    else:
        # 奇数インデックス: COLOR -> WHITE
        color_index = (color_segment_index - 1) // 2
        start_hex = COLORS[color_index]
        end_hex = WHITE_HEX
        
    stroke_color = interpolate_color(start_hex, end_hex, t_color)

    return path_d, stroke_color

def generate_svg_file(frame_index: int, total_frames: int, output_dir: str):
    """単一のSVGファイルを生成して保存します。"""
    
    path_d, stroke_color = generate_frame_data(frame_index, total_frames)
    
    # ファイル名のフォーマット (throbber-0000.svg, throbber-0001.svg, ...)
    filename = os.path.join(output_dir, f"throbber-{frame_index:04d}.svg")
    
    # SVGテンプレート
    svg_content = f"""\
<svg
    viewBox="0 0 120 60" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">

    <!-- 背景は透明にしてPlymouthが背景色を使用できるようにするか、単色にします -->
    <!-- <rect x="0" y="0" width="120" height="60" fill="#0ff" /> -->
    
    <path
        d="{path_d}"
        fill="none"
        stroke="{stroke_color}"
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
        help="生成するSVGフレームの総数。12の倍数で、かつパスアニメーションの滑らかさを考慮して120以上を推奨します。\n例: 120, 240, 360"
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