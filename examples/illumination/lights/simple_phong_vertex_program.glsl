#version 330 core

layout (location = 0) in vec3 position;
//layout (location = 1) in vec3 color;
layout (location = 1) in vec3 normal;


out vec3 fragPosition;
out vec3 fragOriginalColor;
out vec3 fragNormal;

uniform vec3 u_color = vec3(1.0);
uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

void main()
{
    fragPosition = vec3(u_model * vec4(position, 1.0));
    fragOriginalColor = u_color;
    fragNormal = mat3(transpose(inverse(u_model))) * normal;  
    
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}