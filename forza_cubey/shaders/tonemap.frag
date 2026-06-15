#version 410 core
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D scene;
uniform sampler2D bloomBlur;
uniform float exposure;
uniform bool bloom;

void main() {
    vec3 hdrColor = texture(scene, TexCoord).rgb;
    vec3 bloomColor = texture(bloomBlur, TexCoord).rgb;
    if (bloom) hdrColor += bloomColor;
    
    // Reinhard tone mapping
    vec3 mapped = hdrColor * exposure;
    mapped = mapped / (mapped + vec3(1.0));
    
    // Gamma correction
    mapped = pow(mapped, vec3(1.0 / 2.2));
    
    FragColor = vec4(mapped, 1.0);
}
