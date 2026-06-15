#version 410 core
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D gAlbedo;
uniform sampler2D gMaterial;

uniform vec3 lightDir;
uniform vec3 lightColor;
uniform float lightIntensity;
uniform vec3 cameraPos;
uniform float exposure;

void main() {
    vec3 fragPos = texture(gPosition, TexCoord).rgb;
    vec3 normal = normalize(texture(gNormal, TexCoord).rgb);
    vec4 albedo = texture(gAlbedo, TexCoord);
    vec4 material = texture(gMaterial, TexCoord);
    
    float metallic = material.r;
    float roughness = material.g;
    float ao = material.b;
    
    // Directional light
    vec3 L = normalize(-lightDir);
    vec3 V = normalize(cameraPos - fragPos);
    vec3 H = normalize(L + V);
    
    float NdotL = max(dot(normal, L), 0.0);
    float NdotV = max(dot(normal, V), 0.0);
    float NdotH = max(dot(normal, H), 0.0);
    
    // Diffuse
    vec3 diffuse = albedo.rgb * NdotL * lightColor * lightIntensity;
    
    // Specular (Blinn-Phong)
    float specPower = mix(8.0, 128.0, 1.0 - roughness);
    float spec = pow(NdotH, specPower) * metallic;
    vec3 specular = vec3(spec) * lightColor * lightIntensity;
    
    // Ambient
    vec3 ambient = albedo.rgb * 0.1 * ao;
    
    vec3 color = ambient + diffuse + specular;
    
    // Tone mapping
    color = color * exposure;
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0 / 2.2));
    
    FragColor = vec4(color, albedo.a);
}
