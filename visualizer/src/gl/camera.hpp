#pragma once

#include <glm/gtc/type_ptr.hpp>

const float ROT_SENSITIVITY = 0.005f, ZOOM_SENSITIVITY = 2.0f, PAN_SENSITIVITY = 0.001f;

glm::mat4 cameraProj();
glm::mat4 cameraView();

void initCamera();
void updateCamera();
