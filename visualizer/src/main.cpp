
#include "gl/camera.hpp"
#include "gl/window.hpp"

int main(){
    if(!initGL()) return -1;
    initCamera();

    start();
    dispose();
    return 0;
}