#include "gl/window.hpp"

#include "gl/camera.hpp"
#include "gl/input.hpp"
#include "gl/shaders.hpp"
#include "gl/mesh.hpp"

#include <glm/gtc/type_ptr.hpp>
#include <iostream>

GLFWwindow* window = nullptr;

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

    Mesh court, ball; // TODO: Dynamic loading system? Or at least a global vec to track all of them somewhere
    court.load(ASSET_DIR "models/Court.obj");
    ball.load(ASSET_DIR "models/Ball.obj");

    GLint xformLoc = glGetUniformLocation(program, "xform");
    while(!glfwWindowShouldClose(window)){
        glfwPollEvents();

        glClearColor(0.15f, 0.18f, 0.22f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glm::mat4 proj = cameraProj();
        glm::mat4 view = cameraView();


        // TMP

        // TODO: Drawf or smtg
        glm::mat4 courtModel = glm::rotate(glm::mat4(1.0f), 0.0f, glm::vec3(0.0f, 1.0f, 0.0f));

        //Tmp render system
        glUseProgram(program);

        glUniformMatrix4fv(xformLoc, 1, GL_FALSE, glm::value_ptr(proj * view * courtModel));
        glBindVertexArray(court.vao);
        glDrawArrays(GL_TRIANGLES, 0, (GLsizei)court.n);

        // END TMP

        // std::cout << mouseScroll - pmouseScroll << std::endl;

        glfwSwapBuffers(window);
        updateCamera();
        updateInput();
    }
}

void dispose(){
    // TODO: Asset tracking and disposal (VAO + VBO dispose, etc)
    glfwTerminate();
}