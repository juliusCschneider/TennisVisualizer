TODO

Building from root

Mac
```
cmake -S visualizer -B visualizer/build
cmake --build visualizer/build
```

Windows:

```
cmake -S visualizer -B visualizer/build -G "MinGW Makefiles"
```


# Organization

`src/`: Code folder
`src/core`: World and state implementation
`src/gl`: GLFW engine implementation (can be reused across projects)
`src/gui`: Graphical interface (w/ ImGui probably ?)
`src/util`: Extranneous project specific utils (simila to `gl` but more specific) 