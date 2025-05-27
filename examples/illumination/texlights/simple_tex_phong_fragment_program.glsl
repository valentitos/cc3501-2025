#version 330

out vec4 fragColor;

in vec3 fragPosition;
in vec2 fragTexCoords;
in vec3 fragNormal;

uniform vec3 lightPosition; 
uniform vec3 viewPosition;
uniform vec3 La;
uniform vec3 Ld;
uniform vec3 Ls;
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform int shininess;
uniform float constantAttenuation;
uniform float linearAttenuation;
uniform float quadraticAttenuation;

uniform sampler2D samplerTex;

void main()
{
    // ambient
    vec3 ambient = Ka * La;
    
    // diffuse
    // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
    vec3 normalizedNormal = normalize(fragNormal);
    vec3 toLight = lightPosition - fragPosition;
    vec3 lightDir = normalize(toLight);
    float diff = max(dot(normalizedNormal, lightDir), 0.0);
    vec3 diffuse = Kd * Ld * diff;
    
    // specular
    vec3 viewDir = normalize(viewPosition - fragPosition);
    vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = Ks * Ls * spec;

    // attenuation
    float distToLight = length(toLight);
    float attenuation = constantAttenuation
        + linearAttenuation * distToLight
        + quadraticAttenuation * distToLight * distToLight;
        
    vec4 fragOriginalColor = texture(samplerTex, fragTexCoords);

    vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor.rgb;
    fragColor = vec4(result, 1.0);
}