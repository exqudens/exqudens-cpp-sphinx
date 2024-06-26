cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

block()
    set(fileName "util.cmake")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/${fileName}")
        file(REMOVE "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}")
        file(DOWNLOAD
            "https://raw.githubusercontent.com/exqudens/exqudens-cmake/1.0.1/src/main/cmake/${fileName}"
            "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}"
            EXPECTED_MD5 "d7dd546adf3830d9eb6cca7b0dda7d4e"
            STATUS downloadStatus
        )
        if("${downloadStatus}" STREQUAL "0;\"No error\"")
            file(COPY "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/../common")
        else()
            message(FATAL_ERROR "downloadStatus: '${downloadStatus}'")
        endif()
    endif()
endblock()

include("${CMAKE_CURRENT_BINARY_DIR}/../common/util.cmake")

string(REPLACE "." ";" PRESET_NAME_ELEMENTS "${PRESET_NAME}")
if("msvc-16-x64" IN_LIST "PRESET_NAME_ELEMENTS")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-toolchain.cmake")
        set_msvc_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            VERSION "16"
            HOST "x64"
            TARGET "x64"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan.exe" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
elseif("gcc" IN_LIST PRESET_NAME_ELEMENTS)
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake")
        find_file(compilerPath NAMES "gcc" PATHS ENV GCC_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
        set_gnu_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            PATH "${compilerPath}"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
endif()

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/name-version.txt" INFO)
string(REPLACE ":" ";" INFO_LIST "${INFO}")
list(GET INFO_LIST 0 RAW_NAME)
list(GET INFO_LIST 1 RAW_VERSION)
string(STRIP "${RAW_NAME}" NAME)
string(STRIP "${RAW_VERSION}" VERSION)
project("${NAME}" VERSION "${VERSION}" LANGUAGES "NONE")

message(STATUS "project: '${PROJECT_NAME}-${PROJECT_VERSION}'")

include("GenerateExportHeader")
enable_testing()
include(GoogleTest)

find_program(CONAN_COMMAND NAMES "conan.exe" "conan" REQUIRED)
find_program(DOXYGEN_COMMAND NAMES "doxygen.exe" "doxygen" REQUIRED)

enable_language("C")
enable_language("CXX")

set(CMAKE_OBJECT_PATH_MAX 1000)
set(CMAKE_SHARED_LIBRARY_PREFIX "")
set(CMAKE_SHARED_MODULE_PREFIX "")
set(CMAKE_STATIC_LIBRARY_PREFIX "")
set(CMAKE_IMPORT_LIBRARY_PREFIX "")
set(CMAKE_STAGING_PREFIX "")
set(CMAKE_FIND_LIBRARY_PREFIXES "" "lib")
set(CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH FALSE)
set(CMAKE_FIND_USE_CMAKE_SYSTEM_PATH FALSE)
set(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH TRUE)
set(CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY FALSE)
set(CMAKE_FIND_USE_PACKAGE_REGISTRY FALSE)
set(CMAKE_FIND_USE_PACKAGE_ROOT_PATH FALSE)
set(CMAKE_FIND_USE_CMAKE_PATH TRUE)
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG FALSE)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS FALSE)
set(CMAKE_BUILD_RPATH_USE_ORIGIN TRUE)
set(CMAKE_CXX_VISIBILITY_PRESET "hidden")
set(CMAKE_VISIBILITY_INLINES_HIDDEN TRUE)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

set(CMAKE_INSTALL_PREFIX "${PROJECT_BINARY_DIR}/cmake-install" CACHE PATH "..." FORCE)

separate_arguments(CMAKE_CXX_FLAGS NATIVE_COMMAND "${CMAKE_CXX_FLAGS}")
if(MSVC)
    if(NOT "/EHa" IN_LIST CMAKE_CXX_FLAGS AND "/EHsc" IN_LIST CMAKE_CXX_FLAGS)
        list(REMOVE_ITEM CMAKE_CXX_FLAGS "/EHsc")
        list(APPEND CMAKE_CXX_FLAGS "/EHa")
    endif()
endif()
string(JOIN " " CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS})

set(CMAKE_VERBOSE_MAKEFILE TRUE CACHE BOOL "" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE CACHE BOOL "" FORCE)

