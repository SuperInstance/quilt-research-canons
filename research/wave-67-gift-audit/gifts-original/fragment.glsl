#version 300 es
precision highp float;
precision highp usampler2D;
in vec2 v_texCoord;
in vec2 v_charCoord;
uniform usampler2D u_packedStateTexture;
uniform sampler2D u_dynamicFontAtlas;
uniform float u_time;
// Dynamic Workspace Uniform Parameters
uniform int u_renderDecompositionZone; // 1 = Visible, 0 = Collapsed / Hidden
out vec4 fragColor;

void main() {
    uvec4 rawCell = texture(u_packedStateTexture, v_texCoord);
    uint packedWord = rawCell.r;

    uint glyphIndex  = packedWord & 0xFFu;
    uint colorIndex  = (packedWord >> 8u) & 0xFFu;
    uint weightVal   = (packedWord >> 16u) & 0xFFu;
    uint buzzChannel = (packedWord >> 28u) & 0x0Fu;

    // Evaluate layout boundaries based on current operational visibility toggle states
    bool isResonanceZone = (v_texCoord.y > 0.833);
    vec2 dynamicCoords = v_texCoord;
    float floatBuzz = float(buzzChannel) / 15.0;

    // Only apply the high-frequency ripple if the interface switch is active
    if (u_renderDecompositionZone == 1 && isResonanceZone && buzzChannel > 0u) {
        dynamicCoords.x += sin(v_texCoord.y * 120.0 + u_time * 24.0) * (floatBuzz * 0.015);
    }

    float atlasCells = 32.0;
    vec2 fontLookupCoord = vec2((v_charCoord.x + float(glyphIndex % 32u)) / atlasCells, (v_charCoord.y + float(glyphIndex / 32u)) / atlasCells);
    float glyphMask = texture(u_dynamicFontAtlas, fontLookupCoord).r;

    vec3 pixelColor = vec3(
        float(colorIndex & 0x03u) * 0.33,
        float((colorIndex >> 2u) & 0x03u) * 0.33,
        float((colorIndex >> 4u) & 0x03u) * 0.33
    ) * (float(weightVal) / 255.0);

    // Dynamic Color Pass routing
    if (u_renderDecompositionZone == 1 && isResonanceZone) {
        vec3 decompositionBlue = vec3(0.0, 0.38, 0.65);
        pixelColor = mix(pixelColor, decompositionBlue * (floatUnpackedBuzz + 0.3), 0.7);
    } else if (u_renderDecompositionZone == 0 && isResonanceZone) {
        // If hidden, collapse the color signature down to match the standard grid baseline format
        pixelColor = vec3(0.05, 0.05, 0.06);
    }

    fragColor = vec4(pixelColor * glyphMask, 1.0);
}
