


#define NEQ 3
#define RTOL  RCONST(1.0e-4)   /* scalar relative tolerance            */


#define Ith(v,i)    NV_Ith_S(v,i-1)       /* Ith numbers components 1..NEQ */
#define IJth(A,i,j) DENSE_ELEM(A,i-1,j-1) /* IJth numbers rows,cols 1..NEQ */



// In user_funcs.c:
int setup_initial_states(N_Vector y);
int setup_tolerances(N_Vector abstol);
int loop_function(float t, N_Vector y);


int f(realtype t, N_Vector y, N_Vector ydot, void *user_data);

int Jac(long int N, realtype t,
               N_Vector y, N_Vector fy, DlsMat J, void *user_data,
               N_Vector tmp1, N_Vector tmp2, N_Vector tmp3);
