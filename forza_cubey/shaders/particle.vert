#version 410 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
out float Life;

uniform mat4 viewProj;
uniform vec3 position;
uniform float size;
uniform float life;
uniform float maxLife;

void main() {
    vec3 worldPos = position + aPos * size;
    gl_Position = viewProj * vec4(worldPos, 1.0);
    TexCoord = aTexCoord;
    Life = life / maxLife;
}
