#version 330

flat in vec3 vertexLightColor;
in vec2 fragTexCoords;

out vec4 fragColor;

uniform sampler2D samplerTex;

void main()
{
    vec4 textureColor = texture(samplerTex, fragTexCoords);
    fragColor = vec4(vertexLightColor, 1.0) * textureColor;
}