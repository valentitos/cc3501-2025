#version 330

in vec2 fragTexCoord;

out vec4 outColor;

uniform sampler2D u_texture;

void main() {
    outColor =  texture(u_texture, fragTexCoord);
    if(outColor.a < 0.1)
        discard;
}