#include "figure.hpp"

#include "gl/camera.hpp"
#include "gl/mesh.hpp"
#include "gl/window.hpp"

#include <iostream>
#include <vector>

#include <assimp/Importer.hpp>
#include <assimp/postprocess.h>
#include <assimp/scene.h>
#include <glad/glad.h>

Figure player;

void Figure::init(){
    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);
    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, pos));
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, norm));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, color));
    glEnableVertexAttribArray(2);

    // Default pose
    rightHanded = true;

    lFoot = {1.05f, 0.05f, 11.95f};
    rFoot = {1.38f, 0.05f, 12.10f};

    lKnee = {1.06f, 0.48f, 11.90f};
    rKnee = {1.36f, 0.48f, 12.04f};

    lTorso = {1.08f, 0.92f, 11.95f};
    rTorso = {1.34f, 0.92f, 12.03f};

    lShoulder = {1.02f, 1.45f, 11.93f};
    rShoulder = {1.40f, 1.45f, 12.05f};

    head = {1.21f, 1.75f, 11.97f};

    lElbow = {0.95f, 1.18f, 11.78f};
    lHand = {1.10f, 1.08f, 11.62f};

    rElbow = {1.48f, 1.16f, 11.88f};
    rHand = {1.32f, 1.06f, 11.65f};
    racket = {1.18f, 1.38f, 11.15f};
}

void Figure::draw(){
    const glm::vec3 COLOR = {0.9f, 0.9f, 0.9f};

    std::vector<Vertex> vertices; // Ah yes I love hardcoding
    vertices.push_back({lFoot,{0, 1, 0},COLOR});
    vertices.push_back({lKnee,{0, 1, 0},COLOR});

    vertices.push_back({lKnee,{0, 1, 0},COLOR});
    vertices.push_back({lTorso,{0, 1, 0},COLOR});

    vertices.push_back({lTorso,{0, 1, 0},COLOR});
    vertices.push_back({lShoulder,{0, 1, 0},COLOR});

    vertices.push_back({lShoulder,{0, 1, 0},COLOR});
    vertices.push_back({lElbow,{0, 1, 0},COLOR});

    vertices.push_back({lElbow,{0, 1, 0},COLOR});
    vertices.push_back({lHand,{0, 1, 0},COLOR});


    vertices.push_back({rFoot,{0, 1, 0},COLOR});
    vertices.push_back({rKnee,{0, 1, 0},COLOR});

    vertices.push_back({rKnee,{0, 1, 0},COLOR});
    vertices.push_back({rTorso,{0, 1, 0},COLOR});

    vertices.push_back({rTorso,{0, 1, 0},COLOR});
    vertices.push_back({rShoulder,{0, 1, 0},COLOR});

    vertices.push_back({rShoulder,{0, 1, 0},COLOR});
    vertices.push_back({rElbow,{0, 1, 0},COLOR});

    vertices.push_back({rElbow,{0, 1, 0},COLOR});
    vertices.push_back({rHand,{0, 1, 0},COLOR});

    // TODO: Do something special with the racket?
    if(rightHanded){
        vertices.push_back({rHand,{0, 1, 0},COLOR});
        vertices.push_back({racket,{0, 1, 0},COLOR});
    }
    else{
        vertices.push_back({lHand,{0, 1, 0},COLOR});
        vertices.push_back({racket,{0, 1, 0},COLOR});
    }

    vertices.push_back({lTorso,{0, 1, 0},COLOR});
    vertices.push_back({rTorso,{0, 1, 0},COLOR});

    vertices.push_back({lShoulder,{0, 1, 0},COLOR});
    vertices.push_back({rShoulder,{0, 1, 0},COLOR});


    vertices.push_back({lShoulder,{0, 1, 0},COLOR});
    vertices.push_back({head,{0, 1, 0},COLOR});

    vertices.push_back({rShoulder,{0, 1, 0},COLOR});
    vertices.push_back({head,{0, 1, 0},COLOR});
    // Absolute cinema

    glUniformMatrix4fv(xformLoc, 1, GL_FALSE, glm::value_ptr(cameraProj() * cameraView()));
    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);

    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex), vertices.data(), GL_DYNAMIC_DRAW);
    glDrawArrays(GL_LINES, 0, (GLsizei)vertices.size());
}