from .Core import *
from .Constraints import *

from anytree import Node, RenderTree

from tqdm import tqdm
import copy, warnings


# from multiprocessing import Pool

def BF_Search(V,D,C,printing=False,add_if_satisfies=False,print_total_states=False,with_tqdm=False):
    solution_states=[]
    all_states_iterator = (Qualitative_State(dict(zip(D.keys(), s))) for s in itertools.product(*D.values())) 

    if print_total_states or with_tqdm:
        total_prod=1
        for dom in D.values():
            total_prod=total_prod*len(dom)
    if print_total_states:
        print(f"Search Space has {total_prod:,} total states")

    # with Pool() as p:
    #     args = [(state, C) for state in all_states_iterator]
    #     consistent = p.starmap(check_state_consistency, args)
    if with_tqdm==True:
        try:
            for state in tqdm(all_states_iterator,total=total_prod):
                consistent=True
                for constraint in C:
                    evaluation_result=constraint.evaluate_state(state,printing=printing,add_if_satisfies=add_if_satisfies)
                    if evaluation_result==False:
                        consistent=False
                if consistent:
                    if state.is_complete(reference_vars=V): #consistent and complete
                        solution_states.append(state)
        except Exception as e:
            raise ValueError(f"failed evaluating {constraint} on {state} with q_spaces {constraint.quantity_spaces}")
    else:
        try:
            for state in all_states_iterator:
                consistent=True
                for constraint in C:
                    evaluation_result=constraint.evaluate_state(state,printing=printing,add_if_satisfies=add_if_satisfies)
                    if evaluation_result==False:
                        consistent=False
                if consistent:
                    if state.is_complete(reference_vars=V): #consistent and complete
                        solution_states.append(state)
        except Exception as e:
            raise ValueError(f"failed evaluating {constraint} on {state} with q_spaces {constraint.quantity_spaces}")

    return solution_states



def Node_Consistency(D,C,printing=False,add_if_satisfies=False):

    var_to_constraints_dict={}
    for c in C:
        for e in c.variables:
            if e not in var_to_constraints_dict.keys():
                var_to_constraints_dict[e] = []
            if c not in var_to_constraints_dict[e]:
                var_to_constraints_dict[e].append(c)

    #get unary constraints
    unary_constraints=[c for c in C if len(c.variables)==1]
    #get vars in those constraints
    unary_const_vars=list(set([c.variables[0] for c in unary_constraints]))

    new_D=copy.deepcopy(D)
    #get new domains of vars that participate in unary constraints
    for var in unary_const_vars:
        new_D[var]=[]
        for qv in D[var]:
            consistent=True
            for c in set(var_to_constraints_dict[var])&set(unary_constraints):
                evaluation_result=c.evaluate_tuple(qv, add_if_satisfies=add_if_satisfies, printing=printing)
                
                #print(var,c,qv,evaluation_result)
                if evaluation_result==False:
                    consistent=False
                
                if consistent:
                    new_D[var].append(qv)
    
    return new_D


def Revise_Domain(arc_to_constraints_dict,D,v1,v2,add_if_satisfies=False,printing=False):
    #depends on the order (v1,v2) and revises only v1's domain
    new_dom=copy.deepcopy(D[v1])
    revised=False
    for qv1 in D[v1]:
        for c in arc_to_constraints_dict[frozenset([v1,v2])]: #list of binary constraints where v1 participates (as first or 2nd var)
            if c.variables[0]==v1:
                evaluation_result=any([c.evaluate_tuple(qv1,qv2,add_if_satisfies=add_if_satisfies, printing=printing) for qv2 in D[v2]]) #any qv2 in v2's domain makes (qv1,qv2) satisfy c
            elif c.variables[1]==v1:
                evaluation_result=any([c.evaluate_tuple(qv2,qv1,add_if_satisfies=add_if_satisfies, printing=printing) for qv2 in D[v2]]) #any qv2 in v2's domain makes (qv2,qv1) satisfy c
            else:
                raise ValueError(f"variable {v1} is not the first, nor second variable in {c}")
            
            #print(qv1,D[v2],evaluation_result)
            if evaluation_result==False:
                revised=True
                new_dom.remove(qv1)
    return revised,new_dom
        

