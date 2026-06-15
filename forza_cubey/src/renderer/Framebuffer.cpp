#include "Framebuffer.hpp"
#include <iostream>

namespace fc {

Framebuffer::Framebuffer(int w, int h, int flags) : m_w(w), m_h(h), m_flags(flags) {
    create();
}

Framebuffer::~Framebuffer() {
    destroy();
}

void Framebuffer::create() {
    glGenFramebuffers(1, &m_fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);

    if (m_flags & GBuffer) {
        // Position
        glGenTextures(1, &m_pos);
        glBindTexture(GL_TEXTURE_2D, m_pos);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_pos, 0);

        // Normal
        glGenTextures(1, &m_norm);
        glBindTexture(GL_TEXTURE_2D, m_norm);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, m_norm, 0);

        // Albedo
        glGenTextures(1, &m_albedo);
        glBindTexture(GL_TEXTURE_2D, m_albedo);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, m_albedo, 0);

        // Material (metallic, roughness, ao, emissive)
        glGenTextures(1, &m_material);
        glBindTexture(GL_TEXTURE_2D, m_material);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT3, GL_TEXTURE_2D, m_material, 0);

        GLuint attachments[] = {GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3};
        glDrawBuffers(4, attachments);
    } else if (m_flags & HDR) {
        glGenTextures(1, &m_color);
        glBindTexture(GL_TEXTURE_2D, m_color);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_color, 0);
    } else if (m_flags & DepthOnly) {
        // Depth-only (shadow map)
        glGenTextures(1, &m_depth);
        glBindTexture(GL_TEXTURE_2D, m_depth);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, m_w, m_h, 0, GL_DEPTH_COMPONENT, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
        float border[] = {1,1,1,1};
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, m_depth, 0);
        glDrawBuffer(GL_NONE);
        glReadBuffer(GL_NONE);
    } else {
        glGenTextures(1, &m_color);
        glBindTexture(GL_TEXTURE_2D, m_color);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_color, 0);
    }

    if ((m_flags & Depth) || (m_flags & GBuffer) || (m_flags & HDR)) {
        glGenRenderbuffers(1, &m_rbo);
        glBindRenderbuffer(GL_RENDERBUFFER, m_rbo);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, m_w, m_h);
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, m_rbo);
    }

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "[Framebuffer] Incomplete!\n";
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void Framebuffer::destroy() {
    if (m_fbo) glDeleteFramebuffers(1, &m_fbo);
    if (m_color) glDeleteTextures(1, &m_color);
    if (m_depth) glDeleteTextures(1, &m_depth);
    if (m_pos) glDeleteTextures(1, &m_pos);
    if (m_norm) glDeleteTextures(1, &m_norm);
    if (m_albedo) glDeleteTextures(1, &m_albedo);
    if (m_material) glDeleteTextures(1, &m_material);
    if (m_rbo) glDeleteRenderbuffers(1, &m_rbo);
}

void Framebuffer::bind() {
    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);
    glViewport(0, 0, m_w, m_h);
}

void Framebuffer::unbind() {
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void Framebuffer::bindTextures() {
    if (m_pos) {
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, m_pos);
    }
    if (m_norm) {
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, m_norm);
    }
    if (m_albedo) {
        glActiveTexture(GL_TEXTURE2);
        glBindTexture(GL_TEXTURE_2D, m_albedo);
    }
    if (m_material) {
        glActiveTexture(GL_TEXTURE3);
        glBindTexture(GL_TEXTURE_2D, m_material);
    }
}

void Framebuffer::resize(int w, int h) {
    destroy();
    m_w = w; m_h = h;
    create();
}

} // namespace fc
