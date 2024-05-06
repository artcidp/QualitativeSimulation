# QSIM: Qualitative Simulation

This is a python implementation of the Qualitative Simulation algorithm QSIM, adapted from: 
B. Kuipers, Qualitative Reasoning: Modeling and Simulation with Incomplete Knowledge
(Artificial Intelligence). Cambridge, Mass.: MIT Press, 1994, ISBN: 978-0-262-11190-4


<!-- USAGE EXAMPLES -->
## Basic usage exmaple

1. Define basic landmark values
```python
from QSIM import *

zero=landmark_value("0",0)
inf=landmark_value("inf",1,is_finite=False)
neg_inf=landmark_value("-inf",-1,is_finite=False)
one=landmark_value("1",Sign(1))
```	

2. Define quantity spaces for each variable
```python

#time
t0=landmark_value("t0",0)
t_qs=quantity_space("t",[t0,inf])

#dt
dt_qs=quantity_space(variable="dt",landmarks_list=[zero,one])
dt_qs.set_maximum_limit(one)
dt_qs.set_minimum_limit(zero)

#x
x0=landmark_value("x0",1)
x_qs=quantity_space("x",[neg_inf,zero,x0,inf])

#vx
vx0=landmark_value("vx0",1)
vx_qs=quantity_space("vx",[neg_inf,zero,inf])

#ax
ax0=landmark_value("ax0",-1)
ax_qs=quantity_space("ax",[neg_inf,ax0,zero,inf])
```

3. Define qualitative constraints
```python
dt_x_vx=Derivative(quantity_spaces=[x_qs,vx_qs])
dt_vx_ax=Derivative(quantity_spaces=[vx_qs,ax_qs])
mminus_ax_x=Minus([ax_qs,x_qs])

dt_t_dt=Derivative(quantity_spaces=[t_qs,dt_qs])
const_dt_pos=Constant(quantity_spaces=[dt_qs],current_value=one)
```

4. Define Qualitative Differential Equation (V,Q,C,T) and initial state
```python
all_q_spaces=[t_qs,x_qs,vx_qs,ax_qs,dt_qs]
V=[qs.variable for qs in all_q_spaces]

Q={}
for qs in all_q_spaces:
    Q[qs.variable]=qs

C=[dt_x_vx,dt_vx_ax,mminus_ax_x,dt_t_dt,const_dt_pos]

T=[False] #null transition

Dbar={'t':qualitative_value(t0,None),'x':qv_x0,'vx':qualitative_value(zero,None),'ax':qualitative_value(ax0,None)} 
initial_conditions_state=Qualitative_State(Dbar)
```

5. Generate behavior tree
```python
root=QSIM(V,Q,C,T,initial_conditions_state,time_var="t",cycle_match_criteria="strong",max_breadth=3000,max_depth=9)
for pre, fill, node in RenderTree(root): 
        if node.name["cycle_loc"]==None:
            print(str(pre)+str(node.name["loc"])+":"+str({key: node.name["State"].get(key,qv_none_both) for key in V})+" ") 
        else:
            print(str(pre)+str(node.name["loc"])+":"+str({key: node.name["State"].get(key,qv_none_both) for key in V})+" -> "+str(node.name["cycle_loc"]))

```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



