#include "camera.hpp"

#include "gl/window.hpp"

glm::vec3 eye, center;

glm::mat4 cameraProj(){
    return glm::perspective(glm::radians(45.0f), (float)WIDTH / HEIGHT, 0.1f, 100.0f); // Maybe creating a new matrix every time is inefficient? i dunno, I've only done java OpenGL not C++
}

glm::mat4 cameraView(){
    return glm::lookAt(eye, center, glm::vec3(0.0f, 1.0f, 0.0f));
}

void initCamera(){
    eye = glm::vec3(0.0f, 18.0f, 28.0f);
    center = glm::vec3(0.0f, 0.0f, 0.0f);
}

void updateCamera(){

    // TODO: Rotate center around eye and translate eye
}