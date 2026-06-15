#version 410 core
in vec2 TexCoord;

out float FragColor;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D texNoise;

uniform vec3 samples[64];
uniform mat4 projection;
uniform vec2 noiseScale;

void main() {
    vec3 fragPos = texture(gPosition, TexCoord).xyz;
    vec3 normal = normalize(texture(gNormal, TexCoord).xyz);
    vec3 randomVec = normalize(texture(texNoise, TexCoord * noiseScale).xyz);
    
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);
    
    float occlusion = 0.0;
    float radius = 0.5;
    float bias = 0.025;
    
    for (int i = 0; i < 64; ++i) {
        vec3 samplePos = TBN * samples[i];
        samplePos = fragPos + samplePos * radius;
        
        vec4 offset = vec4(samplePos, 1.0);
        offset = projection * offset;
        offset.xyz = offset.xyz / offset.w * 0.5 + 0.5;
        
        float sampleDepth = texture(gPosition, offset.xy).z;
        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fragPos.z - sampleDepth));
        occlusion += (sampleDepth >= samplePos.z + bias ? 1.0 : 0.0) * rangeCheck;
    }
    
    FragColor = 1.0 - (occlusion / 64.0);
}
