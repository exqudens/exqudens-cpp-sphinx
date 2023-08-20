cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

cmake_policy(PUSH)
cmake_policy(SET CMP0007 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0010 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0012 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0054 NEW)
cmake_policy(PUSH)
cmake_policy(SET CMP0057 NEW)

function(execute_script args)
    set(currentFunctionName "${CMAKE_CURRENT_FUNCTION}")
    cmake_path(GET "CMAKE_CURRENT_LIST_DIR" PARENT_PATH projectDir)
    cmake_path(GET "CMAKE_CURRENT_LIST_FILE" STEM currentFileNameNoExt)
    string(JOIN "\n" requirementsFileContent
        "Sphinx==6.2.1"
        "linuxdoc==20230506"
        "breathe==4.35.0"
        "xmltodict==0.13.0"
        "mlx.traceability==10.0.0"
        "docxbuilder==1.2.0"
        "rst2pdf==0.100"
        ""
    )

    set(options)
    set(oneValueKeywords
        "VERBOSE"
        "SSL"
        "WARNINGS_TO_ERRORS"
        "TOCTREE_MAXDEPTH"
        "TOCTREE_CAPTION"
        "SOURCE_DIR"
        "BUILD_DIR"
        "REQUIREMENTS_FILE"
        "ENV_DIR"
        "TITLE"
        "OUTPUT_DIR"
        "CLEAN"
    )
    set(multiValueKeywords
        "FILES"
        "EXTRA_FILES"
        "TEST_REPORT_FILES"
        "BUILDERS"
    )

    cmake_parse_arguments("${currentFunctionName}" "${options}" "${oneValueKeywords}" "${multiValueKeywords}" "${args}")

    if(NOT "${${currentFunctionName}_UNPARSED_ARGUMENTS}" STREQUAL "")
        message(FATAL_ERROR "Unparsed arguments: '${${currentFunctionName}_UNPARSED_ARGUMENTS}'")
    endif()

    if("${${currentFunctionName}_VERBOSE}")
        set(verbose "TRUE")
    else()
        set(verbose "FALSE")
    endif()

    if("${verbose}")
        message(STATUS "execute file: '${CMAKE_CURRENT_LIST_FILE}'")
        string(TIMESTAMP currentDateTime "%Y-%m-%d %H:%M:%S")
        message(STATUS "currentDateTime: '${currentDateTime}'")
    endif()

    if("${${currentFunctionName}_SSL}" STREQUAL "")
        set(ssl "TRUE")
    else()
        if("${${currentFunctionName}_SSL}")
            set(ssl "TRUE")
        else()
            set(ssl "FALSE")
        endif()
    endif()

    if("${${currentFunctionName}_WARNINGS_TO_ERRORS}" STREQUAL "")
        set(warningsToErrors "TRUE")
    else()
        if("${${currentFunctionName}_WARNINGS_TO_ERRORS}")
            set(warningsToErrors "TRUE")
        else()
            set(warningsToErrors "FALSE")
        endif()
    endif()

    if("${${currentFunctionName}_TOCTREE_MAXDEPTH}" STREQUAL "")
        set(toctreeMaxdepth "2")
    else()
        set(toctreeMaxdepth "${${currentFunctionName}_TOCTREE_MAXDEPTH}")
    endif()

    if("${${currentFunctionName}_TOCTREE_CAPTION}" STREQUAL "")
        set(toctreeCaption "Contents:")
    else()
        set(toctreeCaption "${${currentFunctionName}_TOCTREE_CAPTION}")
    endif()

    if("${${currentFunctionName}_SOURCE_DIR}" STREQUAL "")
        set(sourceDirRelative "doc")
    else()
        set(sourceDirRelative "${${currentFunctionName}_SOURCE_DIR}")
        cmake_path(APPEND sourceDirRelative "DIR")
        cmake_path(GET "sourceDirRelative" PARENT_PATH sourceDirRelative)
    endif()

    if("${${currentFunctionName}_BUILD_DIR}" STREQUAL "")
        set(buildDirRelative "build/${currentFileNameNoExt}")
    else()
        set(buildDirRelative "${${currentFunctionName}_BUILD_DIR}")
        cmake_path(APPEND buildDirRelative "DIR")
        cmake_path(GET "buildDirRelative" PARENT_PATH buildDirRelative)
    endif()

    if("${${currentFunctionName}_REQUIREMENTS_FILE}" STREQUAL "")
        set(requirementsFileRelative "${buildDirRelative}/requirements.txt")
    else()
        set(requirementsFileRelative "${${currentFunctionName}_REQUIREMENTS_FILE}")
        cmake_path(APPEND requirementsFileRelative "DIR")
        cmake_path(GET "requirementsFileRelative" PARENT_PATH requirementsFileRelative)
    endif()

    if("${${currentFunctionName}_ENV_DIR}" STREQUAL "")
        set(envDirRelative "${buildDirRelative}/py-env")
    else()
        set(envDirRelative "${${currentFunctionName}_ENV_DIR}")
        cmake_path(APPEND envDirRelative "DIR")
        cmake_path(GET "envDirRelative" PARENT_PATH envDirRelative)
    endif()

    if("${${currentFunctionName}_TITLE}" STREQUAL "")
        set(title "documentation")
    else()
        set(title "${${currentFunctionName}_TITLE}")
        string(REPLACE " " "_" titleFileName "${title}")
    endif()

    if("${${currentFunctionName}_OUTPUT_DIR}" STREQUAL "")
        set(outputDirRelative "build/doc/${titleFileName}")
    else()
        set(outputDirRelative "${${currentFunctionName}_OUTPUT_DIR}")
        cmake_path(APPEND outputDirRelative "DIR")
        cmake_path(GET "outputDirRelative" PARENT_PATH outputDirRelative)
    endif()

    if("${${currentFunctionName}_CLEAN}" STREQUAL "")
        set(clean "TRUE")
    else()
        if("${${currentFunctionName}_CLEAN}")
            set(clean "TRUE")
        else()
            set(clean "FALSE")
        endif()
    endif()

    if("${${currentFunctionName}_BUILDERS}" STREQUAL "")
        set(builders "html" "docx" "pdf")
    else()
        set(builders "${${currentFunctionName}_BUILDERS}")
    endif()

    if("${${currentFunctionName}_FILES}" STREQUAL "")
        set(files
            "requirements/requirements.rst"
            "designs/designs.rst"
            "tests/tests.rst"
            "links/links.rst"
        )
    else()
        set(files "")
        foreach(file IN LISTS "${currentFunctionName}_FILES")
            set(fileRelative "${file}")
            cmake_path(APPEND fileRelative "DIR")
            cmake_path(GET "fileRelative" PARENT_PATH fileRelative)
            list(APPEND files "${fileRelative}")
        endforeach()
    endif()

    if("${${currentFunctionName}_EXTRA_FILES}" STREQUAL "")
        set(extraFiles "")
    else()
        set(extraFiles "${${currentFunctionName}_EXTRA_FILES}")
    endif()

    if("${${currentFunctionName}_TEST_REPORT_FILES}" STREQUAL "")
        set(testReportFiles "None")
    else()
        set(testReportFiles "${${currentFunctionName}_TEST_REPORT_FILES}")
    endif()

    find_program(SPHINX_BUILD_COMMAND
        NAMES "sphinx-build.exe" "sphinx-build"
        PATHS "${projectDir}/${envDirRelative}/Scripts"
              "${projectDir}/${envDirRelative}/bin"
        NO_CACHE
        NO_DEFAULT_PATH
    )

    # create sphinx env
    if("${SPHINX_BUILD_COMMAND}" STREQUAL "SPHINX_BUILD_COMMAND-NOTFOUND")
        if("${verbose}")
            message(STATUS "create sphinx env")
        endif()
        if(NOT EXISTS "${projectDir}/${requirementsFileRelative}")
            file(WRITE "${projectDir}/${requirementsFileRelative}" "${requirementsFileContent}")
        endif()
        find_program(PYTHON_COMMAND NAMES "py.exe" "py" "python.exe" "python" NO_CACHE REQUIRED)
        execute_process(
            COMMAND "${PYTHON_COMMAND}" "-m" "venv" "${envDirRelative}"
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(PIP_COMMAND
            NAMES "pip.exe" "pip"
            PATHS "${projectDir}/${envDirRelative}/Scripts"
                  "${projectDir}/${envDirRelative}/bin"
            NO_CACHE
            REQUIRED
            NO_DEFAULT_PATH
        )
        set(command "${PIP_COMMAND}" "install")
        if(NOT "${ssl}")
            list(APPEND command
                "--trusted-host" "pypi.org"
                "--trusted-host" "pypi.python.org"
                "--trusted-host" "files.pythonhosted.org"
                "-r" "${requirementsFileRelative}"
            )
        endif()
        list(APPEND command "-r" "${requirementsFileRelative}")
        execute_process(
            COMMAND ${command}
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )
        find_program(SPHINX_BUILD_COMMAND
            NAMES "sphinx-build.exe" "sphinx-build"
            PATHS "${projectDir}/${envDirRelative}/Scripts"
                  "${projectDir}/${envDirRelative}/bin"
            NO_CACHE
            REQUIRED
            NO_DEFAULT_PATH
        )
    endif()

    # create structure
    if("${verbose}")
        message(STATUS "create structure")
    endif()
    if(EXISTS "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}")
        file(REMOVE_RECURSE "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}")
    endif()
    string(JOIN "\n" indexRstContent
        ".. toctree::"
        "   :maxdepth: ${toctreeMaxdepth}"
        "   :caption: ${toctreeCaption}"
        ""
        ""
    )
    foreach(file IN LISTS "files")
        cmake_path(GET "file" PARENT_PATH fileDir)
        cmake_path(GET "file" FILENAME fileName)
        cmake_path(GET "fileName" STEM fileNameNoExt)
        if("${fileDir}" STREQUAL "")
            string(APPEND indexRstContent "   ${fileNameNoExt}" "\n")
            file(COPY "${projectDir}/${sourceDirRelative}/${file}" DESTINATION "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}")
        else()
            string(APPEND indexRstContent "   ${fileDir}/${fileNameNoExt}" "\n")
            file(MAKE_DIRECTORY "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}/${fileDir}")
            file(COPY "${projectDir}/${sourceDirRelative}/${file}" DESTINATION "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}/${fileDir}")
        endif()
    endforeach()
    foreach(file IN LISTS "extraFiles")
        string(FIND "${file}" ">" delimiterIndex)
        if("${delimiterIndex}" EQUAL "-1")
            set(fileSrc "${projectDir}/${sourceDirRelative}/${file}")
            set(fileDst "${file}")
        else()
            string(REPLACE ">" ";" fileParts "${file}")
            list(GET "fileParts" "0" fileSrc)
            list(GET "fileParts" "1" fileDst)
            cmake_path(RELATIVE_PATH "fileSrc" BASE_DIRECTORY "${projectDir}" OUTPUT_VARIABLE fileSrc)
        endif()

        cmake_path(GET "fileDst" PARENT_PATH fileDir)
        if("${fileDir}" STREQUAL "")
            file(COPY "${fileSrc}" DESTINATION "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}")
        else()
            file(MAKE_DIRECTORY "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}/${fileDir}")
            file(COPY "${fileSrc}" DESTINATION "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}/${fileDir}")
        endif()

    endforeach()
    file(WRITE "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}/index.rst" "${indexRstContent}")
    file(COPY "${projectDir}/${sourceDirRelative}/conf.py" DESTINATION "${projectDir}/${buildDirRelative}/${sourceDirRelative}/${titleFileName}")

    foreach(builder IN LISTS "builders")

        # build
        if("${verbose}")
            message(STATUS "build ${builder}")
        endif()
        if("${clean}" AND EXISTS "${projectDir}/${outputDirRelative}/${builder}")
            file(REMOVE_RECURSE "${projectDir}/${outputDirRelative}/${builder}")
        endif()
        set(flags "")
        if("${verbose}")
            list(APPEND flags "-v" "-v" "-v")
        else()
            if("${warningsToErrors}")
                list(APPEND flags "-q")
            else()
                list(APPEND flags "-Q")
            endif()
        endif()
        if("${warningsToErrors}")
            list(APPEND "flags" "-W")
        endif()
        list(APPEND "flags"
            "-E"
        )
        execute_process(
            COMMAND "${CMAKE_COMMAND}"
                    "-E"
                    "env"
                    "PROJECT_DIR=${projectDir}"
                    "PROJECT_TITLE=${title}"
                    "PROJECT_TEST_REPORT_FILES=${testReportFiles}"
                    "--"
                    "${SPHINX_BUILD_COMMAND}"
                    ${flags}
                    "-b"
                    "${builder}"
                    "${buildDirRelative}/${sourceDirRelative}/${titleFileName}"
                    "${outputDirRelative}/${builder}"
            WORKING_DIRECTORY "${projectDir}"
            COMMAND_ECHO "STDOUT"
            COMMAND_ERROR_IS_FATAL "ANY"
        )

    endforeach()

    if("${verbose}")
        string(TIMESTAMP currentDateTime "%Y-%m-%d %H:%M:%S")
        message(STATUS "currentDateTime: '${currentDateTime}'")
    endif()
endfunction()

block()
    set(args "")
    set(argsStarted "FALSE")
    math(EXPR argIndexMax "${CMAKE_ARGC} - 1")
    foreach(i RANGE "0" "${argIndexMax}")
        if("${argsStarted}")
            list(APPEND args "${CMAKE_ARGV${i}}")
        elseif(NOT "${argsStarted}" AND "${CMAKE_ARGV${i}}" STREQUAL "--")
            set(argsStarted "TRUE")
        endif()
    endforeach()
    execute_script("${args}")
endblock()

cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
cmake_policy(POP)
