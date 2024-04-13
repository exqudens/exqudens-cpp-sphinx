/*!
* @file exqudens/Strings.hpp
* @brief String processing.
* @copyright Copyright-Line-1
* @n
* Copyright-Line-2
* Copyright-Line-3
* @author Exqudens
* @date 2023
*/

#pragma once

#include <string>

#include "exqudens/export.hpp"

namespace exqudens {

  /*!
  * @brief String utility class.
  *
  * -# Number-Item-1
  * -# Number-Item-2
  *     -# Nested-Number-Item-1
  *     -# Nested-Number-Item-2
  *         -# Nested-Nested-Number-Item-1
  *         -# Nested-Nested-Number-Item-1
  *
  * - Bullet-Item-1
  * - Bullet-Item-2
  *     - Nested-Bullet-Item-1
  *     - Nested-Bullet-Item-2
  *         - Nested-Nested-Bullet-Item-1
  *         - Nested-Nested-Bullet-Item-2
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
  *
  * @image xml structure-1.png "My application" width=3cm
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
      *    (a + b)^3 = a^3 + 3ab + b^3
      *
      * Formula :math:`a^3 + b^3 = c^3`
      * @endverbatim
      *
      * @return Result string.
      */
      static std::string ltrim(
          const std::string& value //!< Input string.
      );

      /*!
      * @brief Remove all spaces from end of the string.
      *
      * - Bullet-Item-7
      *
      * @return Result string.
      */
      static std::string rtrim(
          const std::string& value //!< Input string.
      );

      /*!
      * @verbatim embed:rst:leading-asterisk
      * Remove all spaces from begin and end of the string.
      * @endverbatim
      *
      * @return Result string.
      */
      static std::string trim(
          const std::string& value //!< Input string.
      );

  };

}
