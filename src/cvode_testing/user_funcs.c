
#include <stdio.h>

/* Header files with a description of contents used */

#include <cvode/cvode.h>             /* prototypes for CVODE fcts., consts. */
#include <nvector/nvector_serial.h>  /* serial N_Vector types, fcts., macros */
#include <cvode/cvode_dense.h>       /* prototype for CVDense */
#include <sundials/sundials_dense.h> /* definitions DlsMat DENSE_ELEM */
#include <sundials/sundials_types.h> /* definition of type realtype */

#include <assert.h>

#include "user_defs.h"

#define Y1    RCONST(1.0)      /* initial y components */
#define Y2    RCONST(0.0)
#define Y3    RCONST(0.0)


#define ATOL1 RCONST(1.0e-8)   /* vector absolute tolerance components */
#define ATOL2 RCONST(1.0e-14)
#define ATOL3 RCONST(1.0e-6)


class MyClass{

};


void PrintOutput(realtype t, realtype y1, realtype y2, realtype y3);


int setup_initial_states(N_Vector y)
{
  /* Initialize y */
  Ith(y,1) = Y1;
  Ith(y,2) = Y2;
  Ith(y,3) = Y3;
}

int setup_tolerances(N_Vector abstol)
{
  /* Set the scalar relative tolerance */
  //reltol = RTOL;
  /* Set the vector absolute tolerance */
  Ith(abstol,1) = ATOL1;
  Ith(abstol,2) = ATOL2;
  Ith(abstol,3) = ATOL3;

}


int loop_function(float t, N_Vector y)
{
    printf("Loop function: %f", t);
    PrintOutput(t, Ith(y,1), Ith(y,2), Ith(y,3));

}





int f(realtype t, N_Vector y, N_Vector ydot, void *user_data)
{
  realtype y1, y2, y3, yd1, yd3;

  y1 = Ith(y,1); y2 = Ith(y,2); y3 = Ith(y,3);

  yd1 = Ith(ydot,1) = RCONST(-0.04)*y1 + RCONST(1.0e4)*y2*y3;
  yd3 = Ith(ydot,3) = RCONST(3.0e7)*y2*y2;
        Ith(ydot,2) = -yd1 - yd3;

  return(0);
}

/*
 * g routine. Compute functions g_i(t,y) for i = 0,1. 
 */


/*
 * Jacobian routine. Compute J(t,y) = df/dy. *
 */

int Jac(long int N, realtype t,
               N_Vector y, N_Vector fy, DlsMat J, void *user_data,
               N_Vector tmp1, N_Vector tmp2, N_Vector tmp3)
{
  realtype y1, y2, y3;

  y1 = Ith(y,1); y2 = Ith(y,2); y3 = Ith(y,3);

  IJth(J,1,1) = RCONST(-0.04);
  IJth(J,1,2) = RCONST(1.0e4)*y3;
  IJth(J,1,3) = RCONST(1.0e4)*y2;
  IJth(J,2,1) = RCONST(0.04); 
  IJth(J,2,2) = RCONST(-1.0e4)*y3-RCONST(6.0e7)*y2;
  IJth(J,2,3) = RCONST(-1.0e4)*y2;
  IJth(J,3,2) = RCONST(6.0e7)*y2;

  return(0);
}

























int do_integrate(float t_start, float t_stop, int n_points);
int main()
{
    do_integrate(0.0, 10000.0, 100);
}
