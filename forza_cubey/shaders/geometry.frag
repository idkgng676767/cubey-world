#version 410 core
layout(location = 0) out vec4 gPosition;
layout(location = 1) out vec4 gNormal;
layout(location = 2) out vec4 gAlbedo;
layout(location = 3) out vec4 gMaterial;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in vec4 Color;
in mat3 TBN;

uniform vec3 cameraPos;
uniform float metallic;
uniform float roughness;
uniform float ao;

void main() {
    gPosition = vec4(FragPos, 1.0);
    gNormal = vec4(normalize(Normal), 1.0);
    gAlbedo = Color;
    gMaterial = vec4(metallic, roughness, ao, 1.0);
}
