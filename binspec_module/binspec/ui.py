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