#include <fstream>
#include <iostream>
#include <sstream>

#include <glad/glad.h>
#include <string>

GLuint compileShader(GLenum type, const char* path){
    std::ifstream file(path);
    std::stringstream ss;
    ss << file.rdbuf();
    std::string src = ss.str();
    const char* code = src.c_str();

    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &code, nullptr);
    glCompileShader(shader);
    return shader;
}

GLuint createProgram(const char* vsPath, const char* fsPath){
    GLuint vs = compileShader(GL_VERTEX_SHADER, vsPath);
    GLuint fs = compileShader(GL_FRAGMENT_SHADER, fsPath);
    GLuint prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, fs);
    glLinkProgram(prog);
    glDeleteShader(vs);
    glDeleteShader(fs);
    return prog;
}