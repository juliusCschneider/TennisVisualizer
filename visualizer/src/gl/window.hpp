#pragma once

#include <glad/glad.h>
#include <GLFW/glfw3.h>

void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode);

int init();
void start();

const GLuint WIDTH = 800, HEIGHT = 600;

extern GLFWwindow* window;