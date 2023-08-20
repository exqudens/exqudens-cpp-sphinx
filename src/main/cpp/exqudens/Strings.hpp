#pragma once

#include <string>

#include "exqudens/export.hpp"

namespace exqudens {

  /*!

    @brief String utility functions container.

  */
  class EXQUDENS_EXPORT Strings {

    public:

      /*!

        @brief Remove all spaces from begin of the string.

      */
      static std::string ltrim(const std::string& value);

      /*!

        @brief Remove all spaces from end of the string.

      */
      static std::string rtrim(const std::string& value);

      /*!

        @brief Remove all spaces from begin and end of the string.

      */
      static std::string trim(const std::string& value);

  };

}
