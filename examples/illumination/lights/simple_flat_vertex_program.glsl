#version 330

in vec3 position;
in vec3 normal;

flat out vec4 fragColor;

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
    vec3 vertexPos = vec3(u_model * vec4(position, 1.0));
    gl_Position = projection * view * u_model * vec4(position, 1.0f);

    mat3 normalMatrix = mat3(transpose(inverse(u_model)));
    vec3 qnormal = normalize(normalMatrix * normal);
    vec3 norm = normalize(qnormal);

    // ambient
    vec3 ambient = Ka * La;
    
    // diffuse 
    vec3 toLight = lightPosition - vertexPos;
    vec3 lightDir = normalize(toLight);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = Kd * Ld * diff;
    
    // specular
    vec3 viewDir = normalize(viewPosition - vertexPos);
    vec3 reflectDir = reflect(-lightDir, norm);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = Ks * Ls * spec;

    // attenuation
    float distToLight = length(toLight);
    float attenuation = constantAttenuation
        + linearAttenuation * distToLight
        + quadraticAttenuation * distToLight * distToLight;
    
    vec3 result = (ambient + ((diffuse + specular) / attenuation)) * u_color;
    //vertexColor = vec4(result, 1.0);
    fragColor = vec4(result, 1.0);
}