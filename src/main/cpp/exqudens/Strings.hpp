#pragma once

#include <string>

#include "exqudens/export.hpp"

namespace exqudens {

  /*!
  * @verbatim embed:rst:leading-asterisk
  * String utility class.
  *
  * #. Number-Item-3
  * #. Number-Item-4
  *
  * .. math::
  *
  *    (a + b)^2 = a^2 + 2ab + b^2
  *
  * Formula :math:`a^2 + b^2 = c^2`
  * @endverbatim
  */
  class EXQUDENS_EXPORT Strings {

    public:

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from begin of the string.
      *
      * #. Number-Item-5
      * @endverbatim
      */
      static std::string ltrim(const std::string& value);

      /*!
      * @brief Remove all spaces from end of the string.
      *
      * -# Number-Item-6
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
