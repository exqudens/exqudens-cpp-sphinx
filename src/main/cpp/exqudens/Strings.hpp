#pragma once

#include <string>

#include "exqudens/export.hpp"

namespace exqudens {

  /*!
  * @verbatim embed:rst:leading-asterisk
  * String utility class.
  *
  * #. Item-3
  * #. Item-4
  * @endverbatim
  */
  class EXQUDENS_EXPORT Strings {

    public:

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from begin of the string.
      * @endverbatim
      */
      static std::string ltrim(const std::string& value);

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from end of the string.
      * @endverbatim
      */
      static std::string rtrim(const std::string& value);

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from begin and end of the string.
      * @endverbatim
      */
      static std::string trim(const std::string& value);

  };

}
