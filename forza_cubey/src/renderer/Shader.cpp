#include "Shader.hpp"
#include <fstream>
#include <sstream>
#include <iostream>

namespace fc {

Shader::~Shader() { if (m_id) glDeleteProgram(m_id); }

void Shader::load(const std::string& vertPath, const std::string& fragPath) {
    auto vertSrc = loadFile(vertPath);
    auto fragSrc = loadFile(fragPath);
    GLuint vs = compileShader(vertSrc, GL_VERTEX_SHADER);
    GLuint fs = compileShader(fragSrc, GL_FRAGMENT_SHADER);
    linkProgram(vs, fs);
    glDeleteShader(vs);
    glDeleteShader(fs);
}

std::string Shader::loadFile(const std::string& path) {
    std::ifstream f(path);
    if (!f.is_open()) {
        std::cerr << "[Shader] Missing: " << path << "\n";
        return "";
    }
    std::stringstream b;
    b << f.rdbuf();
    return b.str();
}

GLuint Shader::compileShader(const std::string& src, GLenum type) {
    GLuint s = glCreateShader(type);
    const char* c = src.c_str();
    glShaderSource(s, 1, &c, nullptr);
    glCompileShader(s);
    GLint ok;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[512];
        glGetShaderInfoLog(s, 512, nullptr, log);
        std::cerr << "[Shader] Compile error:\n" << log << "\n";
    }
    return s;
}

void Shader::linkProgram(GLuint v, GLuint f) {
    m_id = glCreateProgram();
    glAttachShader(m_id, v);
    glAttachShader(m_id, f);
    glLinkProgram(m_id);
    GLint ok;
    glGetProgramiv(m_id, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[512];
        glGetProgramInfoLog(m_id, 512, nullptr, log);
        std::cerr << "[Shader] Link error:\n" << log << "\n";
    }
}

void Shader::use() const { glUseProgram(m_id); }
void Shader::setBool(const std::string& n, bool v) const { glUniform1i(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setInt(const std::string& n, int v) const { glUniform1i(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setFloat(const std::string& n, float v) const { glUniform1f(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setVec2(const std::string& n, const glm::vec2& v) const { glUniform2fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setVec3(const std::string& n, const glm::vec3& v) const { glUniform3fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setVec4(const std::string& n, const glm::vec4& v) const { glUniform4fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setMat4(const std::string& n, const glm::mat4& v) const { glUniformMatrix4fv(glGetUniformLocation(m_id, n.c_str()), 1, GL_FALSE, &v[0][0]); }

} // namespace fc
