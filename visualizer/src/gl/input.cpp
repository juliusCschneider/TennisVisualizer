#include "input.hpp"

#include <glm/gtc/type_ptr.hpp>


bool mousePressed[3];
glm::vec2 pmouse, mouse;
double pmouseScroll, mouseScroll;
// TODO: Key pressed hashSet


void keyPressed(GLFWwindow* window, int key, int _scancode, int action, int mode){
    if(key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) glfwSetWindowShouldClose(window, GL_TRUE);
}

void mouseButton(GLFWwindow* window, int button, int action, int mods){
    bool newVal = action == GLFW_PRESS;
    if(button == GLFW_MOUSE_BUTTON_LEFT) mousePressed[0] = newVal;
    else if(button == GLFW_MOUSE_BUTTON_RIGHT) mousePressed[2] = newVal;
    else mousePressed[1] = newVal;
}

void mouseMove(GLFWwindow* window, double x, double y){
    mouse.x = x;
    mouse.y = y;
}

void scroll(GLFWwindow* window, double xoffset, double yoffset){
    mouseScroll += yoffset;
}

void updateInput(){
    pmouse.x = mouse.x;
    pmouse.y = mouse.y;
    pmouseScroll = mouseScroll;
}