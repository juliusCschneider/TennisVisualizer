#pragma once

#include <glm/gtc/type_ptr.hpp>

glm::mat4 cameraProj();
glm::mat4 cameraView();

void initCamera();
void updateCamera(); // Called when mouse moving and stuff
