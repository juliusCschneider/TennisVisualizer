#include <glad/glad.h>
#include <glm/glm.hpp>

struct Vertex
{
    glm::vec3 pos;
    glm::vec3 norm;
    glm::vec3 color;
};

struct Mesh
{
    int n;
    GLuint vao;
    GLuint vbo;

    void load(const char *path);
};