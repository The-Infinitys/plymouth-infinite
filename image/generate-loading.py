"""
<svg
    viewBox="0 0 120 60" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <linearGradient id="rainbow-gradient" x1="0%" y1="0%" x2="100%" y2="0%" spreadMethod="repeat">
      <animate attributeName="x1" dur="20s" from="-100%" to="100%" repeatCount="indefinite" />
      <animate attributeName="x2" dur="20s" from="0%" to="200%" repeatCount="indefinite" />
      <stop stop-color="#00ffff" offset="0" />
      <stop stop-color="#0000ff" offset="0.167" />
      <stop stop-color="#ff00ff" offset="0.333" />
      <stop stop-color="#ff0000" offset="0.5" />
      <stop stop-color="#ffff00" offset="0.667" />
      <stop stop-color="#00ff00" offset="0.833" />
      <stop stop-color="#00ffff" offset="1" />
    </linearGradient>
  </defs>
  <path
    id="path"
    d="
    M 10,30
    l 10,20
    h 30
    l 20,-40
    h 30
    l 10,20
    l -10,20
    h -30
    l -20,-40
    h -30
    z
    "
    fill="none"
    stroke="url(#rainbow-gradient)"
    stroke-width="10"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
  <circle r="5" fill="red">
    <animateMotion repeatCount="indefinite" dur="5s">
      <mpath href="#path" />
    </animateMotion>
  </circle>
</svg>
"""

head="""<svg
    viewBox="0 0 120 60" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">
    <path
    id="path"
    d="
    M 10,30
    l 10,20
    h 30
    l 20,-40
    h 30
    l 10,20
    l -10,20
    h -30
    l -20,-40
    h -30
    z
    "
    fill="none"
    stroke="none"
  />
  <rect x="0" y="0" width="120" height="60" fill="#000" stroke="none"/>
"""
foot="""</svg>"""

length = 10
per=0.5
r=5
def circle(begin:float) -> str:
    return f"""
    <circle x="{120+2*r}" y="{60+2*r}" r="{r}" fill="#fff" stroke="none">
    <animateMotion repeatCount="indefinite" dur="{str(length)}s" begin="{str(begin)}s">
      <mpath href="#path" />
    </animateMotion>
  </circle>
    """

def generate_loading(level=100) -> str:
    result = head
    for i in range(level):
        result += circle(i*length/level*per)
    result += foot
    return result
  
with open("loading.svg", "w") as f:
    f.write(generate_loading())
