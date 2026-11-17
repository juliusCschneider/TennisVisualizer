#include "gl/window.hpp"
#include "gl/shaders.hpp"
#include "gl/mesh.hpp"

#include <glm/gtc/type_ptr.hpp>

int main(){
    if (!init()) return -1;

    GLuint program = createProgram(ASSET_DIR "shaders/v.glsl", ASSET_DIR "shaders/f.glsl");

    Mesh court;
    court.load(ASSET_DIR "models/Court.obj");

    GLint xformLoc = glGetUniformLocation(program, "xform");
    while (!glfwWindowShouldClose(window)){
        glfwPollEvents();

        glClearColor(0.15f, 0.18f, 0.22f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glm::mat4 proj = glm::perspective(glm::radians(45.0f), (float)WIDTH / HEIGHT, 0.1f, 100.0f);
        glm::mat4 view = glm::lookAt(glm::vec3(0.0f, 18.0f, 28.0f), glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
        glm::mat4 model = glm::rotate(glm::mat4(1.0f), (float)glfwGetTime() * 0.4f, glm::vec3(0.0f, 1.0f, 0.0f));
        glm::mat4 xform = proj * view * model;

        glUseProgram(program);
        glUniformMatrix4fv(xformLoc, 1, GL_FALSE, glm::value_ptr(xform));
        glBindVertexArray(court.vao);
        glDrawArrays(GL_TRIANGLES, 0, (GLsizei)court.n);

        glfwSwapBuffers(window);
    }

    glfwTerminate();
    return 0;
}