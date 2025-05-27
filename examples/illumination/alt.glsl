#version 330

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

out vec3 vertexColor;

uniform vec3 u_color = vec3(1.0);
uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

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

void main()
{
    // --- Transformaciones básicas ---
    mat3 normalMatrix = mat3(transpose(inverse(u_model)));
    vec3 qnormal = normalize(normalMatrix * normal); // rotamos la normal correctamente

    vec3 fragPos = vec3(u_model * vec4(position, 1.0)); // posición del vértice en el mundo

    // --- Cálculo de iluminación Gouraud (Phong model de iluminación) ---
    // Componente ambiental

    vec3 ambient = Ka * La;

    // Componente difusa
    vec3 lightDir = normalize(lightPosition - fragPos);
    float diff = max(dot(qnormal, lightDir), 0.0);
    vec3 diffuse = Kd * Ld * diff;


    // Componente especular
    vec3 viewDir = normalize(viewPosition - fragPos);
    vec3 reflectDir = reflect(-lightDir, qnormal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = Ks * Ls * spec;

    // attenuation
    float distToLight = length(lightPosition - fragPos);
    float attenuation = constantAttenuation
        + linearAttenuation * distToLight
        + quadraticAttenuation * distToLight * distToLight;
    
    vec3 result = (ambient + ((diffuse + specular) / attenuation)) * u_color;
    vertexColor = result;


    // Transformar vértice
    gl_Position = projection * view * u_model * vec4(fragPos, 1.0);
}