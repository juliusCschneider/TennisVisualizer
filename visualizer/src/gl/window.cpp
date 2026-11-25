#include "gl/window.hpp"

#include "core/world.hpp"
#include "gl/camera.hpp"
#include "gl/input.hpp"
#include "gl/shaders.hpp"
#include "gl/mesh.hpp"

#include <iostream>

GLFWwindow* window = nullptr;
int xformLoc;

int initGL(){
    if(!glfwInit()) return 0;

    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_RESIZABLE, GL_FALSE);
    glfwWindowHint(GLFW_SAMPLES, 4);

    window = glfwCreateWindow(WIDTH, HEIGHT, "Tennis Visualizer", nullptr, nullptr);
    if(!window){
        std::cerr << "Failed to create GLFW window\n";
        glfwTerminate();
        return 0;
    }
    glfwMakeContextCurrent(window);
    glfwSetKeyCallback(window, keyPressed);
    glfwSetMouseButtonCallback(window, mouseButton);
    glfwSetCursorPosCallback(window, mouseMove);
    glfwSetScrollCallback(window, scroll);

    if(!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)){
        std::cerr << "Failed to initialize GLAD\n";
        return 0;
    }

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_MULTISAMPLE);
    return 1;
}

void start(){
    GLuint program = createProgram(ASSET_DIR "shaders/v.glsl", ASSET_DIR "shaders/f.glsl");

    xformLoc = glGetUniformLocation(program, "xform");

    initWorld();

    while(!glfwWindowShouldClose(window)){
        glfwPollEvents();

        glClearColor(0.1f, 0.15f, 0.2f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glUseProgram(program);

        updateWorld();
        renderWorld();

        glfwSwapBuffers(window);
        updateCamera();
        updateInput();
    }
}

void dispose(){
    // TODO: Asset tracking and disposal (VAO + VBO dispose, etc)
    // Hehe this is never going to be done huh (memory leak galore)
    glfwTerminate();
}