def Arc_Consistency(D,C,printing=False,add_if_satisfies=False):
    
    binary_constraints=[c for c in C if len(c.variables)==2]
    #get vars in those constraints
    binary_const_vars=set([v for c in binary_constraints for v in c.variables])

    #get arcs (sets of two vars that appear together in some binary constraint-oder doesn't matter)
    aux_list=[set(c.variables) for c in binary_constraints] #constraints can be duplicated
    unique_arcs_list=[s for s in set(frozenset(x) for x in aux_list)] #arcs must be frozensets to use as dictionary keys

    #map arc to constraints
    arc_to_constraints_dict={}
    for a in unique_arcs_list:
        if a not in arc_to_constraints_dict.keys():
            arc_to_constraints_dict[a]=[]
        for c in binary_constraints:
            if set(c.variables)==a: #order does not matter (can compare set with frozenset)
                arc_to_constraints_dict[a].append(c)

    #build hypergraph to get neighbors of each node
    # data = {i: c.variables for i,c in enumerate(C)}
    # H = hnx.Hypergraph(setsystem=data)

    #get new domains of vars that participate in binary constraints
    new_D=copy.deepcopy(D)
    
    #create queue of arcs
    arcs_queue=copy.deepcopy(unique_arcs_list)
    while len(arcs_queue)>0:
        #pop arc from queue
        arc=list(arcs_queue.pop(0))
        
        #if "vx" in arc:

        
        #revise domain of v1
        #try:
        revised,new_dom=Revise_Domain(arc_to_constraints_dict,new_D,arc[0],arc[1],add_if_satisfies=add_if_satisfies,printing=printing) #revise domain of v1 wr to v2
        #except:
        #    pass
        #    print(arc_to_constraints_dict,D,arc)
        #print(arc,revised,arcs_queue)

        #if revised, get other neighbors of vi and reinsert their arcs into the queue, update domain of vi
        if revised:
            new_arcs=[a for a in arc_to_constraints_dict.keys() if (arc[0] in a and arc[1] not in a)]
            arcs_queue.extend(new_arcs)
            #new_arcs=[frozenset([n,arc[0]]) for n in set(H.neighbors(arc[0]))&(binary_const_vars) if n!=arc[1]]
            new_D[arc[0]]=new_dom
            #print(arc[0],new_dom)

        #converse revise
        revised,new_dom=Revise_Domain(arc_to_constraints_dict,new_D,arc[1],arc[0],add_if_satisfies=add_if_satisfies,printing=printing) #revise domain of v2 wr to v1
        if revised:
            new_arcs=[a for a in arc_to_constraints_dict.keys() if (arc[1] in a and arc[0] not in a)]
            arcs_queue.extend(new_arcs)
            new_D[arc[1]]=new_dom

    return new_D



def  Cfilter(V,Q,C,Dbar=None,Domains=None,printing=False,add_if_satisfies=False,print_total_states=False):
    """
    V: list of strings of var names
    Q: dict of quantity spaces, one for each var
    C: list of constraints, each var from V must appear at least in one constraint
    Dbar: initial state (usually partially specified)
    Domains: pre-generated domains, list of qualitative values for each var in V, if not provided domains are generated from Dbar
    """

    assert (Dbar!=None) ^ (Domains!=None), "must provide either Dbar or domains, but cannot provide both"

    if Dbar!=None:
        Restricted_Domains=domain_restriction(Q,Dbar)
    else:
        Restricted_Domains=Domains

    new_D1=Node_Consistency(Restricted_Domains,C,printing=printing,add_if_satisfies=add_if_satisfies)
    new_D2=Arc_Consistency(new_D1,C,printing=printing,add_if_satisfies=add_if_satisfies)
    states=BF_Search(V,new_D2,C,printing=printing,add_if_satisfies=add_if_satisfies,print_total_states=print_total_states)
    return states



