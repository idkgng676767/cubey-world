#version 410 core
in vec2 TexCoord;
in float Life;

out vec4 FragColor;

uniform vec3 color;
uniform float opacity;

void main() {
    float dist = length(TexCoord - vec2(0.5));
    float alpha = smoothstep(0.5, 0.0, dist) * opacity * Life;
    FragColor = vec4(color, alpha);
}
