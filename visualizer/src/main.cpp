#include "gl/window.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>

#include <assimp/Importer.hpp>
#include <assimp/postprocess.h>
#include <assimp/scene.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

struct Vertex{
    glm::vec3 pos;
    glm::vec3 norm;
    glm::vec3 color;
};

static GLuint compileShader(GLenum type, const char* path){
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

static GLuint createProgram(const char* vsPath, const char* fsPath){
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

static std::vector<Vertex> loadObj(const char* path){
    std::vector<Vertex> vertices;
    Assimp::Importer importer;
    const aiScene* scene = importer.ReadFile(path, aiProcess_Triangulate | aiProcess_GenSmoothNormals | aiProcess_PreTransformVertices);

    if(!scene || !scene->mRootNode){
        std::cerr << "Assimp error: " << importer.GetErrorString() << "\n";
        return vertices;
    }

    for(unsigned m = 0;m < scene->mNumMeshes;m++){
        const aiMesh* mesh = scene->mMeshes[m];
        aiColor4D diff(0.8f, 0.8f, 0.8f, 1.0f);
        aiGetMaterialColor(scene->mMaterials[mesh->mMaterialIndex], AI_MATKEY_COLOR_DIFFUSE, &diff);

        for(unsigned f = 0;f < mesh->mNumFaces;f++){
            const aiFace& face = mesh->mFaces[f];
            for(unsigned i = 0;i < face.mNumIndices;i++){
                unsigned idx = face.mIndices[i];
                const aiVector3D& v = mesh->mVertices[idx];
                const aiVector3D n = mesh->HasNormals() ? mesh->mNormals[idx] : aiVector3D(0, 1, 0);
                vertices.push_back({{v.x, v.y, v.z}, {n.x, n.y, n.z}, {diff.r, diff.g, diff.b}});
            }
        }
    }
    return vertices;
}

int main(){
    if(!init()) return -1;

    GLuint program = createProgram(ASSET_DIR "shaders/v.glsl", ASSET_DIR "shaders/f.glsl");
    std::vector<Vertex> vertices = loadObj(ASSET_DIR "models/Court.obj");

    GLuint vao, vbo;
    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);

    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex), vertices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, pos));
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, norm));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, color));
    glEnableVertexAttribArray(2);

    GLint xformLoc = glGetUniformLocation(program, "xform");

    while(!glfwWindowShouldClose(window)){
        glfwPollEvents();

        glClearColor(0.15f, 0.18f, 0.22f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glm::mat4 proj = glm::perspective(glm::radians(45.0f), (float)WIDTH / HEIGHT, 0.1f, 100.0f);
        glm::mat4 view = glm::lookAt(glm::vec3(0.0f, 18.0f, 28.0f), glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
        glm::mat4 model = glm::rotate(glm::mat4(1.0f), (float)glfwGetTime() * 0.4f, glm::vec3(0.0f, 1.0f, 0.0f));
        glm::mat4 xform = proj * view * model;

        glUseProgram(program);
        glUniformMatrix4fv(xformLoc, 1, GL_FALSE, glm::value_ptr(xform));
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLES, 0, (GLsizei)vertices.size());

        glfwSwapBuffers(window);
    }

    glfwTerminate();
    return 0;
}