def get_next_landmark(current_landmark: landmark_value,q_space: quantity_space):
    try:
        next_index=q_space.landmarks.index(current_landmark)+1
        next_element=q_space.landmarks[next_index]
    except:
        next_element=None

    return next_element

def get_previous_landmark(current_landmark: landmark_value,q_space: quantity_space):
    try:
        previous_index=q_space.landmarks.index(current_landmark)-1
        if previous_index<0:
            previous_element=None
        else:
            previous_element=q_space.landmarks[previous_index]
    except:
        previous_element=None
    return previous_element


def Compute_Successor_from_Timepoint(var_qv: qualitative_value,var_q_space: quantity_space):

    if var_qv.qmag_type==landmark_value:
        if var_qv.qdir==Sign(0):
            var_successors_list = [var_qv]

            next_landmark=get_next_landmark(var_qv.qmag,var_q_space)
            if next_landmark!=None:
                var_successors_list.append(qualitative_value((var_qv.qmag,next_landmark),Sign(1))) #((l_j,l_j+1),inc)
            # else:
            #     var_successors_list.append(qualitative_value(var_qv.qmag,Sign(1))) #(l_j,inc), where l_j is an upper limit (typically inf) --not mentioned in the book
            previous_landmark=get_previous_landmark(var_qv.qmag,var_q_space)
            if previous_landmark!=None:
                var_successors_list.append(qualitative_value((previous_landmark,var_qv.qmag),Sign(-1))) #((l_j-1,l_j),dec)
            # else:
            #     var_successors_list.append(qualitative_value(var_qv.qmag,Sign(-1))) #(l_j-1,dec), where l_j-1 is a lower limit (typically -inf) --not mentioned in the book

        elif var_qv.qdir==Sign(1):
            var_successors_list=[]
            next_landmark=get_next_landmark(var_qv.qmag,var_q_space)
            if next_landmark!=None:
                var_successors_list.append(qualitative_value((var_qv.qmag,next_landmark),Sign(1))) #((l_j,l_j+1),inc)
            #else:
            #    var_successors_list.append(qualitative_value(var_qv.qmag,Sign(1))) #(l_j,inc), where l_j is an upper limit (typically inf) --not mentioned in the book

        elif var_qv.qdir==Sign(-1):
            var_successors_list=[]
            previous_landmark=get_previous_landmark(var_qv.qmag,var_q_space)
            if previous_landmark!=None:
                var_successors_list.append(qualitative_value((previous_landmark,var_qv.qmag),Sign(-1))) #((l_j-1,l_j),dec)
            # else:
            #     var_successors_list.append(qualitative_value(var_qv.qmag,Sign(-1))) #(l_j-1,dec), where l_j-1 is a lower limit (typically -inf) --not mentioned in the book
        else:
            raise ValueError("Must have defined sign value")


    elif var_qv.qmag_type==tuple: #interval between landmarks
        if var_qv.qdir==Sign(0):
            var_successors_list=[qualitative_value(var_qv.qmag,Sign(dir,derivative=True)) for dir in [-1,0,1]] #((l_j,l_j+1),dec), ((l_j,l_j+1),std), ((l_j,l_j+1),inc) --new landmark?
        elif var_qv.qdir==Sign(-1):
            var_successors_list=[var_qv] #((l_j,l_j+1),dec)
        elif var_qv.qdir==Sign(1):
            var_successors_list=[var_qv] #((l_j,l_j+1),inc)
        else:
            raise ValueError("Must have defined sign value")

    else:
        raise ValueError("Must provide a valid qmag value")
    return var_successors_list


