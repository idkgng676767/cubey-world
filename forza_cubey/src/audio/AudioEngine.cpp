#include "AudioEngine.hpp"
#include <iostream>

namespace fc {

AudioEngine::AudioEngine() = default;
AudioEngine::~AudioEngine() { shutdown(); }

bool AudioEngine::initialize() {
    std::cout << "[Audio] Engine initialized (stub - integrate OpenAL/miniaudio here)\n";
    return true;
}

void AudioEngine::shutdown() {
    std::cout << "[Audio] Engine shutdown\n";
}

void AudioEngine::update() {
    // Update 3D audio positions
}

int AudioEngine::loadSound(const std::string& path) {
    m_sounds.push_back(nullptr);
    return (int)m_sounds.size() - 1;
}

void AudioEngine::playSound(int id, const glm::vec3& pos) {
    // Play sound at position
}

void AudioEngine::playMusic(const std::string& path, float vol) {
    std::cout << "[Audio] Playing music: " << path << " at volume " << vol << "\n";
}

void AudioEngine::stopMusic() {
    // Stop music
}

void AudioEngine::setListener(const glm::vec3& pos, const glm::vec3& fwd, const glm::vec3& up) {
    // Update listener position/orientation
}

void AudioEngine::setMasterVolume(float v) {
    m_masterVol = v;
}

} // namespace fc
