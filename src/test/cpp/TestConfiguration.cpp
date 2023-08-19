#include "TestConfiguration.hpp"

#include <filesystem>
#include <stdexcept>

std::string TestConfiguration::getExecutableFile() {
  try {
    return executableFile.value();
  } catch (...) {
    std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
  }
}

std::string TestConfiguration::getExecutableDir() {
  try {
    return executableDir.value();
  } catch (...) {
    std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
  }
}

void TestConfiguration::setExecutableFile(const std::string& value) {
  try {
    executableFile = value;
    executableDir = std::filesystem::path(value).parent_path().string();
  } catch (...) {
    std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
  }
}