def Compute_Successor_from_Timeinterval(var_qv: qualitative_value,var_q_space: quantity_space):
    if var_qv.qmag_type==landmark_value:
        if var_qv.qdir==Sign(0):
            var_successors_list=[var_qv]
        else:
            raise ValueError("Value cannot be at a landmark and have non-zero derivative when between timepoints.")
    
    elif var_qv.qmag_type==tuple: #interval between landmarks
        if var_qv.qdir==Sign(0):
            var_successors_list=[var_qv] #((l_j,l_j+1),std) *
            #raise ValueError("A quantity between two landrmarks cannot have zero derivative when between timepoints. This should instead be a new landmark value.")
        elif var_qv.qdir==Sign(-1):
            list_qmags=[var_qv.qmag[0],var_qv.qmag]
            list_qdirs=[Sign(dir,derivative=True) for dir in [-1,0]]
            var_successors_list=[qualitative_value(mag,dir) for mag,dir in itertools.product(list_qmags,list_qdirs)] #((l_j,l_j+1),dec), ((l_j,l_j+1),std) *, (l_j+1,inc), (l_j+1,std)
        elif var_qv.qdir==Sign(1):
            list_qmags=[var_qv.qmag[1],var_qv.qmag]
            list_qdirs=[Sign(dir,derivative=True) for dir in [1,0]]
            var_successors_list=[qualitative_value(mag,dir) for mag,dir in itertools.product(list_qmags,list_qdirs)] #((l_j,l_j+1),inc), ((l_j,l_j+1),std) *, (l_j+1,inc), (l_j+1,std)
        else:
            raise ValueError("Must have defined sign value")

    else:
        raise ValueError("Must provide a valid qmag value")

    return var_successors_list


def get_new_domains(current_parent_state,time_var,V,Q):
    #domain restriction from variable sucessors
    new_domains={}
    for var in set(V):#-set(time_var):

        var_qv=current_parent_state[var]
        var_qs=Q[var]

        if current_parent_state[time_var].qmag_type==landmark_value:
            #print("timepoint")
            try:
                var_successors_list=Compute_Successor_from_Timepoint(var_qv,var_qs)
            except Exception as e:
                print("Timepoint",var_qv,e)
                var_successors_list=[]
        else: #tuple
            #print("time interval")
            try:
                var_successors_list=Compute_Successor_from_Timeinterval(var_qv,var_qs)
            except Exception as e:
                print("Time Interval",var_qv,e)
                var_successors_list=[]
        #print(current_parent.name,var,var_successors_list)

        new_domains[var]=var_successors_list

    #print(current_parent.name,new_domains)

    return new_domains




def insert_new_landmark(current_value: qualitative_value,q_space:quantity_space,special_character=None,printing=False): 
    """
    current_value: qualitative value, includes landmarks before or after the new landmark after insertion
    Q: dictionary of all quantity spaces, with variables as keys
    Insert before 2nd landmark of current value. (Previously position: 0=before, 1=after)
    special_character: useful to distinguish values in different domains (e.g. afer transitions), usually an apostorphe
    """
    assert current_value.is_in_q_space(q_space)
    
    variable=q_space.variable
    if special_character==None:
        special_character=''

    try:
        new_landmark_sign=current_value.sign

        i=1
        new_landmark=landmark_value(variable+str(i)+special_character,new_landmark_sign)
        while variable+str(i)+special_character in q_space.names or new_landmark in q_space.landmarks:
            i+=1
            new_landmark=landmark_value(variable+str(i),new_landmark_sign)

        insert_index=q_space.landmarks.index(current_value.qmag[1]) #insert before 2nd landmark
        new_qspace=copy.deepcopy(q_space)
        new_qspace.landmarks.insert(insert_index,new_landmark)


        assert new_landmark in new_qspace.landmarks
        if new_qspace.compare_landmarks(new_landmark,new_qspace.maximum_limit)>=Sign(0):
            warnings.warn(f"inserted value {new_landmark} is greater than max limit. Consider setting a new max limit")
        if new_qspace.compare_landmarks(new_qspace.minimum_limit,new_landmark)>=Sign(0):
            warnings.warn(f"inserted value {new_landmark} is less than min limit. Consider setting a new min limit")
        #assert new_qspace.compare_landmarks(new_landmark,new_qspace.maximum_limit)>=Sign(0), "inserted value greater than max limit"
        #assert new_qspace.compare_landmarks(new_qspace.minimum_limit,new_landmark)>=Sign(0), "inserted value less than min limit"

        if printing:
            print(f"Old qs: {q_space}, New qs: {new_qspace}, Inserted Landmark:{new_landmark}")

    except Exception as e:
        raise ValueError(f"Error {e}\n when inserting landmark on {q_space} between {current_value}")

    return new_landmark,new_qspace

