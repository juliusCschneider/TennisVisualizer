rm ./visualizer/build/app
cmake -S visualizer -B visualizer/build
cmake --build visualizer/build
./visualizer/build/app
