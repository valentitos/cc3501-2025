#version 330

in vec3 position;
in vec2 texCoord;

uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);
uniform float time = 0.0;
uniform float frames = 1.0;
uniform float speed = 1.0;

out vec2 fragTexCoord;

void main() {
    fragTexCoord = vec2((texCoord.x+ floor(time*speed))/frames, texCoord.y);
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}