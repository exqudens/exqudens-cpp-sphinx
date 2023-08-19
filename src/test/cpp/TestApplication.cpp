#include "TestApplication.hpp"

#include <string>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "TestConfiguration.hpp"
#include "exqudens/Tests.hpp"

int TestApplication::run(int* argc, char** argv) {
  if (argc != nullptr && *argc > 0) {
    TestConfiguration::setExecutableFile(std::string(argv[0]));
  }
  testing::InitGoogleMock(argc, argv);
  testing::InitGoogleTest(argc, argv);
  return RUN_ALL_TESTS();
}
