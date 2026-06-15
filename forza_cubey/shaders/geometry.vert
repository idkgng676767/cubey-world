#version 410 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in vec3 aTangent;
layout(location = 4) in vec3 aBitangent;
layout(location = 5) in vec4 aColor;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;
out vec4 Color;
out mat3 TBN;

uniform mat4 model;
uniform mat4 viewProj;

void main() {
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    gl_Position = viewProj * worldPos;
    
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    Color = aColor;
    
    vec3 T = normalize(mat3(model) * aTangent);
    vec3 B = normalize(mat3(model) * aBitangent);
    vec3 N = normalize(mat3(model) * aNormal);
    TBN = mat3(T, B, N);
}
