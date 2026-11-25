#pragma once

#include <glad/glad.h>
#include <GLFW/glfw3.h>

const GLuint WIDTH = 800, HEIGHT = 600;

extern GLFWwindow* window;
extern int xformLoc;

int initGL();
void keyPressed(GLFWwindow* window, int key, int scancode, int action, int mode);

void start();
void dispose();