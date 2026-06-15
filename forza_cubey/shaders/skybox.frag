#version 410 core
in vec3 TexCoords;

out vec4 FragColor;

uniform vec3 topColor;
uniform vec3 bottomColor;
uniform float offset;
uniform float exponent;

void main() {
    float h = normalize(TexCoords + offset).y;
    float t = max(pow(max(h, 0.0), exponent), 0.0);
    vec3 color = mix(bottomColor, topColor, t);
    FragColor = vec4(color, 1.0);
}
