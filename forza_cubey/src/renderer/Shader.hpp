#pragma once
#include <string>
#include <glm/glm.hpp>
#include <glad/glad.h>

namespace fc {
class Shader {
public:
    Shader() = default;
    ~Shader();
    void load(const std::string& vertPath, const std::string& fragPath);
    void use() const;
    void setBool(const std::string& n, bool v) const;
    void setInt(const std::string& n, int v) const;
    void setFloat(const std::string& n, float v) const;
    void setVec2(const std::string& n, const glm::vec2& v) const;
    void setVec3(const std::string& n, const glm::vec3& v) const;
    void setVec4(const std::string& n, const glm::vec4& v) const;
    void setMat4(const std::string& n, const glm::mat4& v) const;
    GLuint getID() const { return m_id; }
private:
    GLuint m_id = 0;
    std::string loadFile(const std::string& path);
    GLuint compileShader(const std::string& src, GLenum type);
    void linkProgram(GLuint v, GLuint f);
};
} // namespace fc
