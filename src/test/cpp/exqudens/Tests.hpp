#pragma once

#include <exception>
#include <iostream>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "TestUtils.hpp"
#include "exqudens/Strings.hpp"

namespace exqudens {

  class Tests : public testing::Test {};

  TEST_F(Tests, test1) {
    try {
      std::cout << "executableDir: '" + TestUtils::getExecutableDir() + "'\n";
      std::string expected = "aaa ";
      std::cout << "expected: '" + expected + "'\n";
      std::string actual = Strings::ltrim(" \t\n aaa ");
      std::cout << "actual: '" + actual + "'\n";

      ASSERT_EQ(expected, actual);
    } catch (const std::exception& e) {
      FAIL() << TestUtils::toString(e);
    }
  }

  TEST_F(Tests, test2) {
    try {
      std::cout << "executableDir: '" + TestUtils::getExecutableDir() + "'\n";
      std::string expected = " aaa";
      std::cout << "expected: '" + expected + "'\n";
      std::string actual = Strings::rtrim(" aaa \t\n ");
      std::cout << "actual: '" + actual + "'\n";

      ASSERT_EQ(expected, actual);
    } catch (const std::exception& e) {
      FAIL() << TestUtils::toString(e);
    }
  }

  TEST_F(Tests, test3) {
    try {
      std::cout << "executableDir: '" + TestUtils::getExecutableDir() + "'\n";
      std::string expected = "aaa";
      std::cout << "expected: '" + expected + "'\n";
      std::string actual = Strings::trim(" \t\n aaa \t\n ");
      std::cout << "actual: '" + actual + "'\n";

      ASSERT_EQ(expected, actual);
    } catch (const std::exception& e) {
      FAIL() << TestUtils::toString(e);
    }
  }

}
