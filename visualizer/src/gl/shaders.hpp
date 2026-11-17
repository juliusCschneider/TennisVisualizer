#pragma once

#include <glad/glad.h>

GLuint compileShader(GLenum type, const char *path);
GLuint createProgram(const char *vsPath, const char *fsPath);