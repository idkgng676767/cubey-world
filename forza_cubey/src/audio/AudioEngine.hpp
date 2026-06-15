#pragma once
#include <string>
#include <vector>
#include <glm/glm.hpp>

namespace fc {
struct AudioSource {
    unsigned int id = 0;
    glm::vec3 position;
    float volume = 1.0f, pitch = 1.0f;
    bool loop = false, is3D = true;
    float minDist = 1.0f, maxDist = 100.0f;
};
class AudioEngine {
public:
    AudioEngine();
    ~AudioEngine();
    bool initialize();
    void shutdown();
    void update();
    int loadSound(const std::string& path);
    void playSound(int id, const glm::vec3& pos = glm::vec3(0));
    void playMusic(const std::string& path, float vol = 0.5f);
    void stopMusic();
    void setListener(const glm::vec3& pos, const glm::vec3& fwd, const glm::vec3& up);
    void setMasterVolume(float v);
private:
    void* m_device = nullptr;
    std::vector<void*> m_sounds;
    void* m_music = nullptr;
    float m_masterVol = 1.0f;
};
} // namespace fc
