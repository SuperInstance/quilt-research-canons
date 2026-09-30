// Locate the uniform variable slot within your WebGL controller initialization phase
const decompositionZoneToggleLoc = gl.getUniformLocation(program, "u_renderDecompositionZone");
let isPanelVisible = 1; // Default state: 1 = Active visibility, 0 = Collapsed/Hidden

function bindDecompositionPanelToggle(isVisible) {
    isPanelVisible = isVisible ? 1 : 0;

    // Inject the flag directly into the active GPU execution state
    gl.useProgram(program);
    gl.uniform1i(decompositionZoneToggleLoc, isPanelVisible);

    console.log(`[GPU Core] Decomposition panel visibility updated: ${isPanelVisible}`);
}

// Attach event listener straight to your high-density dashboard control button
document.getElementById("btn-toggle-resonance-panel").addEventListener("click", () => {
    const activeState = document.getElementById("toggle-admin-filter").checked; // Recycles existing framework checks
    bindDecompositionPanelToggle(!isPanelVisible);
});
