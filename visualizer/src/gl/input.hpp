#pragma once

#include <glm/gtc/type_ptr.hpp>

#include <glad/glad.h>
#include <glm/glm.hpp>
#include <GLFW/glfw3.h>

extern bool mousePressed[3];
extern glm::vec2 pmouse, mouse;
extern double pmouseScroll, mouseScroll;

void keyPressed(GLFWwindow* window, int key, int _scancode, int action, int mode);
void mouseButton(GLFWwindow* window, int button, int action, int mods);
void mouseMove(GLFWwindow* window, double x, double y);
void scroll(GLFWwindow* window, double xoffset, double yoffset);
void updateInput(); // Called AT THE END of the update loop (for pmouse, pscroll, etc)