set(TEST_GROUP "all" CACHE STRING "...")
set(TEST_CASE "all" CACHE STRING "...")

set(TARGET_CMAKE_INSTALL_DEPENDS_ON "cmake-test")
option(SKIP_CMAKE_TEST "..." FALSE)
if(${SKIP_CMAKE_TEST})
    set(TARGET_CMAKE_INSTALL_DEPENDS_ON "${PROJECT_NAME}")
    set(TARGET_CMAKE_INSTALL_DEPENDS_ON "cmake-test")
    if("${TEST_GROUP}" STREQUAL "all" AND "${TEST_CASE}" STREQUAL "all")
        set(TEST_REGEXP "^.+\\..+$")
    elseif(NOT "${TEST_GROUP}" STREQUAL "all" AND "${TEST_CASE}" STREQUAL "all")
        set(TEST_REGEXP "^${TEST_GROUP}\\..+$")
    elseif("${TEST_GROUP}" STREQUAL "all" AND NOT "${TEST_CASE}" STREQUAL "all")
        set(TEST_REGEXP "^.+\\.${TEST_CASE}$")
    elseif(NOT "${TEST_GROUP}" STREQUAL "all" AND NOT "${TEST_CASE}" STREQUAL "all")
        set(TEST_REGEXP "^${TEST_GROUP}\\.${TEST_CASE}$")
    endif()
endif()

if(NOT "${BUILD_SHARED_LIBS}" AND "${MINGW}")
    set(CMAKE_CXX_STANDARD_LIBRARIES "-static-libgcc -static-libstdc++ ${CMAKE_CXX_STANDARD_LIBRARIES}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-Bstatic,--whole-archive -lwinpthread -Wl,--no-whole-archive")
endif()

