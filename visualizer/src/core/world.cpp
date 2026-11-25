#include "core/world.hpp"

#include "core/figure.hpp"
#include "gl/mesh.hpp"

#include <glm/gtc/type_ptr.hpp>

Mesh court, ball;

void initWorld(){
    court.load(ASSET_DIR "models/Court.obj");
    ball.load(ASSET_DIR "models/Ball.obj");

    player.init();
}

void updateWorld(){
    // TODO: Probably put the timeline integration in here ?
}

void renderWorld(){
    glm::mat4 courtModel = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.0f, 0.0f));
    court.draw(courtModel);

    player.draw();
}