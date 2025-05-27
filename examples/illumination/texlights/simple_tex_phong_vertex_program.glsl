#version 330

in vec3 position;
in vec3 normal;
in vec2 texCoord;

out vec3 fragPosition;
out vec2 fragTexCoords;
out vec3 fragNormal;

uniform vec3 u_color = vec3(1.0);
uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

void main()
{
    fragPosition = vec3(u_model * vec4(position, 1.0));
    fragTexCoords = texCoord;
    fragNormal = mat3(transpose(inverse(u_model))) * normal;  
    
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}