path_points=[
  [10,30],
  [20,50],
  [50,50],
  [70,10],
  [100,10],
  [110,30],
  [100,50],
  [70,50],
  [50,10],
  [20,10],
]

def morphing(length:int)->str:
  index_points = [i if i < length else length - 1 for i in range(length + 1)]
  for i in range(len(index_points)):
    index_points[i] = index_points[i] - 1
  values_result = ""
  keytimes_result = ""
  keytimes=0.0
  for i in range(len(path_points)+1):
    keytimes = (i) / len(path_points)
    index_points[0]=(index_points[0]+1)%len(path_points)
    index_points[len(index_points) - 1]=(index_points[len(index_points) - 1]+1)%len(path_points)
    path = f"M {path_points[index_points[0]][0]},{path_points[index_points[0]][1]}"
    for j in range(len(index_points)):
      if j!=0:
        path += f"L {path_points[index_points[j]][0]},{path_points[index_points[j]][1]}"
    values_result += f"{path};\n"
    keytimes_result += f"{format(keytimes,'.10f')};\n"
    print(index_points,keytimes)
    for k in range(len(index_points)):
      if k!=0 and k!=len(index_points) - 1:
        index_points[k] = (index_points[k] + 1) % len(path_points)
        path = f"M {path_points[index_points[0]][0]},{path_points[index_points[0]][1]}"
        for j in range(len(index_points)):
          if j!=0:
            path += f"L {path_points[index_points[j]][0]},{path_points[index_points[j]][1]}"
        values_result += f"{path};\n"
        keytimes_result += f"{format(keytimes,'.10f')};\n"
        print(index_points,keytimes)
  index_points = [i if i < length else length - 1 for i in range(length + 1)]
  for i in range(len(index_points)):
    index_points[i] = index_points[i] - 1
  keytimes=1
  path = f"M {path_points[index_points[0]][0]},{path_points[index_points[0]][1]}"
  for j in range(len(index_points)):
    path += f"L {path_points[index_points[j]][0]},{path_points[index_points[j]][1]}"
  values_result += f"{path};\n"
  keytimes_result += f"{keytimes};\n"
  values_result = values_result.rstrip(";\n")
  keytimes_result = keytimes_result.rstrip(";\n")
  return f'values="\n{values_result}"\n keyTimes="\n{keytimes_result}"'

svg=f"""\
<svg
    viewBox="0 0 120 60" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">

    <rect x="0" y="0" width="120" height="60" fill="#0ff" />
    <path
    d="M0,0L120,60"
    fill="none"
    stroke="#FFFFFF"
    stroke-width="10"
    stroke-linecap="round"
    stroke-linejoin="round">
    <animate
      attributeName="d"
      dur="10s"
      repeatCount="indefinite"
      calcMode="linear"
      {morphing(6)}
    />
    </path>
</svg>
"""
with open("next-loading.svg", mode="w") as f:
  f.write(svg)