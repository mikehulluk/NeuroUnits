//#include "real.hpp"
#include "/home/mh735/mpfr_real/mpfr_real_v0.0.9-alpha/real.hpp"


int main () {
  mpfr::real<4096> a = "1.23456789";
  mpfr::real<4096> b = 5.;
  std::cout << sin(2 * pow(a, b)) << std::endl;

  return 0;
}
