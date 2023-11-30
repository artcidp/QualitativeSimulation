from .Core import *
import itertools
import inspect

# print(inspect.getmembers(Core, inspect.isfunction))
# print(inspect.getmembers(Core, inspect.isclass))

# print([o for o in inspect.getmembers(inspect.currentframe().f_globals) if inspect.isfunction(o[1])])
# print([o for o in inspect.getmembers(inspect.currentframe().f_globals) if inspect.isclass(o[1])])

def evaluate_conditions(p,if_all_None="raise"):
    assert if_all_None in ["raise","ignore","reject","None"]
    # Remove None values from the list
    v = [x for x in p if x is not None]
    if len(v)==0:
        if if_all_None=="ignore":
            return True
        elif if_all_None=="reject":
            return False
        elif if_all_None=="None":
            return None
        else:
            raise ValueError("All conditions returned None")
    else:
        # Check if there is at least one False value
        return all(v)
    

class Derivative: # d/dt x = y
    def __init__(self,quantity_spaces,if_all_None="raise") -> None:
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==2 and isinstance(quantity_spaces[0],quantity_space) and isinstance(quantity_spaces[0],quantity_space), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        self.corresponding_values = set()
        
        assert len(self.variables)==2 and isinstance(self.variables[0],str) and isinstance(self.variables[1],str), "Variables are not correctly specified"
        self.if_all_None=if_all_None
        
    
    def __str__(self):
        if len(self.corresponding_values)==0:
            return "⟨ (d/dt "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ (d/dt "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return "⟨ (d/dt "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ (d/dt "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"

    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==2 and isinstance(new_quantity_spaces[0],quantity_space) and isinstance(new_quantity_spaces[1],quantity_space),  "Quantity spaces are incorrectly defined"
        assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable and new_quantity_spaces[1].variable == self.quantity_spaces[1].variable, "New Quantity spaces don't correspond to the assigned variables"
        self.quantity_spaces = new_quantity_spaces

    def check_condition1(self,x_qv: qualitative_value,y_qv: qualitative_value): #[𝑥']=[𝑦] for now this will only check one tuple at a time
        #assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
            #assert x_qv.q_space.variable==self.variables[0] and y_qv.q_space.variable==self.variables[1], "Qualitative Values provided don't match with constraint variables"
        return x_qv.qdir == y_qv.sign

        # if isinstance(y_qv.qmag,landmark_value):
        #     return x_qv.qdir == y_qv.qmag.sign
        # else: #y_qv.qmag is a tuple of landmarks
        #     return x_qv.qdir == sign_of_interval(y_qv)

    def evaluate_tuple(self,x_qv: qualitative_value,y_qv: qualitative_value,add_if_satisfies=False,cv_type="landmarks" ,printing=False):
        assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]) and y_qv.is_in_q_space(self.quantity_spaces[1]), "A value does not correspond to the quantity space"

        conditions_list=[self.check_condition1(x_qv,y_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)

        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value and y_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv,y_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv,y_qv))
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) satisfies the constraint. Results:{conditions_list}")
        else:
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) does not satisfy the constraint. Results:{conditions_list}")
        
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks",printing=False):
        x_var=self.variables[0]
        y_var=self.variables[1]
        return self.evaluate_tuple(x_qv=state[x_var],y_qv=state[y_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)
    
    #add new value

    #check conddition
    #return condition for latest value

    #return all previous values that satisfy the condition (corresponding values)

#basic landmarks
# zero=landmark_value("0",0)
# inf=landmark_value("inf",1,is_finite=False)
# neg_inf=landmark_value("-inf",-1,is_finite=False)
# vy0=landmark_value("vy0",1)
# y_qs=quantity_space("y",[neg_inf,zero,inf])
# vy_qs=quantity_space("vy",[neg_inf,zero,vy0,inf])

# dt_y_vy=Derivative(quantity_spaces=[y_qs,vy_qs])

# #Dbar={'t':qv_t0,'y':qv_y0,'vy':qv_vy0,'ay':qv_none_both}
# Q=[y_qs,vy_qs]
# Domains=domain_restriction(Q)

# all_states_iterator = (dict(zip(Domains.keys(), s)) for s in itertools.product(*Domains.values())) 
# for state in all_states_iterator:
#     y_qv=state["y"]
#     vy_qv=state["vy"]

#     dt_y_vy.evaluate_tuple(y_qv,vy_qv,printing=False,add_if_satisfies=True)
# print(dt_y_vy.corresponding_values)

class Constant: # const x = x_0
    def __init__(self,quantity_spaces,current_value,if_all_None="raise") -> None: #considers that changing the fixed/current value might require a different instance, for now, the current value is mandatory
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==1 and isinstance(quantity_spaces[0],quantity_space), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        self.corresponding_values = set()
        self.current_value = current_value
        self.if_all_None=if_all_None

        if isinstance(self.current_value,qualitative_value): #must be landmark value or tuple of landmarks
            self.current_value = self.current_value.qmag

        assert (isinstance(self.variables,tuple) or isinstance(self.variables,list)) and len(self.variables)==1 and isinstance(self.variables[0],str), "Variables are not correctly specified"
        if isinstance(self.variables,tuple):
            self.variables=self.variables[0] 
        
    def __str__(self):
        if len(self.corresponding_values)==0:
            return "⟨ (const "+str(self.variables[0])+")⟩"
        else:
            return  "⟨ (const "+str(self.variables[0])+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return "⟨ (const "+str(self.variables[0])+")⟩"
        else:
            return  "⟨ (const "+str(self.variables[0])+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==1 and isinstance(new_quantity_spaces[0],quantity_space),  "Quantity spaces are incorrectly defined"
        assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable, "New Quantity space doesn't correspond to the assigned variable"
        self.quantity_spaces = new_quantity_spaces

    def check_condition1(self,x_qv: qualitative_value): #[𝑥˙]=0
        #assert x_qv.is_complete, "Qualitative Value must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
            #assert x_qv.q_space.variable==self.variables, "Qualitative Value provided doesn't match with constraint variable"
        return x_qv.qdir == Sign(0)
    
    def check_condition2(self,x_qv: qualitative_value): #[𝑥]𝑥𝑖=0,  if xi is the initial value
        #assert x_qv.is_complete, "Qualitative Value must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
            #assert x_qv.q_space.variable==self.variables, "Qualitative Value provided doesn't match with constraint variable"
        #if isinstance(x_qv.qmag,qualitative_value):
        return x_qv.qmag == self.current_value
    

    def evaluate_tuple(self,x_qv: qualitative_value, add_if_satisfies=False,cv_type="landmarks", printing=False):
        assert x_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]),  "A value does not correspond to the quantity space"
        
        conditions_list=[self.check_condition1(x_qv), self.check_condition2(x_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)
        #evaluation_result=self.check_condition1(x_qv) and self.check_condition2(x_qv)
        #print(x_qv,self.check_condition1(x_qv), self.check_condition2(x_qv))
        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv))
        else:
            if printing==True:
                print(f"Tuple ({x_qv}) does not satisfy the constraint. Results:{conditions_list}")
        
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks", printing=False):
        x_var=self.variables[0]
        #y_var=self.variables[1]
        return self.evaluate_tuple(x_qv=state[x_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)
    


#class Derivative: # d/dt x = y
class M: # y=f(x), f in M+/-
    def __init__(self,quantity_spaces,type: Sign,if_all_None="ignore") -> None:
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==2 and isinstance(quantity_spaces[0],quantity_space) and isinstance(quantity_spaces[1],quantity_space), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        
        self.corresponding_values = set()
        self.type = type

        assert type==Sign(1) or type==Sign(-1), "Invalid M constraint type"
        assert len(self.variables)==2 and isinstance(self.variables[0],str) and isinstance(self.variables[1],str), "Variables are not correctly specified"

        self.if_all_None=if_all_None
        #inf_landmark=landmark_value("inf",Sign(1),is_finite=False)
        #neg_inf_landmark=landmark_value("-inf",Sign(-1),is_finite=False)
        
        # qvals_list=[]
        # for qs in self.quantity_spaces:
        #     qvals_list.append([qualitative_value(qs.maximum_limit,Sign(qd)) for qd in [-1,0,1]])
        # for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
        #     self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)
        
        if type==Sign(1):
            self.type_str = "M+"

            qvals_list=[] #add inf, inf
            if not self.quantity_spaces[0].maximum_limit.is_finite and not self.quantity_spaces[1].maximum_limit.is_finite:
                for qs in self.quantity_spaces:
                    qvals_list.append([qualitative_value(qs.maximum_limit,Sign(qd)) for qd in [-1,0,1]])
                for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
                    self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)

            qvals_list=[] #add -inf,-inf
            if not self.quantity_spaces[0].minimum_limit.is_finite and not self.quantity_spaces[1].minimum_limit.is_finite:
                for qs in self.quantity_spaces:
                    qvals_list.append([qualitative_value(qs.minimum_limit,Sign(qd)) for qd in [-1,0,1]])
                for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
                    self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)


        else: #sign(-1)
            self.type_str = "M-"

            qvals_list=[] #add inf, -inf
            if not self.quantity_spaces[0].maximum_limit.is_finite and not self.quantity_spaces[1].minimum_limit.is_finite:
                qvals_list=[[qualitative_value(self.quantity_spaces[0].maximum_limit,Sign(qd)) for qd in [-1,0,1]]] #inf
                qvals_list.append([qualitative_value(self.quantity_spaces[1].minimum_limit,Sign(qd)) for qd in [-1,0,1]]) #-inf
            for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
                self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)

            qvals_list=[] #add -inf, inf
            if not self.quantity_spaces[0].minimum_limit.is_finite and not self.quantity_spaces[1].maximum_limit.is_finite:
                qvals_list=[[qualitative_value(self.quantity_spaces[0].minimum_limit,Sign(qd)) for qd in [-1,0,1]]]
                qvals_list.append([qualitative_value(self.quantity_spaces[1].maximum_limit,Sign(qd)) for qd in [-1,0,1]])
            for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
                self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)
    
    def __str__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ("+self.type_str+" "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ("+self.type_str+" "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ("+self.type_str+" "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ("+self.type_str+" "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==2 and isinstance(new_quantity_spaces[0],quantity_space) and isinstance(new_quantity_spaces[1],quantity_space),  "Quantity spaces are incorrectly defined"
        assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable and new_quantity_spaces[1].variable == self.quantity_spaces[1].variable, "New Quantity spaces don't correspond to the assigned variables"
        self.quantity_spaces = new_quantity_spaces
        
    
    def check_condition1(self,x_qv: qualitative_value, y_qv: qualitative_value): #[𝑥˙]=+/-[y˙]
        # assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
            #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        # if y_qv.q_space!=None:
            #assert y_qv.q_space.variable==self.variables[1], "Qualitative Value provided doesn't match with constraint variable"
            # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        
        if self.type==Sign(1):
            return x_qv.qdir == y_qv.qdir
        else:
            return x_qv.qdir == -y_qv.qdir
    
    def check_condition2(self,x_qv: qualitative_value, y_qv: qualitative_value): #[𝑥]𝑥𝑖=+/-[y]y𝑖,  if xi,yi are corresponding values
        #assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        #assert x_qv.q_space!=None or y_qv.q_space!=None, "Qualitative Values must have a Quantity Space assinged for comparison of corresponding values"
        
        # assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        
        
        consistent=True
        for xi_qv, yi_qv in self.corresponding_values:
            if self.type==Sign(1):
                condition = (x_qv.sign_wr_value(xi_qv,q_space=self.quantity_spaces[0]) == y_qv.sign_wr_value(yi_qv,q_space=self.quantity_spaces[1]))
            else:
                condition = (x_qv.sign_wr_value(xi_qv,q_space=self.quantity_spaces[0]) == -(y_qv.sign_wr_value(yi_qv,q_space=self.quantity_spaces[1])))
            if condition==False:
                consistent=False
        return consistent
    

    def evaluate_tuple(self,x_qv: qualitative_value,y_qv: qualitative_value,add_if_satisfies=False,cv_type="landmarks", printing=False):
        assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]) and y_qv.is_in_q_space(self.quantity_spaces[1]), "A value does not correspond to the quantity space"

        conditions_list=[self.check_condition1(x_qv,y_qv), self.check_condition2(x_qv,y_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)

        #evaluation_result=self.check_condition1(x_qv,y_qv) and self.check_condition2(x_qv,y_qv)

        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value and y_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv,y_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv,y_qv))    
        
        
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) satisfies the constraint. Results:{conditions_list}")
        else:
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) does not satisfy the constraint. Results:{conditions_list}")
        
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks",printing=False):
        x_var=self.variables[0]
        y_var=self.variables[1]
        return self.evaluate_tuple(x_qv=state[x_var],y_qv=state[y_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)
    

class Plus(M): #child class of M+, must have (0,0) as corresponding value (therefore equivalent to M+0 constraint)
    def __init__(self, quantity_spaces) -> None:
        super().__init__(quantity_spaces, type=Sign(1))
        
        zero_landmark=landmark_value("0",Sign(0))
        qvals_list=[]
        for i in range(2): #len(self.quantity_spaces):
            qvals_list.append([qualitative_value(zero_landmark,Sign(qd)) for qd in [-1,0,1]])
        for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
            self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)


