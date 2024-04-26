html_template = """
<html>

<style>
    #binary-view {
        font-size: 0;
    }
    #binary-view span {
        display: inline-block;
        user-select: none;
        font-size: 24px;
        letter-spacing: 2px;
        padding-left: 1px;
        padding-right: 1px;
    }
    #binary-view span:hover {
        outline: 2px cyan solid;
    }
    #spec-info {
        visibility: hidden;
        background-color: gray;
        position: absolute;
        width: 200px;
        height: 100px;
    }
</style>

<head>
    <script>
        window.spec_history = [ /*INSERT_SPEC_HISTORY*/ ]
        window.binary_string = "/*INSERT_BINARY_STRING*/"
    </script>

    <script>
        function showSpecInfo(position, spec) {
            let info = document.getElementById("spec-info")
            let label = document.getElementById("spec-info-label")
            let bit_length = document.getElementById("spec-info-bit-length")

            label.innerHTML = spec.label
            bit_length.innerHTML = spec.bit_length

            info.style = `left: ${position.x}; right: ${position.y}; visibility: visible !important;`
        }
    </script>

    <script>
        window.onload = function() {
            let offset = 0

            colors = [
                [220, 220, 220],  // Light gray
                [173, 216, 230],  // Pale blue
                [152, 255, 152],  // Mint green
                [245, 245, 220],  // Beige
                [255, 255, 204],  // Light yellow
                [255, 182, 193],  // Soft pink
                [230, 230, 250],  // Lavender
                [255, 218, 185],  // Peach
                [175, 238, 238],  // Light teal
                [255, 253, 208],  // Cream
                [255, 160, 122],  // Light salmon
                [135, 206, 235],  // Sky blue
                [144, 238, 144],  // Light green
                [230, 230, 250],  // Light lavender
                [238, 232, 170],  // Pale goldenrod
                [240, 128, 128],  // Light coral
                [176, 224, 230],  // Powder blue
                [224, 255, 255],  // Light cyan
                [240, 255, 240],  // Honeydew
                [119, 136, 153],  // Light slate gray
                [240, 248, 255],  // Alice blue
                [176, 196, 222],  // Light steel blue
                [135, 206, 250],  // Light sky blue
                [175, 238, 238],  // Pale turquoise
                [250, 250, 210],  // Light goldenrod yellow
                [255, 182, 193],  // Light pink
                [173, 216, 230],  // Light blue
                [204, 153, 204],  // Light grayish magenta
                [224, 255, 255],  // Light grayish cyan
                [221, 160, 221],  // Light grayish plum
            ]
            let colorIndex = 0

            window.spec_history.forEach(spec => {
                let bits = window.binary_string.substring(offset, spec.bit_length)
                let span = document.createElement("span")
                let color = colors[colorIndex]
                span.style = `background-color: rgb(${color[0]}, ${color[1]}, ${color[2]})`
                span.innerHTML = bits

                span.onclick = function(e) {
                    showSpecInfo({ x: e.clientX, y: e.clientY }, spec)
                }

                document.getElementById("binary-view").appendChild(span)

                colorIndex += 1

                if (colorIndex >= colors.length) {
                    colorIndex = 0
                }
            });
        }
    </script>
</head>

<body>
    <div id="binary-view"></div>
    <div id="spec-info">
        <button onclick="document.getElementById('spec-info').style = ''">X</button>
        <br>
        <span>Label:</span>
        <span id="spec-info-label">LABEL</span>
        <br>
        <span>Bit Length:</span>
        <span id="spec-info-bit-length">BIT LENGTH</span>
    </div>
</body>

</html>
"""

from ..spec import Specification

def show(spec: Specification, data: bytes, *, port: int=55791):
    """Show a webpage which visualizes the specification. This method depends on the given :class:`Specification`'s history tracking to be enabled. Addtionally requires Flask to be installed.
    
    :param stream: A bytes object used to display the specification. In most cases, this is sourced from the bytes stream that was initially passed to the specification.
    :param port: The local port to host the webpage on."""

    if not spec.is_history_enabled():
        raise ValueError("Expected a Specification with history enabled.")

    from flask import Flask
    import webbrowser

    app = Flask("BinSpec")

    def index():
        json_spec_template = "{ bit_length: %s, label: '%s' }"
        spec_history = ",".join(map(lambda s: json_spec_template % (s[0].get_bit_length(), s[2]), spec.get_history()))
        binary_string = "".join(map(lambda b: format(b, '#010b'), stream.read()))

        from .ui import html_template

        html = html_template.replace("/*INSERT_SPEC_HISTORY*/", spec_history).replace("/*INSERT_BINARY_STRING*/", binary_string)
          
        return html

    app.add_url_rule("/", view_func=index)

    webbrowser.open_new_tab(f"http://localhost:{port}")
    app.run(port=port)