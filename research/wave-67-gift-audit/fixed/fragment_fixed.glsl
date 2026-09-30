#version 300 es
precision highp float;
precision highp usampler2D;
in vec2 v_texCoord;
in vec2 v_charCoord;
uniform usampler2D u_packedStateTexture;
uniform sampler2D u_dynamicFontAtlas;
uniform float u_time;
uniform int u_renderDecompositionZone; // 1 = Visible, 0 = Collapsed / Hidden
out vec4 fragColor;

// the ripple, declared BEFORE main (GLSL has no forward refs) so its output is
// actually consumed by the sampler. Honest limitation documented: per-cell buzz
// wobble is impossible pre-fetch from the SAME texture (chicken-and-egg) — it
// needs a previous-frame texture or vertex-stage displacement. The wobble here
// is driven by the zone boundary itself.
vec2 dynamicCoordsFor(vec2 uv, int zoneVisible, float time) {
    vec2 dc = uv;
    if (zoneVisible == 1 && uv.y > 0.833) {
        dc.x += sin(uv.y * 120.0 + time * 24.0) * 0.015;
    }
    return dc;
}

void main() {
    // FIXED vs the gift: (1) floatUnpackedBuzz was never declared -> floatBuzz;
    // (2) the gift's ripple wrote dynamicCoords but the sampler read v_texCoord
    // (dead code) — here the sampler follows dynamicCoords.
    uvec4 rawCell = texture(u_packedStateTexture, dynamicCoordsFor(v_texCoord, u_renderDecompositionZone, u_time));
    uint packedWord = rawCell.r;

    uint glyphIndex  = packedWord & 0xFFu;
    uint colorIndex  = (packedWord >> 8u) & 0xFFu;
    uint weightVal   = (packedWord >> 16u) & 0xFFu;
    uint buzzChannel = (packedWord >> 28u) & 0x0Fu;

    bool isResonanceZone = (v_texCoord.y > 0.833);
    float floatBuzz = float(buzzChannel) / 15.0;

    float atlasCells = 32.0;
    vec2 fontLookupCoord = vec2((v_charCoord.x + float(glyphIndex % 32u)) / atlasCells,
                                (v_charCoord.y + float(glyphIndex / 32u)) / atlasCells);
    float glyphMask = texture(u_dynamicFontAtlas, fontLookupCoord).r;

    vec3 pixelColor = vec3(
        float(colorIndex & 0x03u) * 0.33,
        float((colorIndex >> 2u) & 0x03u) * 0.33,
        float((colorIndex >> 4u) & 0x03u) * 0.33
    ) * (float(weightVal) / 255.0);

    if (u_renderDecompositionZone == 1 && isResonanceZone) {
        vec3 decompositionBlue = vec3(0.0, 0.38, 0.65);
        pixelColor = mix(pixelColor, decompositionBlue * (floatBuzz + 0.3), 0.7);
    } else if (u_renderDecompositionZone == 0 && isResonanceZone) {
        pixelColor = vec3(0.05, 0.05, 0.06);
    }

    fragColor = vec4(pixelColor * glyphMask, 1.0);
}
