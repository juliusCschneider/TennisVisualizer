#include "camera.hpp"

// Maybe I should have made this an object so we can have multiple cameras ? Eh it's whatever

#include "gl/input.hpp"
#include "gl/window.hpp"

float pitch, yaw, distance;
glm::vec3 camera, center;

glm::mat4 cameraProj(){
    return glm::perspective(glm::radians(45.0f), (float)WIDTH / HEIGHT, 0.1f, 100.0f); // Maybe creating a new matrix every time is inefficient? i dunno, I've only done java OpenGL not C++
}

glm::mat4 cameraView(){
    return glm::lookAt(camera, center, glm::vec3(0.0f, 1.0f, 0.0f));
}

void calcCamera(){
    const float maxPitch = 1.55334f, maxDistance = 70.0f, minDistance = 1.0f;;
    distance = glm::clamp(distance, minDistance, maxDistance);
    pitch = glm::clamp(pitch, -maxPitch, maxPitch);
    float cosPitch = cos(pitch);
    glm::vec3 offset(
        distance * cosPitch * cos(yaw),
        distance * sin(pitch),
        distance * cosPitch * sin(yaw)
    );
    camera = center + offset;
}

void initCamera(){
    pitch = 0.5f;
    yaw = 0.0f;
    distance = 30.0f;
    center = glm::vec3(0.0f, 0.0f, 0.0f);
    calcCamera();
}

void updateCamera(){
    distance += (mouseScroll - pmouseScroll) * -ZOOM_SENSITIVITY;
    if(mousePressed[2]){
        yaw += (mouse.x - pmouse.x) * ROT_SENSITIVITY;
        pitch += (mouse.y - pmouse.y) * ROT_SENSITIVITY;
    }
    if(mousePressed[1]) initCamera();
    if(mousePressed[0]){
        glm::vec3 forward(-cos(yaw), 0.0f, -sin(yaw));
        glm::vec3 right(-sin(yaw), 0.0f, cos(yaw));
        center += (right * (mouse.x - pmouse.x) + forward * (mouse.y - pmouse.y)) * PAN_SENSITIVITY * distance;
    }
    calcCamera();
}