set_conan_architecture(CONAN_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
set_conan_compiler(CONAN_COMPILER "${CMAKE_CXX_COMPILER_ID}")
set_conan_compiler_version(CONAN_COMPILER_VERSION "${CMAKE_CXX_COMPILER_ID}" "${CMAKE_CXX_COMPILER_VERSION}" MAX_ELEMENTS "1")
set_conan_compiler_runtime(CONAN_COMPILER_RUNTIME "${CMAKE_MSVC_RUNTIME_LIBRARY}")
set_conan_compiler_runtime(CONAN_RELEASE_COMPILER_RUNTIME "${CMAKE_MSVC_RUNTIME_LIBRARY}")

set_python_boolean(CONAN_INTERFACE_ONLY "${INTERFACE_ONLY}")
set_python_boolean(CONAN_BUILD_SHARED_LIBS "${BUILD_SHARED_LIBS}")

set_conan_settings(CONAN_SETTINGS
    "arch=${CONAN_ARCH}"
    "os=${CMAKE_SYSTEM_NAME}"
    "compiler=${CONAN_COMPILER}"
    "compiler.version=${CONAN_COMPILER_VERSION}"
    "compiler.runtime=${CONAN_COMPILER_RUNTIME}"
    "compiler.libcxx=${CONAN_COMPILER_LIBCXX}"
    "build_type=${CMAKE_BUILD_TYPE}"
)
set_conan_options(CONAN_OPTIONS
    "interface=${CONAN_INTERFACE_ONLY}"
    "shared=${CONAN_BUILD_SHARED_LIBS}"
)
set("CONAN_INSTALL_PREFIX" "${PROJECT_BINARY_DIR}/conan-install")
if(NOT EXISTS "${CONAN_INSTALL_PREFIX}")
    execute_process(
        COMMAND "${CONAN_COMMAND}"
                install
                "${PROJECT_SOURCE_DIR}/conanfile.py"
                --install-folder
                "${CONAN_INSTALL_PREFIX}"
                ${CONAN_SETTINGS}
                ${CONAN_OPTIONS}
        COMMAND_ECHO "STDERR"
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ENCODING "UTF-8"
        COMMAND_ERROR_IS_FATAL ANY
    )
endif()
if(NOT EXISTS "${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
    message(FATAL_ERROR "Not exists: '${CONAN_INSTALL_PREFIX}/conan-packages.cmake'!")
endif()
include("${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
set(CMAKE_MODULE_PATH "${CONAN_INSTALL_PREFIX}")
foreach(
    conanPackageName
    cmakePackageName
    cmakePackageVersion
    cmakePackagePath
    IN ZIP_LISTS
    "${PROJECT_NAME}_CONAN_PACKAGE_NAMES"
    "${PROJECT_NAME}_CMAKE_PACKAGE_NAMES"
    "${PROJECT_NAME}_CMAKE_PACKAGE_VERSIONS"
    "${PROJECT_NAME}_CMAKE_PACKAGE_PATHS"
)
    if(
        "" STREQUAL "${conanPackageName}"
        OR "" STREQUAL "${cmakePackageName}"
        OR "" STREQUAL "${cmakePackageVersion}"
        OR "" STREQUAL "${cmakePackagePath}"
    )
        string(JOIN " " errorMessage
            "Empty value 'conanPackageName': '${conanPackageName}'"
            "or 'cmakePackageName': '${cmakePackageName}'"
            "or 'cmakePackageVersion': '${cmakePackageVersion}'"
            "or 'cmakePackagePath': '${cmakePackagePath}'!"
        )
        message(FATAL_ERROR "${errorMessage}")
    elseif(NOT IS_DIRECTORY "${cmakePackagePath}")
        message(FATAL_ERROR "Not is directory 'cmakePackagePath': '${cmakePackagePath}'!")
    endif()

    list(APPEND CMAKE_PREFIX_PATH "${cmakePackagePath}")

    if("gtest" STREQUAL "${conanPackageName}")
        file(REMOVE "${CONAN_INSTALL_PREFIX}/Find${cmakePackageName}.cmake")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${cmakePackageVersion}" EXACT QUIET CONFIG)
    else()
        file(REMOVE "${CONAN_INSTALL_PREFIX}/Find${cmakePackageName}.cmake")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${cmakePackageVersion}" EXACT QUIET CONFIG)
    endif()

endforeach()
set_not_found_package_names(NOT_FOUND_PACKAGE_NAMES ${NOT_FOUND_PACKAGE_NAMES})
if(NOT "" STREQUAL "${NOT_FOUND_PACKAGE_NAMES}")
    foreach(package ${NOT_FOUND_PACKAGE_NAMES})
        message(SEND_ERROR "${package}_FOUND: '${${package}_FOUND}' ${package}_NOT_FOUND_MESSAGE: '${${package}_NOT_FOUND_MESSAGE}'")
    endforeach()
    message(FATAL_ERROR "Some package not found!")
endif()

add_library("${PROJECT_NAME}"
    "src/main/c/exqudens/math.h"
    "src/main/c/exqudens/math.c"
    "src/main/c/exqudens/math_util.h"
    "src/main/c/exqudens/math_util.c"
    "src/main/cpp/exqudens/Strings.hpp"
    "src/main/cpp/exqudens/Strings.cpp"
)
string(CONCAT EXQUDENS_FUNCTION_ATTRIBUTES_CONTENT
    "#ifndef EXQUDENS_FUNCTION_ATTRIBUTES\n"
    "#  define EXQUDENS_FUNCTION_ATTRIBUTES\n"
    "#endif /* EXQUDENS_FUNCTION_ATTRIBUTES */\n"
)
generate_export_header("${PROJECT_NAME}"
    BASE_NAME "EXQUDENS"
    EXPORT_FILE_NAME "generated/src/main/cpp/exqudens/export.hpp"
    CUSTOM_CONTENT_FROM_VARIABLE "EXQUDENS_FUNCTION_ATTRIBUTES_CONTENT"
)
if(NOT "${BUILD_SHARED_LIBS}")
    set_target_properties("${PROJECT_NAME}" PROPERTIES COMPILE_FLAGS -DEXQUDENS_STATIC_DEFINE)
endif()
target_include_directories("${PROJECT_NAME}" PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/generated/src/main/cpp>"
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/main/c>"
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/main/cpp>"
    "$<INSTALL_INTERFACE:include>"
)
set_target_properties("${PROJECT_NAME}" PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/main/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/main/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/main/bin"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/main/bin"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/main/bin"

    ARCHIVE_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/main/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/main/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/main/lib"
    ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/main/lib"
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/main/lib"

    LIBRARY_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/main/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/main/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/main/lib"
    LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/main/lib"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/main/lib"
)
set_property(TARGET "${PROJECT_NAME}" PROPERTY "VERSION" "${PROJECT_VERSION}")
set_property(TARGET "${PROJECT_NAME}" PROPERTY "SOVERSION" "${PROJECT_VERSION}")
set_property(TARGET "${PROJECT_NAME}" PROPERTY "INTERFACE_${PROJECT_NAME}_MAJOR_VERSION" "${PROJECT_VERSION}")
set_property(TARGET "${PROJECT_NAME}" APPEND PROPERTY "COMPATIBLE_INTERFACE_STRING" "${PROJECT_NAME}_MAJOR_VERSION")
install(
    TARGETS "${PROJECT_NAME}"
    EXPORT "${PROJECT_NAME}-targets"
    INCLUDES DESTINATION "include"
    RUNTIME DESTINATION "bin"
    LIBRARY DESTINATION "lib"
    ARCHIVE DESTINATION "lib"
)
install(
    EXPORT "${PROJECT_NAME}-targets"
    DESTINATION "cmake"
    NAMESPACE "${PROJECT_NAME}::"
    FILE "${PROJECT_NAME}-targets.cmake"
)
include(CMakePackageConfigHelpers)
configure_package_config_file(
    "${PROJECT_SOURCE_DIR}/package-config.cmake.in"
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
    INSTALL_DESTINATION "cmake"
)
write_basic_package_version_file(
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-config-version.cmake"
    VERSION "${PROJECT_VERSION}"
    COMPATIBILITY "ExactVersion"
)
install(
    FILES "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-config-version.cmake"
    DESTINATION "cmake"
)
install(
    DIRECTORY "${PROJECT_BINARY_DIR}/generated/src/main/cpp/"
              "src/main/cpp/"
    DESTINATION "include"
    FILES_MATCHING
    PATTERN "*.h"
    PATTERN "*.hpp"
)

add_library("test-lib" STATIC
    "src/test/cpp/TestConfiguration.hpp"
    "src/test/cpp/TestConfiguration.cpp"
    "src/test/cpp/TestApplication.hpp"
    "src/test/cpp/TestApplication.cpp"
    "src/test/cpp/TestUtils.hpp"
    "src/test/cpp/TestUtils.cpp"
    "src/test/cpp/exqudens/Tests.hpp"
)
target_include_directories("test-lib" PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/test/cpp>"
    "$<INSTALL_INTERFACE:include>"
)
target_link_libraries("test-lib" PUBLIC
    "${PROJECT_NAME}"
    "GTest::gmock"
    "GTest::gtest"
    "GTest::gmock_main"
    "GTest::gtest_main"
)
set_target_properties("test-lib" PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/bin"

    ARCHIVE_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/lib"

    LIBRARY_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/lib"
)

add_executable("test-app" "src/test/cpp/main.cpp")
target_link_libraries("test-app"
    "test-lib"
)
set_target_properties("test-app" PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/bin"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/bin"

    ARCHIVE_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/lib"
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/lib"

    LIBRARY_OUTPUT_DIRECTORY                "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE        "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL     "${PROJECT_BINARY_DIR}/test/lib"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG          "${PROJECT_BINARY_DIR}/test/lib"
)
if("${BUILD_SHARED_LIBS}")
    if("${CMAKE_SYSTEM_NAME}" STREQUAL "Windows")
        add_custom_command(TARGET "test-app"
            POST_BUILD
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "$<TARGET_PROPERTY:${PROJECT_NAME},RUNTIME_OUTPUT_DIRECTORY>" "$<TARGET_PROPERTY:test-app,RUNTIME_OUTPUT_DIRECTORY>"
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "${CONAN_INSTALL_PREFIX}/bin" "$<TARGET_PROPERTY:test-app,RUNTIME_OUTPUT_DIRECTORY>"
            VERBATIM
            USES_TERMINAL
        )
    elseif()
        add_custom_command(TARGET "test-app"
            POST_BUILD
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "$<TARGET_PROPERTY:${PROJECT_NAME},LIBRARY_OUTPUT_DIRECTORY>" "$<TARGET_PROPERTY:test-app,LIBRARY_OUTPUT_DIRECTORY>"
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "${CONAN_INSTALL_PREFIX}/lib" "$<TARGET_PROPERTY:test-app,LIBRARY_OUTPUT_DIRECTORY>"
            VERBATIM
            USES_TERMINAL
        )
    endif()
endif()

gtest_discover_tests("test-app"
    WORKING_DIRECTORY "${PROJECT_BINARY_DIR}/test/bin"
    PROPERTIES ENVIRONMENT "PARENT_PATH=;PATH="
    XML_OUTPUT_DIR "${PROJECT_BINARY_DIR}/test/report/xml"
)

add_custom_target("cmake-test"
    COMMAND "${CMAKE_CTEST_COMMAND}" --preset "${PRESET_NAME}"
    DEPENDS "test-app"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)

add_custom_target("cmake-install" ALL
    COMMAND "${CMAKE_COMMAND}" --install "${PROJECT_BINARY_DIR}" --prefix "${CMAKE_INSTALL_PREFIX}"
    DEPENDS ${TARGET_CMAKE_INSTALL_DEPENDS_ON}
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)

add_custom_target("conan-export"
    COMMAND "${CONAN_COMMAND}"
            export-pkg
            --force
            "${PROJECT_SOURCE_DIR}/conanfile.py"
            #"gitlab-group+gitlab-sub-group+${PROJECT_NAME}/stable"
            --package-folder
            "${CMAKE_INSTALL_PREFIX}"
            ${CONAN_SETTINGS}
            ${CONAN_OPTIONS}
    DEPENDS "${CMAKE_INSTALL_PREFIX}/cmake/${PROJECT_NAME}-config.cmake"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)

add_custom_target("sphinx-doc"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "doxygen"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            SOURCE_DIR "src/main/cpp"
            OUTPUT_DIR "build/doxygen/main"
            CLEAN "true"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "doxygen"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            SOURCE_DIR "src/test/cpp"
            OUTPUT_DIR "build/doxygen/test"
            CLEAN "true"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "sphinx"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            REQUIREMENTS_FILE "sphinx-requirements.txt"
            CONF_JSON_VARS "PROJECT_DIR=${PROJECT_SOURCE_DIR}"
                           "PROJECT_BREATHE_DEFAULT=main"
                           "PROJECT_TITLE=${PROJECT_NAME} designs"
            OUTPUT_DIR "build/doc/full"
            TYPE "full"
            FILES "requirements/requirements.rst"
                  "designs/designs.rst"
                  "links/links.rst"
            EXTRA_FILES "designs/png/structure.png"
            BUILDERS "html" "docx"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-requirements"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "sphinx"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            REQUIREMENTS_FILE "sphinx-requirements.txt"
            CONF_JSON_VARS "PROJECT_DIR=${PROJECT_SOURCE_DIR}"
                           "PROJECT_TITLE=${PROJECT_NAME} designs"
                           "PROJECT_BREATHE_DEFAULT=main"
            OUTPUT_DIR "build/doc/requirements"
            TYPE "requirements"
            FILES "requirements/requirements.rst"
            BUILDERS "html" "docx"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-c-designs"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "doxygen"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            #SOURCE_DIR "src/main/c"
            OUTPUT_DIR "build/doxygen/main"
            DOXYGEN_TAGS "PROJECT_NAME=${PROJECT_NAME}"
                         "OUTPUT_DIRECTORY=build/doxygen/main"
                         "RECURSIVE=YES"
                         "INPUT=src/main/c"
                         "ENABLE_PREPROCESSING=YES"
                         "GENERATE_XML=YES"
                         "GENERATE_HTML=NO"
                         "GENERATE_LATEX=NO"
                         "FILE_PATTERNS=*.h *.c"
                         "OPTIMIZE_OUTPUT_FOR_C=YES"
                         "EXTRACT_ALL=YES"
                         "EXTRACT_ANON_NSPACES=YES"
                         "EXTRACT_LOCAL_CLASSES=YES"
                         "EXTRACT_LOCAL_METHODS=YES"
                         "EXTRACT_PACKAGE=YES"
                         "EXTRACT_PRIVATE=YES"
                         "EXTRACT_PRIV_VIRTUAL=YES"
                         "EXTRACT_STATIC=YES"
                         "MACRO_EXPANSION=YES"
                         "EXPAND_ONLY_PREDEF=YES"
                         "PREDEFINED=DOXYGEN_SKIP_THIS"
            CLEAN "true"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "sphinx"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            REQUIREMENTS_FILE "sphinx-requirements.txt"
            CONF_JSON_VARS "PROJECT_DIR=${PROJECT_SOURCE_DIR}"
                           "PROJECT_BREATHE_DEFAULT=main"
                           "PROJECT_TITLE=${PROJECT_NAME} designs"
                           "PROJECT_STYLE_DOCX=${PROJECT_SOURCE_DIR}/doc/style.docx"
            OUTPUT_DIR "build/doc/c-design"
            TYPE "designs"
            FILES "designs/c-design.rst"
            BUILDERS #"html"
                     "docx"
            WARNINGS_TO_ERRORS "false"
            SPHINX_WARNINGS_ERRORS_FILE "${PROJECT_BINARY_DIR}/sphinx-warnings-errors.txt"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-designs"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "doxygen"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            SOURCE_DIR "src/main/cpp"
            OUTPUT_DIR "build/doxygen/main"
            DOXYGEN_ADD_TAGS "IMAGE_PATH=src/main/resources/png"
            CLEAN "true"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "sphinx"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            REQUIREMENTS_FILE "sphinx-requirements.txt"
            CONF_JSON_VARS "PROJECT_DIR=${PROJECT_SOURCE_DIR}"
                           "PROJECT_BREATHE_DEFAULT=main"
                           "PROJECT_TITLE=${PROJECT_NAME} designs"
                           "PROJECT_STYLE_DOCX=${PROJECT_SOURCE_DIR}/doc/style.docx"
            OUTPUT_DIR "build/doc/designs"
            TYPE "designs"
            FILES "designs/designs.rst"
            EXTRA_FILES "designs/png/structure.png"
                        #"docutils.conf"
            BUILDERS "html" "docx"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-designs-1"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "doxygen"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            SOURCE_DIR "src/main/cpp"
            OUTPUT_DIR "build/doxygen/main"
            DOXYGEN_ADD_TAGS "IMAGE_PATH=src/main/resources/png"
            CLEAN "true"
    COMMAND "${CMAKE_COMMAND}" "-P" "${PROJECT_BINARY_DIR}/../common/util.cmake" "--" "sphinx"
            SOURCE_BASE_DIR "${PROJECT_SOURCE_DIR}"
            REQUIREMENTS_FILE "sphinx-requirements.txt"
            CONF_JSON_VARS "PROJECT_DIR=${PROJECT_SOURCE_DIR}"
                           "PROJECT_BREATHE_DEFAULT=main"
                           "PROJECT_TITLE=${PROJECT_NAME} designs"
                           "PROJECT_STYLE_DOCX=${PROJECT_SOURCE_DIR}/doc/style.docx"
                           "PROJECT_GENERATED_INCLUDE_PATH=generated/designs-1-include.rst"
            OUTPUT_DIR "build/doc/designs-1"
            TYPE "designs-1"
            FILES "designs/designs-1.rst"
                  #"generated/designs-1-include.rst>TOCTREE_ONLY"
            EXTRA_FILES "designs/png/structure.png"
                        #"docutils.conf"
            BUILDERS "html" "docx"
            WARNINGS_TO_ERRORS "false"
            SPHINX_WARNINGS_ERRORS_FILE "${PROJECT_BINARY_DIR}/sphinx-warnings-errors.txt"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-all"
    COMMAND "${CMAKE_COMMAND}" "-E" "echo" "BUILD_SUCCESSFUL"
    DEPENDS "sphinx-doc"
            "sphinx-doc-requirements"
            "sphinx-doc-designs"
            "sphinx-doc-designs-1"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)
add_custom_target("sphinx-doc-clean"
    COMMAND "${CMAKE_COMMAND}" "-E" "rm" "-rf" "build/doxygen" "build/doc"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
    USES_TERMINAL
)

set_target_names(ALL_TARGETS "${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "project: '${PROJECT_NAME}-${PROJECT_VERSION}' all targets:")
foreach(t IN LISTS ALL_TARGETS)
    message(STATUS "${t}")
endforeach()