#inserting landmark outside limits?
#inserting before or after given landmark?


def get_ancestors_from_leaf(leaf_node,key="State"): #note: doesn't consider cycles identified in the tree 
    if key==None:
        ancestor_info_list=[n for n in leaf_node.ancestors]
        behavior_info_list=ancestor_info_list+[leaf_node]
    else:
        ancestor_info_list=[n.name[key] for n in leaf_node.ancestors]
        behavior_info_list=ancestor_info_list+[leaf_node.name[key]]
    return behavior_info_list


def get_behavior_from_leaf(leaf_node,key="State"): #note: doesn't consider cycles identified in the tree 
    if key==None:
        ancestor_info_list=[n for n in leaf_node.ancestors]
        behavior_info_list=ancestor_info_list+[leaf_node]
    else:
        ancestor_info_list=[n.name[key] for n in leaf_node.ancestors]
        behavior_info_list=ancestor_info_list+[leaf_node.name[key]]
    return behavior_info_list







################################### Main Function ###############################


def QSIM(V,Q,C,Trans_conditions,initial_conditions_state,time_var="t",cycle_match_criteria="weak",max_breadth=3000,max_depth=10):

    initial_system_state={"State":initial_conditions_state,"Q":Q,"C":C,"loc":(-1,0),"cycle_loc":None}
    states_list=[initial_system_state]

    root = Node(initial_system_state)
    current_parent_list=[root]

    initial_psr_solutions=Cfilter(V,Q,C,Dbar=initial_conditions_state)

    #possible initial states
    #states_list=[]
    current_parent_list=[]
    for i,state in enumerate(initial_psr_solutions):
        assert state.is_complete, "Incomplete state"
        ############################add corresponding values to initial states
        initial_C=copy.deepcopy(C)
        for c in initial_C:
            try:
                evaluation=c.evaluate_state(state,add_if_satisfies=True)
                assert evaluation, f"solution state didn't stasify constraint {c}"
            except Exception as e:
                raise ValueError(f"Error evaluating {c} with {state}\n and q_spaces {c.quantity_spaces}")
        system_state={"State":state,"Q":Q,"C":initial_C,"loc":(0,i),"cycle_loc":None}
        #states_list.append(system_state)
        current_parent_list.append(Node(system_state,parent=root))


    for lvl in range(max_depth-1):
        print(lvl)
        current_breadth = 0

        new_parents_list=[] 
        for current_parent in tqdm(current_parent_list): #agenda for the level
            #if "Q" in current_parent.name.keys():
            current_Q=copy.deepcopy(current_parent.name["Q"]) #only copy these since they will be modified
            current_C=copy.deepcopy(current_parent.name["C"])
            current_parent_state=current_parent.name["State"]
            current_parent_loc=current_parent.name["loc"]
            current_parent_cycle_loc=current_parent.name["cycle_loc"]
            #location=(lvl,current_breadth)
            assert current_parent_state.is_complete(V), "incomplete state with respect to variable set" #assume al states are complete, this could fail in some transitions


            if current_parent_state[time_var].is_finite and current_parent_cycle_loc==None: #if finite time and no cycle identified, calculate sucessors

                #transition_condition = current_parent_state["y"].sign<=Sign(0) and current_parent_state["y"].qdir<Sign(0) 
                #and current_parent_state[time_var].qmag_type==landmark_value #floor condition (simulation stops at floor)
                if any(Trans_conditions): 
                    print("transition occurs") 
                    filtered_solutions=[] #simulation stops at this point, and no successors are generated
                
                else: #no transition occurs, calculate sucessors normaly
                    
                    #domain restriction and psr solutions from variable sucessors
                    #print(current_parent_state,time_var,current_Q["y"])
                    
                    new_domains=get_new_domains(current_parent_state,time_var,V,current_Q)

                    #print(current_parent.name,new_domains)
                    #print("------",new_domains[time_var])
                    #print("------",[t_qv.sign_wr_value(current_parent_state[time_var],q_space=current_Q[time_var])==Sign(1) for t_qv in new_domains[time_var]])
                    
                    #for time, create new landmark and insert into qspace
                    #if not any([t_qv.sign_wr_value(current_parent_state[time_var],q_space=current_Q[time_var])==Sign(1) for t_qv in new_domains[time_var]]): #time inscreases
                    #print(current_parent_state[time_var])
                    #assume time is increasing
                    if current_parent_state[time_var].qmag_type==tuple: #insert new time landmark (only for successors of an interval)
                        current_time_qv=current_parent_state[time_var] #((ti,inf), inc)
                        #previous_time_landmark=current_time_qv.qmag[0] #ti
                        
                        #copy quantities for case when new landmark is inserted
                        new_domains2=copy.deepcopy(new_domains)
                        current_Q2=copy.deepcopy(current_Q)
                        current_C2=copy.deepcopy(current_C)
                        
                        #insert new landmark
                        new_time_landmark,new_tqs=insert_new_landmark(current_time_qv,current_Q[time_var],printing=False) #current qv is (t_i,inf), new landmark is inserted before inf
                        #update sucessors_list
                        new_domains2[time_var]=[qualitative_value(new_time_landmark,Sign(1))]#[qualitative_value((previous_time_landmark, new_time_landmark),Sign(1))]
                        current_Q2[time_var]=new_tqs 
                        
                        #update constraints
                        for c_index,c,j in [(c_index,c, j) for c_index,c in enumerate(current_C2) for j, var in enumerate(c.variables) if var == time_var]: #constraints that involve time var (t is as position j in C's vars)
                            #update time quantity space in the constraint
                            c_qs_list=[new_tqs if i==j else qs for i,qs in enumerate(c.quantity_spaces)] #use new time qspace
                            new_c=copy.deepcopy(c)
                            new_c.update_quantity_spaces(c_qs_list)
                            #update current_C
                            current_C2=[new_c if index==c_index else constraint for index,constraint in enumerate(current_C2)]
                                
                        psr_solutions2=Cfilter(V,current_Q2,current_C2,Domains=new_domains2) #solutions with inserted time landmark
                    
                    else:
                        psr_solutions2=[]
                    #else:
                    #    raise ValueError("Time is non-increasing")
                    
                    #print(V,new_domains,current_C)
                    psr_solutions=Cfilter(V,current_Q,current_C,Domains=new_domains) #normal solutions
                    
                    
                    ###############check global filters
                    filtered_solutions=[]
                    for sol_index, sol in enumerate(psr_solutions+psr_solutions2):
                        
                        if sol_index>=len(psr_solutions): #inherit Q and C from the ones generated above (named parent here, because new landmarks will be inserted afterwards)
                            parent_Q=current_Q2
                            parent_C=current_C2
                        else:
                            parent_Q=current_Q
                            parent_C=current_C

                        ###################add new landmarks
                        #critical point discovery
                        #non-differentiable condition? where derivative is infinite or function is discontinuous (only consider reasonable functions, ie differentiable)
                        #current representation doesn't distinguish when a derivative is infinity, unless part of a derivative constraint
                        
                        zero_derivative_vars=[var for var in set(V)-set(time_var) if sol[var].qdir==Sign(0) and sol[var].qmag_type==tuple and sol[time_var].qmag_type==landmark_value]
                        
                        infinite_value_vars=[var for var in set(V)-set(time_var) if sol[var].qmag_type==landmark_value and sol[var].is_finite==False and sol[time_var].qmag_type==landmark_value]
                        vars_with_infinite_derivative=[c.variables[0] for c in parent_C if (isinstance(c,Derivative) and c.variables[1] in infinite_value_vars and sol[c.variables[0]].qmag_type==tuple)] 
                        assert len(set(zero_derivative_vars)&set(vars_with_infinite_derivative))==0, "a variable has zero and infinite derivative"
                        assert time_var not in vars_with_infinite_derivative, "time variable has infinite derivative"

                        
                        new_Q=copy.deepcopy(parent_Q)
                        new_C=copy.deepcopy(parent_C)
                        for var in set(zero_derivative_vars)|set(vars_with_infinite_derivative):
                            new_landmark,new_qs=insert_new_landmark(sol[var],parent_Q[var],printing=False) #insert after first landmark
                            #update sol
                            sol[var]=qualitative_value(new_landmark,sol[var].qdir)
                            #update Q
                            new_Q[var]=new_qs
                            #update C (constraints involving var)
                            for c_index,c in [(c_index,c) for c_index,c in enumerate(new_C) if var in c.variables]: #constraints in which var participates
                                
                                #update var quantity space in the constraint
                                c_qs_list=[new_qs if qs.variable==var else qs for qs in c.quantity_spaces] #use new qspace (can be repeated)
                                
                                #update c
                                new_c=copy.deepcopy(c)
                                new_c.update_quantity_spaces(c_qs_list)
                                
                                #update new_C
                                new_C=[new_c if index==c_index else constraint for index,constraint in enumerate(new_C)]
                            
                        
                        ############################add corresponding values
                        for c in new_C:
                            try:
                                evaluation=c.evaluate_state(sol,add_if_satisfies=True)
                                assert evaluation, f"solution state didn't stasify constraint {c}"
                            except Exception as e:
                                raise ValueError(f"Error evaluating {c} with {sol}\n and q_spaces {c.quantity_spaces}")
                        
                        
                            
                        ##############################check state/local filters
                        filter1= current_parent_state.is_quiescent(time_var) #quiescent states have no sucessors (std in all qdirs,except time var)

                        if current_parent_state[time_var].qmag_type==tuple:#a timepoint state can have valid no-change successors. eg v1=(L1,std), v2=((L2,L3),inc), but a time interval cant
                            filter2= all([sol[var]==current_parent_state[var] for var in V if var!=time_var]) #no actual chage eg all inc (no-change filter on all vars, except time)
                        else:
                            filter2= False

                        #filter3 = sol["y"].sign<Sign(0) and sol["y"].qdir<Sign(0) #floor condition (simulation stops at floor)

                        filter4 = False #exists in the set of previous states (strong match) - can also consider equal intervals (weak match). landmark with interval?
                        match_criteria=cycle_match_criteria
                        for sys_state in get_ancestors_from_leaf(current_parent,key=None)[1:-2]:  #ignores partial info of initial state, current parent and parent's parent
                            condition1 = (sys_state.name["State"][time_var].qmag_type==landmark_value) and (sol[time_var].qmag_type==landmark_value) #must be at a timepoint
                            condition2 = sys_state.name["loc"]!=current_parent_loc #matches a non-parent state
                       
                            if match_criteria=="strong":
                                condition3 = all([(sol[var]==sys_state.name["State"][var]) and sol[var].qmag_type==landmark_value and sys_state.name["State"][var].qmag_type==landmark_value
                                                for var in V if var!=time_var]) and sys_state.name["State"][time_var].is_finite #doesnt condiser insertions (add: or between the same landmark values)
                            elif match_criteria=="weak":
                                condition3 = all([(sol[var]==sys_state.name["State"][var]) for var in V if var!=time_var]) and sys_state.name["State"][time_var].is_finite
                            else:
                                raise ValueError("match criteria must be weak or strong")

                            if condition1 and condition2 and condition3: #matches existing non-parent state, does not consider insertions
                                filter4=True 
                                current_parent.name["cycle_loc"]=sys_state.name["loc"]

                        filter5 = (sol[time_var].qmag_type==current_parent_state[time_var].qmag_type) #time successor must be of different type. 
                        #Removes cases where a time interval has a time interval sucessor where variables are at landmarks 
                        


                          #filter6: infinite values and divergences (p -> q is substituted by not p or q, negation is thus p and not q)
                        infinite_value_vars=[var for var in set(V)-set(time_var) if not sol[var].is_finite]
                        finite_value_vars=[var for var in set(V)-set(time_var) if sol[var].is_finite]

                        #vars_with_infinite_derivative=[c.variables[0] for c in parent_C if (isinstance(c,Derivative) and c.variables[1] in infinite_value_vars)] 
                        vars_with_finite_derivative=[c.variables[0] for c in parent_C if (isinstance(c,Derivative) and c.variables[1] in finite_value_vars)] 
                        vars_with_non_zero_derivative=[var for var in set(V)-set(time_var) if sol[var].qdir!=Sign(0)]
                        
                        #6a: t finite and f infinite, implies f' must infinite (for all non-time vars f) (only considering those related by derivative constraint), rule d in book
                        filter6a= sol[time_var].is_finite and len(set(infinite_value_vars)&set(vars_with_finite_derivative))>0
                        
                        #6b: t infinite and f finite, implies f' must be zero (for all non-time vars f), rule c in book
                        filter6b= (not sol[time_var].is_finite) and len(set(finite_value_vars)&set(vars_with_non_zero_derivative))>0

                        #6c: (some) f finite and f' not zero, implies t is finite, rule a in book
                        filter6c = any([sol[var].is_finite and sol[var].qdir!=Sign(0) for var in set(V)-set(time_var)]) and (not sol[time_var].is_finite)

                        #6d: (some) f infinite and f' finite, implies t is infinite, rule b in book (same a 6a)
                        filter6d= any([(not sol[var].is_finite) and (sol[var] in vars_with_finite_derivative) for var in set(V)-set(time_var)]) and (sol[time_var].is_finite)
                        #filter6c = any([(var in infinite_value_vars) and (var in vars_with_finite_derivative) for var in set(V)-set(time_var)]) and (sol[time_var].is_finite)

                       
                        
                        #aux_filter: require change of certain variables: x, vx
                        # if lvl>5:
                        #     aux_filter=any([sol[var]==current_parent_state[var] for var in ["x","vx"]])
                        # else:
                        #     aux_filter=False

                        #filter7: higher order derivaties

                        #behavior filters/global filters
                        #filter8: global energy constraint
                        #filter9: quantitative information 
                        #filter10: analytic function constraint
                        #filter11: non-intersection in phase-plane
                        
                        #print(filter1,filter2,filter4,filter5,filter6a,filter6b)
                        filter_conditions_list=[filter1,filter2,filter4,filter5,filter6a,filter6b,filter6c,filter6d]#,aux_filter]
                        if all([not f for f in filter_conditions_list]):
                            filtered_solutions.append((sol,new_Q,new_C))
                        #print(sol,filter_conditions_list)

                
                num_children = len(filtered_solutions)
                current_breadth+= num_children
                #print("curr_breadth",current_breadth)

                if current_breadth<=max_breadth:
                    new_children = num_children
                else:
                    new_children = num_children - (current_breadth - max_breadth)

                for i in range(new_children):
                    

                    node_loc=(lvl+1,current_breadth-num_children+i)

                    child_state=filtered_solutions[i][0] #qualitative state
                    child_qspaces=filtered_solutions[i][1] #new_Q
                    child_constraints=filtered_solutions[i][2] #new_C
                    assert child_state.is_complete(V), "child state is not complete"
                    
                    child_system_state={"State":child_state,"Q":child_qspaces, "C":child_constraints,"loc":node_loc,"cycle_loc":None} 
                    states_list.append(child_system_state)
                    child = Node(child_system_state, parent=current_parent)
                    new_parents_list.append(child)
        
        current_parent_list = new_parents_list
    
    return root