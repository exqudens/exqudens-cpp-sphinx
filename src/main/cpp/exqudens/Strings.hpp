#pragma once

#include <string>

#include "exqudens/export.hpp"

namespace exqudens {

  /*!
  * @brief String utility class.
  *
  * -# Number-Item-1
  * -# Number-Item-2
  *
  * - Bullet-Item-1
  * - Bullet-Item-2
  *
  * | Right | Center | Left  |
  * | ----: | :----: | :---- |
  * | 10    | 10     | 10    |
  * | 100   | 100    | 100   |
  * | ^     | 1000   | 1000  |
  * | 1000  |||
  *
  * @f[
  *    (a + b)^2 = a^2 + 2ab + b^2
  * @f]
  *
  * where @f$a = 2@f$
  */
  class EXQUDENS_EXPORT Strings {

    public:

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from begin of the string.
      *
      * #. Number-Item-5
      * #. Number-Item-6
      *
      * .. math::
      *
      *    (a + b)^2 = a^2 + 2ab + b^2
      *
      * Formula :math:`a^2 + b^2 = c^2`
      * @endverbatim
      */
      static std::string ltrim(const std::string& value);

      /*!
      * @brief Remove all spaces from end of the string.
      *
      * - Bullet-Item-7
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
