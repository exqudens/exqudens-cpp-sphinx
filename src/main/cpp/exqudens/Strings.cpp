#include "exqudens/Strings.hpp"

#include <algorithm>
#include <cctype>
#include <locale>

namespace exqudens {

  std::string Strings::ltrim(const std::string& value) {
    try {
      std::string s = value;
      s.erase(
          s.begin(),
          std::find_if(
              s.begin(),
              s.end(),
              [](unsigned char ch) { return !std::isspace(ch); }
          )
      );
      return s;
    } catch (...) {
      std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
    }
  }

  std::string Strings::rtrim(const std::string& value) {
    try {
      std::string s = value;
      s.erase(
          std::find_if(
              s.rbegin(),
              s.rend(),
              [](unsigned char ch) { return !std::isspace(ch); }
          ).base(),
          s.end()
      );
      return s;
    } catch (...) {
      std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
    }
  }

  std::string Strings::trim(const std::string& value) {
    try {
      std::string s = value;
      s = ltrim(s);
      s = rtrim(s);
      return s;
    } catch (...) {
      std::throw_with_nested(std::runtime_error(std::string(__FUNCTION__) + "(" + __FILE__ + ":" + std::to_string(__LINE__) + ")"));
    }
  }

}