class Minus(M): #child class of M-, must have (0,0) as corresponding value (therefore equivalent to M-0 constraint)
    def __init__(self, quantity_spaces) -> None:
        super().__init__(quantity_spaces, type=Sign(-1))
        
        zero_landmark=landmark_value("0",Sign(0))
        qvals_list=[]
        for i in range(2): #len(self.quantity_spaces):
            qvals_list.append([qualitative_value(zero_landmark,Sign(qd)) for qd in [-1,0,1]])
        for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
            self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)


#must have (0,0,0) as a corresponding value tuple
class Add: # x+y = z
    def __init__(self,quantity_spaces,if_all_None='raise') -> None:
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==3 and all([isinstance(qs,quantity_space) for qs in self.quantity_spaces]), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        self.corresponding_values = set()
        
        assert len(self.variables)==3 and all([isinstance(var,str) for var in self.variables]), "Variables are not correctly specified"
        self.if_all_None=if_all_None

        #initialize with (0,0,0) as a corresponding value tuple (check all combinations)
        zero_landmark=landmark_value("0",Sign(0))
        qvals_list=[]
        for qs in self.quantity_spaces:
            qvals_list.append([qualitative_value(zero_landmark,Sign(qd)) for qd in [-1,0,1]])
        for x_qv,y_qv,z_qv in itertools.product(qvals_list[0],qvals_list[1],qvals_list[2]):
            self.evaluate_tuple(x_qv,y_qv,z_qv,add_if_satisfies=True)

    
    def __str__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ( ADD "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ( ADD "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ( ADD "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ( ADD "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==3 and all([isinstance(qs,quantity_space) for qs in new_quantity_spaces]),  "Quantity spaces are incorrectly defined"
        assert all([new_quantity_spaces[i].variable == self.quantity_spaces[i].variable for i in [0,1,2]]), "New Quantity spaces don't correspond to the assigned variables"
        #assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable and new_quantity_spaces[1].variable == self.quantity_spaces[1].variable, "New Quantity spaces don't correspond to the assigned variables"
        self.quantity_spaces = new_quantity_spaces
        
    
    def check_condition1(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[𝑥˙]+[y˙]=[z˙]
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # if z_qv.q_space!=None:
        #     assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        left_side = (x_qv.qdir + y_qv.qdir)
        right_side = z_qv.qdir
        if (left_side==Sign(None) or right_side==Sign(None)):
            return None
        else:
            return left_side == right_side
    
    def check_condition2(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[𝑥]𝑥𝑖 + [y]y𝑖 = [z]z𝑖,  if xi,yi,zi are corresponding values
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # assert x_qv.q_space!=None or y_qv.q_space!=None or z_qv.q_space!=None, "Qualitative Values must have a Quantity Space assinged for comparison of corresponding values"
        
        # assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        consistent=True
        for xi_qv, yi_qv, zi_qv in self.corresponding_values:
            left_side = (x_qv.sign_wr_value(xi_qv,q_space=self.quantity_spaces[0]) + y_qv.sign_wr_value(yi_qv,self.quantity_spaces[1])) 
            right_side = z_qv.sign_wr_value(zi_qv,self.quantity_spaces[2])
            if (left_side==Sign(None) or right_side==Sign(None)) and consistent in [True,None]: #only becomes None if it is not False
                consistent=None
            elif right_side!=left_side:
                consistent=False

        return consistent
    
    
    def check_condition3(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[𝑥]oo + [y]oo = [z]oo,  
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # if z_qv.q_space!=None:
        #     assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        left_side = (x_qv.sign_wr_infinity() + y_qv.sign_wr_infinity())
        right_side = z_qv.sign_wr_infinity()
        if left_side==Sign(None) and x_qv.sign_wr_infinity() in [Sign(1),Sign(-1)] and y_qv.sign_wr_infinity() in [Sign(1),Sign(-1)]: #discard [oo] + [-oo] cases
            return False
        elif (left_side==Sign(None) or right_side==Sign(None)):
            return None
        else:
            return left_side == right_side

    
    
    def evaluate_tuple(self,x_qv: qualitative_value,y_qv: qualitative_value, z_qv: qualitative_value,add_if_satisfies=False,cv_type="landmarks", printing=False):
        assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]) and y_qv.is_in_q_space(self.quantity_spaces[1]) and z_qv.is_in_q_space(self.quantity_spaces[2]), "A value does not correspond to the quantity space"

        #true and none returns none; false and none returns false
        conditions_list=[self.check_condition1(x_qv,y_qv,z_qv), self.check_condition2(x_qv,y_qv,z_qv), self.check_condition3(x_qv,y_qv,z_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)

        #evaluation_result=self.check_condition1(x_qv,y_qv,z_qv) and self.check_condition2(x_qv,y_qv,z_qv) and self.check_condition3(x_qv,y_qv,z_qv)

        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value and y_qv.qmag_type==landmark_value and z_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv,y_qv,z_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv,y_qv,z_qv))
            if printing==True:
                print(f"Tuple ({x_qv,y_qv,z_qv}) satisfies the constraint. Results:{conditions_list}")
        else:
            if printing==True:
                print(f"Tuple ({x_qv,y_qv,z_qv}) does not satisfy the constraint. Results:{conditions_list}")
    
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks",printing=False):
        x_var=self.variables[0]
        y_var=self.variables[1]
        z_var=self.variables[2]
        return self.evaluate_tuple(x_qv=state[x_var],y_qv=state[y_var],z_qv=state[z_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)
    



class Mult: # x*y = z
    def __init__(self,quantity_spaces,if_all_None="raise") -> None:
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==3 and all([isinstance(qs,quantity_space) for qs in self.quantity_spaces]), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        self.corresponding_values = set()
        #self.type = type

        assert len(self.variables)==3 and all([isinstance(var,str) for var in self.variables]), "Variables are not correctly specified"

        self.if_all_None=if_all_None

        
    
    def __str__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ( MULT "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ( MULT "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return "⟨ ( MULT "+" ".join(self.variables)+")⟩"
        else:
            return  "⟨ ( MULT "+" ".join(self.variables)+")  "+', '.join(map(str, self.corresponding_values))+"⟩"
        

    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==3 and all([isinstance(qs,quantity_space) for qs in new_quantity_spaces]),  "Quantity spaces are incorrectly defined"
        assert all([new_quantity_spaces[i].variable == self.quantity_spaces[i].variable for i in [0,1,2]]), "New Quantity spaces don't correspond to the assigned variables"
        #assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable and new_quantity_spaces[1].variable == self.quantity_spaces[1].variable, "New Quantity spaces don't correspond to the assigned variables"
        self.quantity_spaces = new_quantity_spaces

    def check_condition1(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[𝑥][y]=[z], except [0][oo] (undefined)
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # if z_qv.q_space!=None:
        #     assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        if (x_qv.sign==Sign(0) and y_qv.is_finite==False) or (y_qv.sign==Sign(0) and x_qv.is_finite==False): #undefined operation
            return False #previously returned none 
        else:
            return x_qv.sign*y_qv.sign == z_qv.sign
    

    def check_condition2(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[𝑥˙][y]+[x][y˙]=[z˙]
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # if z_qv.q_space!=None:
        #     assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        left_side = (x_qv.qdir*y_qv.sign)+(x_qv.sign*y_qv.qdir)
        right_side = z_qv.qdir
        if left_side==Sign(None) or right_side==Sign(None) or (x_qv.qdir==Sign(0) and y_qv.is_finite==False) or (y_qv.qdir==Sign(0) and x_qv.is_finite==False):
            return None
        else:
            return left_side == right_side
        


    def check_condition3(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[|𝑥|]|𝑥𝑖| + [|y|]|y𝑖| = [|z|]|z𝑖|,  if xi,yi,zi are corresponding values
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # assert x_qv.q_space!=None or y_qv.q_space!=None or z_qv.q_space!=None, "Qualitative Values must have a Quantity Space assinged for comparison of corresponding values"
        
        # assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        consistent=True
        for xi_qv, yi_qv, zi_qv in self.corresponding_values:
            left_side = (x_qv.sign_abs_wr_value_abs(xi_qv,q_space=self.quantity_spaces[0]) + y_qv.sign_abs_wr_value_abs(yi_qv,q_space=self.quantity_spaces[1])) 
            right_side = z_qv.sign_abs_wr_value_abs(zi_qv,q_space=self.quantity_spaces[2])
            if (left_side==Sign(None) or right_side==Sign(None)) and consistent in [True,None]: #only becomes None if it is not False
                consistent=None
            elif right_side!=left_side:
                consistent=False
        return consistent
    
    
    def check_condition4(self,x_qv: qualitative_value, y_qv: qualitative_value, z_qv: qualitative_value): #[log|𝑥|]oo + [log|y|]oo = [log|z|]oo,  
        # assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # if y_qv.q_space!=None:
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        # if z_qv.q_space!=None:
        #     assert z_qv.q_space == self.quantity_spaces[2], "Quantity space of third variable doesn't match that of third value"
        
        left_side = x_qv.sign_log_abs_wr_infinity() + y_qv.sign_log_abs_wr_infinity()
        right_side = z_qv.sign_log_abs_wr_infinity()
        if left_side==Sign(None) or right_side==Sign(None):
            return None
        else:
            return left_side == right_side
    

    def evaluate_tuple(self,x_qv: qualitative_value,y_qv: qualitative_value, z_qv: qualitative_value,add_if_satisfies=False,cv_type="landmarks", printing=False):
        assert x_qv.is_complete and y_qv.is_complete and z_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]) and y_qv.is_in_q_space(self.quantity_spaces[1]) and z_qv.is_in_q_space(self.quantity_spaces[2]), "A value does not correspond to the quantity space"

        #true and none returns none; false and none returns false
        conditions_list=[self.check_condition1(x_qv,y_qv,z_qv), self.check_condition2(x_qv,y_qv,z_qv), self.check_condition3(x_qv,y_qv,z_qv), self.check_condition4(x_qv,y_qv,z_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)
        #evaluation_result=self.check_condition1(x_qv,y_qv,z_qv) and self.check_condition2(x_qv,y_qv,z_qv) and self.check_condition3(x_qv,y_qv,z_qv) and self.check_condition4(x_qv,y_qv,z_qv)

        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value and y_qv.qmag_type==landmark_value and z_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv,y_qv,z_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv,y_qv,z_qv))
            if printing==True:
                print(f"Tuple ({x_qv,y_qv,z_qv}) satisfies the constraint. Results:{conditions_list}")
        else:
            if printing==True:
                print(f"Tuple ({x_qv,y_qv,z_qv}) does not satisfy the constraint. Results:{conditions_list}")
        
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks",printing=False):
        x_var=self.variables[0]
        y_var=self.variables[1]
        z_var=self.variables[2]
        return self.evaluate_tuple(x_qv=state[x_var],y_qv=state[y_var],z_qv=state[z_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)
    


class U: # y=f(x), f in U+/-, U+ convex, U- concave, a: point where derivative is zero, b: extreme value b=f(a)
    def __init__(self,quantity_spaces,type: Sign,a: landmark_value,b: landmark_value,if_all_None="raise") -> None:
        self.quantity_spaces = quantity_spaces
        assert len(self.quantity_spaces)==2 and isinstance(quantity_spaces[0],quantity_space) and isinstance(quantity_spaces[1],quantity_space), "Quantity spaces are incorrectly defined"
        self.variables = [qs.variable for qs in quantity_spaces]
        
        self.a = a
        self.b = b
        self.a_qv = qualitative_value(self.a,None)
        self.b_qv = qualitative_value(self.b,None)

        self.corresponding_values = set()
        self.type = type

        assert type==Sign(1) or type==Sign(-1), "Invalid U constraint type"
        assert len(self.variables)==2 and isinstance(self.variables[0],str) and isinstance(self.variables[1],str), "Variables are not correctly specified"
        assert a in quantity_spaces[0].landmarks and b in quantity_spaces[1].landmarks, "Constraint parameters must be landmark values in the corresponding quantity spaces"

        self.if_all_None=if_all_None

        #inf_landmark=landmark_value("inf",Sign(1),is_finite=False)
        #neg_inf_landmark=landmark_value("-inf",Sign(-1),is_finite=False)
        
        # qvals_list=[]
        # for qs in self.quantity_spaces:
        #     qvals_list.append([qualitative_value(qs.maximum_limit,Sign(qd)) for qd in [-1,0,1]])
        # for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
        #     self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)
        
        if type==Sign(1):
            self.type_str = "U+"

            # if not self.quantity_spaces[0].maximum_limit.is_finite and not self.quantity_spaces[1].minimum_limit.is_finite:
            #     qvals_list=[[qualitative_value(self.quantity_spaces[0].maximum_limit,Sign(qd)) for qd in [-1,0,1]]]
            #     qvals_list.append([qualitative_value(self.quantity_spaces[1].minimum_limit,Sign(qd)) for qd in [-1,0,1]])
            # for x_qv,y_qv in itertools.product(qvals_list[0],qvals_list[1]):
            #     self.evaluate_tuple(x_qv,y_qv,add_if_satisfies=True)
        else: #sign(-1)
            self.type_str = "U-"

    
    def __str__(self):
        if len(self.corresponding_values)==0:
            return f"⟨ ({self.type_str}_{(self.a,self.b)} {' ' .join(self.variables)})⟩"
        else:
            return  f"⟨ ({self.type_str}_{(self.a,self.b)} {' ' .join(self.variables)})  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    
    def __repr__(self):
        if len(self.corresponding_values)==0:
            return f"⟨ ({self.type_str}_{(self.a,self.b)} {' ' .join(self.variables)})⟩"
        else:
            return  f"⟨ ({self.type_str}_{(self.a,self.b)} {' ' .join(self.variables)})  "+', '.join(map(str, self.corresponding_values))+"⟩"
        
    def update_quantity_spaces(self,new_quantity_spaces):
        assert len(new_quantity_spaces)==2 and isinstance(new_quantity_spaces[0],quantity_space) and isinstance(new_quantity_spaces[1],quantity_space),  "Quantity spaces are incorrectly defined"
        assert new_quantity_spaces[0].variable == self.quantity_spaces[0].variable and new_quantity_spaces[1].variable == self.quantity_spaces[1].variable, "New Quantity spaces don't correspond to the assigned variables"
        self.quantity_spaces = new_quantity_spaces
        
    
    def check_condition1(self,x_qv: qualitative_value, y_qv: qualitative_value): #[𝑥˙]=+/-[y˙]
        # assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        # if x_qv.q_space!=None:
        #     assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        #     #assert x_qv.q_space.variable==self.variables[0], "Qualitative Value provided doesn't match with constraint variable"
        # if y_qv.q_space!=None:
        #     #assert y_qv.q_space.variable==self.variables[1], "Qualitative Value provided doesn't match with constraint variable"
        #     assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        
        if self.type==Sign(1):
            if x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0): #x<a
                return x_qv.qdir == -y_qv.qdir
            elif x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0): #x>a
                return x_qv.qdir == y_qv.qdir
            elif x_qv.qmag==self.a: #x=a (all derivative signs could be permited)
                return None
            else:
                raise ValueError("Invalid comparison")
        else:
            if x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0): #x<a
                return x_qv.qdir == y_qv.qdir
            elif x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0): #x>a
                return x_qv.qdir == -y_qv.qdir
            elif x_qv.qmag==self.a: #x=a (all derivative signs could be permited)
                return None
            else:
                raise ValueError("Invalid comparison")
    
    def check_condition2(self,x_qv: qualitative_value, y_qv: qualitative_value): #[𝑥]𝑥𝑖=+/-[y]y𝑖,  if xi,yi are corresponding values
        # assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        # assert x_qv.q_space!=None or y_qv.q_space!=None, "Qualitative Values must have a Quantity Space assinged for comparison of corresponding values"
        
        # assert x_qv.q_space == self.quantity_spaces[0], "Quantity space of first variable doesn't match that of first value"
        # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"
        
        
        consistent=True
        if self.type==Sign(1):
            for xi_qv, yi_qv in self.corresponding_values:
                if x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0) and xi_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0): #x<a, xi<a
                    condition = (x_qv.sign_wr_value(xi_qv,self.quantity_spaces[0]) == -y_qv.sign_wr_value(yi_qv,self.quantity_spaces[1])) #[x]_xi = -[y]_yi
                elif x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0) and xi_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0): #x>a,xi>a
                    condition = (x_qv.sign_wr_value(xi_qv,self.quantity_spaces[0]) == y_qv.sign_wr_value(yi_qv,self.quantity_spaces[1])) #[x]_xi = [y]_yi
                else:
                    condition=None
                
                if condition==None and consistent in [True,None]: #only becomes None if it is not False
                    consistent=None
                elif condition==False:
                     consistent=False
                
        else:
            for xi_qv, yi_qv in self.corresponding_values:
                if x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0) and xi_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])<Sign(0): #x<a, xi<a
                    condition = (x_qv.sign_wr_value(xi_qv,self.quantity_spaces[0]) == y_qv.sign_wr_value(yi_qv,self.quantity_spaces[1])) #[x]_xi = [y]_yi
                elif x_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0) and xi_qv.sign_wr_value(self.a_qv,self.quantity_spaces[0])>Sign(0): #x>a,xi>a
                    condition = (x_qv.sign_wr_value(xi_qv,self.quantity_spaces[0]) == -y_qv.sign_wr_value(yi_qv,self.quantity_spaces[1])) #[x]_xi = -[y]_yi
                else:
                    condition=None
                
                if condition==None and consistent in [True,None]: #only becomes None if it is not False
                    consistent=None
                elif condition==False:
                     consistent=False
                
        return consistent
    
    def check_condition3(self,x_qv: qualitative_value, y_qv: qualitative_value): #y is limited by b
        # assert y_qv.is_complete, "Qualitative Values must be complete"
        # assert y_qv.q_space!=None, "Qualitative Values must have a Quantity Space assinged for comparison of corresponding values"

        # assert y_qv.q_space == self.quantity_spaces[1], "Quantity space of second variable doesn't match that of second value"

        if self.type==Sign(1): #y>=b
            if x_qv.qmag==self.a: #x=a
                return y_qv.qmag==self.b and y_qv.qdir==Sign(0) #y=b, y'=0 (y'=x' dy/dx, and dy/dx=0, if x=a)
            else: #x!=a
                return y_qv.sign_wr_value(self.b_qv,self.quantity_spaces[1])>Sign(0)  #y>b
        else: #sign(-1) #y<=b
            if x_qv.qmag==self.a: #x=a
                return y_qv.qmag==self.b and y_qv.qdir==Sign(0) #y=b, y'=0 (y'=x' dy/dx, and dy/dx=0, if x=a)
            else: #x!=a
                return y_qv.sign_wr_value(self.b_qv,self.quantity_spaces[1])<=Sign(0) #y<b

    # def check_condition4(self,x_qv: qualitative_value, y_qv: qualitative_value): # f(a)=b
    #     if x_qv.qmag==self.a:
    #         return y_qv.qmag==self.b
    #     else:
    #         return None

    def evaluate_tuple(self,x_qv: qualitative_value,y_qv: qualitative_value,add_if_satisfies=False,cv_type="landmarks", printing=False):
        assert x_qv.is_complete and y_qv.is_complete, "Qualitative Values must be complete"
        assert x_qv.is_in_q_space(self.quantity_spaces[0]) and y_qv.is_in_q_space(self.quantity_spaces[1]), "A value does not correspond to the quantity space"

        conditions_list=[self.check_condition1(x_qv,y_qv), self.check_condition2(x_qv,y_qv), self.check_condition3(x_qv, y_qv)] #, self.check_condition4(x_qv,y_qv)]
        evaluation_result=evaluate_conditions(conditions_list,if_all_None=self.if_all_None)
        #evaluation_result=self.check_condition1(x_qv,y_qv) and self.check_condition2(x_qv,y_qv) and self.check_condition3

        if evaluation_result:
            if add_if_satisfies:
                if cv_type=="landmarks": #check if values are not tuples before adding
                    if x_qv.qmag_type==landmark_value and y_qv.qmag_type==landmark_value:
                        self.corresponding_values.add((x_qv,y_qv))
                else: #simply add the cv
                    self.corresponding_values.add((x_qv,y_qv))
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) satisfies the constraint. Results:{conditions_list}")
        else:
            if printing==True:
                print(f"Tuple ({x_qv,y_qv}) does not satisfy the constraint. Results:{conditions_list}")
        
        return evaluation_result
                
    def evaluate_state(self,state:Qualitative_State,add_if_satisfies=False,cv_type="landmarks",printing=False):
        x_var=self.variables[0]
        y_var=self.variables[1]
        return self.evaluate_tuple(x_qv=state[x_var],y_qv=state[y_var],add_if_satisfies=add_if_satisfies,cv_type=cv_type,printing=printing)