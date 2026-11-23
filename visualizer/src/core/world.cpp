#include "world.hpp"

#include "gl/mesh.hpp"

#include <glm/gtc/type_ptr.hpp>

Mesh court, ball;

void initWorld(){
    court.load(ASSET_DIR "models/Court.obj");
    ball.load(ASSET_DIR "models/Ball.obj");
}

void updateWorld(){

}

void renderWorld(){
    glm::mat4 courtModel = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.0f, 0.0f));
    court.draw(courtModel);
}