#version 330

in vec3 position;
in vec2 texCoord;

uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

out vec2 fragTexCoord;

void main() {
    fragTexCoord = texCoord;
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}