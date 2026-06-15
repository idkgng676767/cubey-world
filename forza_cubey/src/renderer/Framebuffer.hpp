#pragma once
#include <glad/glad.h>

namespace fc {
class Framebuffer {
public:
    enum Flags { Color = 1, Depth = 2, GBuffer = 4, HDR = 8, DepthOnly = 16 };
    Framebuffer(int w, int h, int flags);
    ~Framebuffer();
    void bind();
    void unbind();
    void bindTextures();
    void resize(int w, int h);
    GLuint getColorTexture() const { return m_color; }
    GLuint getDepthTexture() const { return m_depth; }
    GLuint getPositionTexture() const { return m_pos; }
    GLuint getNormalTexture() const { return m_norm; }
    GLuint getAlbedoTexture() const { return m_albedo; }
private:
    GLuint m_fbo = 0;
    int m_w, m_h, m_flags;
    GLuint m_color = 0, m_depth = 0, m_pos = 0, m_norm = 0, m_albedo = 0, m_material = 0, m_rbo = 0;
    void create();
    void destroy();
};
} // namespace fc
