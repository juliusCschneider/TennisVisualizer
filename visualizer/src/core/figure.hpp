#pragma once

#include <glad/glad.h>
#include <glm/gtc/type_ptr.hpp>

struct Figure{
    GLuint vao, vbo;

    bool rightHanded;

    glm::vec3 lFoot, lKnee, lTorso, lShoulder, lElbow, lHand;
    glm::vec3 rFoot, rKnee, rTorso, rShoulder, rElbow, rHand;
    glm::vec3 head, racket;

    void init();
    void draw();
};

extern Figure player;