cmake_minimum_required(VERSION 3.11 FATAL_ERROR)
project(ComputerGraphics C CXX)

set(CMAKE_CXX_STANDARD 20)

if (EXISTS "${CMAKE_CURRENT_LIST_DIR}/framework")
	# Create framework library and include CMake scripts (compiler warnings, sanitizers and static analyzers).
	add_subdirectory("framework")
else()
	# During development the framework lives in parent folder.
	add_subdirectory("../../../framework/" "${CMAKE_BINARY_DIR}/framework/")
endif()

add_executable(Demo
	"src/main.cpp"
	)
target_compile_features(Demo PRIVATE cxx_std_20)
# Link to OpenGL, and Microsoft-GSL and/or make their header files available.
target_link_libraries(Demo PRIVATE CGFramework)
enable_sanitizers(Demo)
set_project_warnings(Demo)

# Copy all files in the resources folder to the build directory after every successful build.
add_custom_command(TARGET Demo POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy_directory
	"${CMAKE_CURRENT_LIST_DIR}/resources/" $<TARGET_FILE_DIR:Demo>)
