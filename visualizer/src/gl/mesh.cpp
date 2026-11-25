#include "gl/mesh.hpp"

#include "gl/camera.hpp"
#include "gl/window.hpp"

#include <iostream>

#include <assimp/Importer.hpp>
#include <assimp/postprocess.h>
#include <assimp/scene.h>
#include <glad/glad.h>
#include <vector>

void Mesh::load(const char* path){
    std::vector<Vertex> vertices;
    Assimp::Importer importer;
    const aiScene* scene = importer.ReadFile(path, aiProcess_Triangulate | aiProcess_GenSmoothNormals | aiProcess_PreTransformVertices);

    if(!scene || !scene->mRootNode){
        std::cerr << "Assimp error: " << importer.GetErrorString() << "\n";
        return;
    }

    for(unsigned m = 0; m < scene->mNumMeshes; m++){
        const aiMesh* mesh = scene->mMeshes[m];
        aiColor4D diff(0.0f, 0.0f, 0.0f, 1.0f);
        aiGetMaterialColor(scene->mMaterials[mesh->mMaterialIndex], AI_MATKEY_COLOR_DIFFUSE, &diff);

        for(unsigned f = 0; f < mesh->mNumFaces; f++){
            const aiFace& face = mesh->mFaces[f];
            for(unsigned i = 0; i < face.mNumIndices; i++){
                unsigned idx = face.mIndices[i];
                const aiVector3D& v = mesh->mVertices[idx];
                const aiVector3D n = mesh->HasNormals() ? mesh->mNormals[idx] : aiVector3D(0, 1, 0);
                vertices.push_back({{v.x, v.y, v.z},{n.x, n.y, n.z},{diff.r, diff.g, diff.b}});
            }
        }
    }

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

    n = vertices.size();
}

void Mesh::draw(glm::mat4 model){
    glUniformMatrix4fv(xformLoc, 1, GL_FALSE, glm::value_ptr(cameraProj() * cameraView() * model)); // TODO: Calculating these camera matrices every time per mesh is probably inefficient, but not nearly as inefficient as the drawing and calculations in rendering right? Surely. Should probs profile to be sure, but I don't gaf
    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLES, 0, (GLsizei)n);
}