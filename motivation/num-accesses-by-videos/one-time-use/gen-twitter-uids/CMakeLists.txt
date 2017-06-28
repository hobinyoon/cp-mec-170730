cmake_minimum_required(VERSION 2.8)

set(EXE_NAME "gen")

project(${EXE_NAME})

include_directories(src/cache)

file(GLOB_RECURSE sources src/*.cpp)

add_executable(${EXE_NAME} ${sources})

target_compile_options(${EXE_NAME} PUBLIC -Wall -Werror -std=gnu++11)

# http://stackoverflow.com/questions/10984442/how-to-detect-c11-support-of-a-compiler-with-cmake/20165220#20165220
set_property(TARGET ${EXE_NAME} PROPERTY CXX_STANDARD 11)

find_package(Boost COMPONENTS
	date_time
	filesystem
	program_options
	regex
	system
	timer
	REQUIRED)

target_link_libraries(${EXE_NAME} PUBLIC
	${Boost_LIBRARIES}
  pthread
	)
